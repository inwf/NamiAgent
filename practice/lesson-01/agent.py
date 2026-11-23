# 测试命令：在 NamiAgent 根目录复制执行，不需要真实 API Key。
# 完整测试：uv run --directory practice/lesson-01 python -m pytest -q
# 只测基础实现：uv run --directory practice/lesson-01 python -m pytest -q -k "not practice_exercise"
# uv run --env-file .env python practice/lesson-01/agent.py "读取 practice/lesson-01/agent.py，用三句话总结这个程序"


import json
import os
import subprocess # 执行 shell 命令
import sys

from openai import OpenAI

client = OpenAI(
    api_key=os.environ["API_KEY"],
    base_url=os.environ.get("BASE_URL", "https://api.deepseek.com"),
)
MODEL = os.environ.get("MODEL", "deepseek-flash")
MAX_STEPS = 20  # 防止死循环：Agent 最多转 20 圈

SYSTEM = (
    "你是一个能操作本地文件和命令行的编程助手。"
    "需要时调用工具，完成任务后直接用文字总结，不要再调用工具。"
)


# 三个工具：read_file、write_file、run_shell

def read_file(path: str) -> str: # 返回 str
# with ...: = 「用完后自动帮我关闭文件」，不用手动写 f.close()，即使中途出错也会关
    with open(path, encoding="utf-8") as f:
        return f.read()

# 把 content 写入文件 path
def write_file(path: str, content: str) -> str:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"已写入 {path}（{len(content)} 字符）"

def run_shell(command: str) -> str:
    # 第 1 课先用最朴素的权限控制：每条命令人工确认
    if input(f"\n[需要确认] 执行命令：{command}\n允许？(y/n) ").strip().lower() != "y":
        return "用户拒绝执行该命令"

    # try:
    #     # 可能出错的代码
    # except 某种错误:
    #     # 真出这种错了，就执行这里
    try:
        p = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        return "命令超时（60 秒）"
    return (p.stdout + p.stderr)[-4000:] or "(无输出)"  # 截断，避免撑爆上下文


TOOL_FUNCS = {"read_file": read_file, "write_file": write_file, "run_shell": run_shell}


# 工具说明：告诉模型有哪些工具、参数是什么 
def _tool(name, desc, props):
# props：参数列表，是一个 dict
# 形如 {"path": "文件路径", "content": "内容"}
# key 是参数名，value 是这个参数的说明
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": desc,
            "parameters": {
                "type": "object", # 参数整体是一个对象
                # 字典推导式
                "properties": {k: {"type": "string", "description": v} for k, v in props.items()},
                # 所以输入：
                # props = {"path": "文件路径", "content": "要写入的内容"}
                # 这一行产出：
                # {
                #     "path":    {"type": "string", "description": "文件路径"},
                #     "content": {"type": "string", "description": "要写入的内容"},
                # }
                "required": list(props), # 取出字典所有 key, 然后转成 list 列表
            },
        },
    }


# 系统工具列表
TOOLS = [
    _tool("read_file", "读取文件内容", {"path": "文件路径"}),
    _tool("write_file", "写入文件内容", {"path": "文件路径", "content": "要写入的内容"}),
    _tool("run_shell", "执行 shell 命令", {"command": "要执行的命令"}),
]


# 核心：Agent 循环

def run(task: str) -> None:
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": task},
    ]
    for step in range(1, MAX_STEPS + 1):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
        )
        msg = response.choices[0].message
        # message 数组就是模型的上下文，不断 append 就行
        # model_dump：dict、exclude_none=True 去掉 None 值
        messages.append(msg.model_dump(exclude_none=True))

        # 模型如果没有要调用的工具 = 他认为任务已结束 -> 循环结束
        if not msg.tool_calls: # not False = True，空 = False
            print(f"\n[完成，共 {step} 步]\n{msg.content}")
            return

        # 模型进行工具调用，并把结果作为 tool 消息 append 到上下文
        for call in msg.tool_calls:
            name = call.function.name
            print(f"[第 {step} 步] {name}({call.function.arguments[:80]})")
            try:
                args = json.loads(call.function.arguments)
                # **args 的意思是：把字典 args 拆成一个个「参数名=值」传给函数
                # args = {"path": "a.txt"}
                # TOOL_FUNCS[name](**args)     # 等价于 read_file(path="a.txt")
                result = TOOL_FUNCS[name](**args)
            except Exception as e: # 工具出错也要告诉模型，让它自己修正
                result = f"工具执行出错：{type(e).__name__}: {e}"
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

    print(f"\n[达到 {MAX_STEPS} 步上限，已停止]")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit('用法：python agent.py "你的任务"')
    run(sys.argv[1])
    

