# 测试命令：在 NamiAgent 根目录复制执行，不需要真实 API Key。
# 完整测试：uv run --directory practice/lesson-04 python -m pytest -q
# 只测基础实现：uv run --directory practice/lesson-04 python -m pytest -q -k "not practice_exercise"


# [0] system     你是一个能使用工具的助手。
# [1] user       读一下 a.txt 和 b.txt，然后告诉我哪个更长
# [2] assistant  （调 read_file a.txt）
# [3] tool       a.txt 的内容……（很长）        ← 下标 3
# [4] assistant  （调 read_file b.txt）
# [5] tool       b.txt 的内容……（很长）        ← 下标 5
# [6] assistant  （调 count_chars）
# [7] tool       120                          ← 下标 7

# tool_idx = [3, 5, 7]
# keep = 1
# old = tool_idx[:-1] = [3, 5]     ← 这两个要清

# 清理后的 JSON

# [
#   {
#     "role": "system",
#     "content": "你是一个能使用工具的助手。"
#   },
#   {
#     "role": "user",
#     "content": "读一下 a.txt 和 b.txt，然后告诉我哪个更长"
#   },
#   {
#     "role": "assistant",
#     "tool_calls": [
#       {
#         "id": "call_1",
#         "type": "function",
#         "function": {
#           "name": "read_file",
#           "arguments": "{\"path\": \"a.txt\"}"
#         }
#       }
#     ]
#   },
#   {
#     "role": "tool",
#     "tool_call_id": "call_1",
#     "content": "[旧工具结果已清理，如需要请重新调用工具]"
#   },
#   {
#     "role": "assistant",
#     "tool_calls": [
#       {
#         "id": "call_2",
#         "type": "function",
#         "function": {
#           "name": "read_file",
#           "arguments": "{\"path\": \"b.txt\"}"
#         }
#       }
#     ]
#   },
#   {
#     "role": "tool",
#     "tool_call_id": "call_2",
#     "content": "[旧工具结果已清理，如需要请重新调用工具]"
#   },
#   {
#     "role": "assistant",
#     "tool_calls": [
#       {
#         "id": "call_3",
#         "type": "function",
#         "function": {
#           "name": "count_chars",
#           "arguments": "{\"text\": \"...\"}"
#         }
#       }
#     ]
#   },
#   {
#     "role": "tool",
#     "tool_call_id": "call_3",
#     "content": "120"
#   }
# ]


# 1. split_for_compact  → 把消息切成 old（旧的）和 recent（最近的）
# 2. render_for_summary(old)  → 把 old 转成纯文本（纯字符串）
# 3. 发给模型，让它压缩成 500 字摘要
# 4. 用「摘要 + recent」替换原来的全部历史


# 三种常用方案：截断 → 清理 → 摘要
import json
import os
from pathlib import Path

MAX_TOOL_CHARS = 4000           # 单个工具结果最多保留的字符数
KEEP_RECENT_TOOL_RESULTS = 3    # tools 结果清理时，保留最近几条工具结果
KEEP_LAST_TURNS = 2             # 摘要压缩时，原样保留最近几轮用户对话

# 程序自己的状态（会话记录、后面的定时任务）放在工作区之外，Agent 的文件工具碰不到
STATE_DIR = Path(os.environ.get("NAMI_STATE_DIR", Path.home() / ".nami-agent"))
SESSION_DIR = STATE_DIR / "sessions"


# 清理旧工具结果时，用的占位符
PLACEHOLDER = "[旧工具结果已清理，如需要请重新调用工具]"

SUMMARY_PROMPT = """你是对话摘要器。把下面这段 Agent 的历史对话压缩成摘要，要求：
1. 保留：用户的目标、已完成的步骤、关键结论、重要的文件路径和参数、尚未解决的问题
2. 丢弃：寒暄、重复内容、工具返回的大段原文
3. 用简洁的条目写，不要超过 500 字
只输出摘要本身。"""


# ---------- 第 1 层：截断工具结果 (tool_result) ----------
def truncate_tool_result(text, limit = MAX_TOOL_CHARS):
    if len(text) <= limit:
        return text
    # half = limit // 4
    # return f"{text[:3*half]}\n...[中间省略 {len(text) - limit} 字符]...\n{text[-half:]}"
    half = limit // 2
    return f"{text[:half]}\n...[中间省略 {len(text) - limit} 字符]...\n{text[-half:]}"


# ---------- 第 2 层：清理旧的工具结果（只改内容，不删消息） ----------
def clear_old_tool_results(messages, keep = KEEP_RECENT_TOOL_RESULTS):
    tool_idx = [i for i, m in enumerate(messages) if m["role"] == "tool"]
    # 清理旧的工具结果，如果 keep <= 0，清理所有工具结果（保留 0 条旧工具结果）
    old = tool_idx[:-keep] if keep > 0 else tool_idx
    for i in old:
        messages[i]["content"] = PLACEHOLDER


# ---------- 第 3 层：摘要压缩（推荐只在 user 消息处切） ----------
# 如果切在 assistant 的 tool_calls 和对应的 tool 消息之间
# 就会产生孤立的 tool 消息 -> tool_calls 和 tool_call_id 要一一对应！！！
def split_for_compact(messages, keep_turns = KEEP_LAST_TURNS):
    """返回： (要被压缩的旧消息, 原样保留的新消息)
    没有可压缩的内容返回 None
    约定 messages[0] 是 system。"""
    # 找到所有 user 消息的下标（只保留 m["role"] == "user"）
    user_idx = [i for i, m in enumerate(messages) if m["role"] == "user"]
#     messages = [
#       {'role':'system'},        # 0
#       {'role':'user'},          # 1  ← user
#       {'role':'assistant'},     # 2
#       {'role':'tool'},          # 3
#       {'role':'assistant'},     # 4
#       {'role':'tool'},          # 5
#       {'role':'assistant'},     # 6
#       {'role':'user'},          # 7  ← user
#       {'role':'assistant'},     # 8
#       {'role':'user'},          # 9  ← user
#   ]
#   user_idx = [1, 7, 9]
    if len(user_idx) <= keep_turns:
        return None
    cut = user_idx[-keep_turns] # 保留最后 keep_turns 个 user 消息的下标
    return messages[:cut], messages[cut:]


# render_for_summary(old)  → 把 old 转成纯文本（纯字符串）
def render_for_summary(msgs):
    lines = []
    for m in msgs:
        # tool_calls 是一个列表， 可能不止调用一个工具
        # assistant 且有 tool_calls
        if m["role"] == "assistant" and m.get("tool_calls"):
            calls = ", ".join(
                f'{c["function"]["name"]}({c["function"]["arguments"]})' 
                for c in m["tool_calls"]
                )
            if m.get("content"):
                lines.append(f'[assistant] {m["content"]}')
            lines.append(f"[assistant 调用工具] {calls}")
        else:
            # assistant 且没有 tool_calls 或者其他消息（user、tool等）
            lines.append(f'[{m["role"]}] {m.get("content") or ""}')
    return "\n".join(lines)


# compact(client, model, messages)  → 压缩消息：本质是一次 api 请求
def compact(client, model, messages):
    parts = split_for_compact(messages) # 没有可压缩的内容返回 None
    if parts is None:
        return messages
    # 旧消息, 原样保留的新消息
    old, recent = parts
    response = client.chat.completions.create(
        model = model, 
        messages = [
            {"role":"system", "content": SUMMARY_PROMPT},
            {"role":"user", "content": render_for_summary(old)}
        ]
    )
    summary = response.choices[0].message.content
    return [
        messages[0], # 保留 system 消息
        {"role": "user", "content": f"[以下是此前对话的摘要]\n{summary}"},
        {"role": "assistant", "content": "好的，我已了解之前的进展，继续。"},
        *recent, # 因为 recent 是一个列表，所以这里要拆开，要不然会把 recent 作为一个整体
    ]


# ---------- 会话持久化 ----------
def save_session(name, messages):
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    (SESSION_DIR / f"{name}.json").write_text(
        json.dumps(messages, ensure_ascii=False, indent=2), encoding="utf-8")

def load_session(name):
    path = SESSION_DIR / f"{name}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


