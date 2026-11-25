# 测试命令：在 NamiAgent 根目录复制执行，不需要真实 API Key。
# 完整测试：uv run --directory practice/lesson-03 python -m pytest -q
# 只测基础实现：uv run --directory practice/lesson-03 python -m pytest -q -k "not practice_exercise"


import json
import os

from openai import OpenAI

from permissions import PermissionManager
from tools import get_schemas, execute

client = OpenAI(
    api_key=os.environ["API_KEY"],
    base_url=os.environ.get("BASE_URL", "https://api.deepseek.com"),
)
MODEL = os.environ.get("MODEL", "deepseek-flash")
MAX_STEPS = 20

SYSTEM = ("你是一个能使用工具的助手，在用户当前目录下完成任务。"
          "必要时调用工具，完成后用简洁的语言汇报结果。")


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
def run(user_input, messages, perms):
    messages.append({"role": "user", "content": user_input})

    for _ in range(MAX_STEPS):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=get_schemas(),
        )
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
            print(f"🔧 {call.function.name}({call.function.arguments[:80]})")
            result = handle_call(call, perms)
            messages.append({"role": "tool","tool_call_id": call.id, "content": result})
    return "（达到最大步数，已停止）"


if __name__ == "__main__":
    messages = [{"role": "system", "content": SYSTEM}]
    perms = PermissionManager() # 单例：整个会话共用，"一直允许"记在它身上

    while True:
        q = input("你> ").strip()
        if q in ("exit", "quit"):
            break
        print("\n" + run(q, messages, perms) + "\n")








