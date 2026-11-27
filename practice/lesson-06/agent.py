# 测试命令：在 NamiAgent 根目录复制执行，不需要真实 API Key。
# 完整测试：uv run --directory practice/lesson-06 python -m pytest -q
# 只测基础实现：uv run --directory practice/lesson-06 python -m pytest -q -k "not practice_exercise"


import json
import os

from openai import OpenAI

from context import (
    truncate_tool_result, 
    clear_old_tool_results, 
    compact,
    save_session,
    load_session
)
from permissions import PermissionManager
from tools import get_schemas, execute
import skills      # noqa: F401  导入即注册 load_skill

client = OpenAI(
    api_key=os.environ["API_KEY"],
    base_url=os.environ.get("BASE_URL", "https://api.deepseek.com"),
)
MODEL = os.environ.get("MODEL", "deepseek-flash")
MAX_STEPS = 20
SOFT_LIMIT = 16000   # 超过：清理旧工具结果
HARD_LIMIT = 24000   # 超过：摘要压缩
# 这两个是演示用的小值，方便你复现。实际按模型窗口的比例来设。

BASE_SYSTEM = ("你是一个能使用工具的助手，在用户的工作区内完成任务。"
               "必要时调用工具，完成后用简洁的语言汇报结果。")

# usage = {"prompt_tokens": 0}   # 上一次调用的真实 token 数（第 6 课会收进 Session）


# client 也从全局变量改成参数传入
# 这样测试时可以塞一个假的客户端进去，不用真的调模型。
def make_client():
    return OpenAI(
        api_key=os.environ["API_KEY"],
        base_url=os.environ.get("BASE_URL", "https://api.deepseek.com"),
    )

# 新的 system prompt
def build_system():
    # BASE_SYSTEM + 项目说明 + 技能说明
    return BASE_SYSTEM + skills.project_notes() + skills.skills_section()

# 按照 session 管理 messages
class Session:
    """一个会话 = 一份 messages + 一个权限管理器 + 上一次的 token 数"""

    # persist 是否持久化, 默认 True
    def __init__(self, name, ask = None, persist = True):
        self.name = name
        self.persist = persist
        saved = load_session(name) if persist else None
        self.messages = saved or [{"role": "system", "content": ""}]
        # 每次用最新的技能列表
        self.messages[0] = {"role": "system", "content": build_system()}
        self.perms = PermissionManager(ask = ask)
        self.prompt_tokens = 0 # 上一次调用的真实 token 数，是服务器返回的

    def save(self):
        if self.persist:
            save_session(self.name, self.messages)
        

# 解析参数、执行工具 perms 是 PermissionManager 的实例
def handle_call(call, perms):
    """解析参数 → 权限检查 → 执行。永远返回字符串。"""
    name = call.function.name
    try:
        # 模型实际想调用的参数
        args = json.loads(call.function.arguments or "{}")
    except json.JSONDecodeError:
        return "Error: 参数不是合法的 JSON"
    decision = perms.check(name, args) # perms 对象的对外入口
    if not decision.allowed:
        return f"[权限拒绝] {decision.reason}"   # 拒绝也要回传，让模型换条路
    return execute(name, args)

# 用户一次请求就算一个 loop
# 一个 loop 可能有多次 api 请求
def run(session, user_input, client, model=MODEL, log=print):
    messages = session.messages
    messages.append({"role": "user", "content": user_input})

    for _ in range(MAX_STEPS):
        # 用上一次调用的真实 token 数，决定这一轮要不要处理(压缩)
        if session.prompt_tokens > HARD_LIMIT: # 第 3 层：摘要压缩
            # [] 和 [:] 区别：「原来的那个列表对象」还是「换成一个新列表」
            messages[:] = compact(client, MODEL, messages)
        elif session.prompt_tokens > SOFT_LIMIT: # 第 2 层：清理旧工具结果
            clear_old_tool_results(messages)

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=get_schemas(),
        )
        session.prompt_tokens = response.usage.prompt_tokens if response.usage else 0
        msg = response.choices[0].message 
        # 模型回答的内容，例：
        # {
        #     "role": "assistant",
        #     "tool_calls": [
        #         {
        #         "id": "call_abc123",
        #         "function": {
        #             "arguments": "{\"path\": \"a.txt\"}",
        #             "name": "read_file"
        #         },
        #         "type": "function"
        #         }
        #     ]
        # }
        messages.append(msg.model_dump(exclude_none=True))

        # 没有工具调用 = 模型给出了最终回答
        if not msg.tool_calls:
            return msg.content or ""

        # 模型有工具调用（可能有多个工具调用）
        for call in msg.tool_calls:
            log(f"🔧 {call.function.name}({call.function.arguments[:80]})")
            result = handle_call(call, session.perms)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id, 
                    "content": truncate_tool_result(result),} # 第 1 层：截断工具结果
                    )
    return "（达到最大步数，已停止）"


def main():
    client = make_client()
    session = Session("default")
    while True:
        q = input("你> ").strip()
        if q in ("exit", "quit"):
            break
        print("\n" + run(session, q, client) + "\n")
        session.save()


if __name__ == "__main__":
    main()

