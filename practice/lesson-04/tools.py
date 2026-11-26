# 测试命令：在 NamiAgent 根目录复制执行，不需要真实 API Key。
# 完整测试：uv run --directory practice/lesson-04 python -m pytest -q
# 只测基础实现：uv run --directory practice/lesson-04 python -m pytest -q -k "not practice_exercise"


# 装饰器 = 「在函数定义时自动对它做一层包装」的语法糖。
# 核心机制：@ 只是函数调用
# @deco
# def f():
#     ...
# 完全等价于：
# def f():
#     ...
# f = deco(f)      # ← @ 就是把下面的函数当参数传进去，再用返回值覆盖同名变量
# 就这么简单。@ 没有任何魔法，纯语法糖。


# @tool("read_file", "读取文件", _params(path="文件路径"))
# def read_file(path): ...
# 等价于：
# def read_file(path): ...
# read_file = tool("read_file", "读取文件", _params(...))(read_file)
# #            └────────── 先调用 tool ──────────┘ └── 再调用它返回的东西 ──┘


import subprocess
import urllib.request

from permissions import WORKSPACE, resolve_in_workspace

MAX_OUTPUT = 8000   # 工具返回给模型的最大字符数
TOOLS = {}          # tools 注册表：name -> {"schema": ..., "func": ...}


# 装饰器
def tool(name, description, parameters):
    """装饰器：把一个函数注册为工具"""
    def decorator(func):
        TOOLS[name] = {
            "schema": {
                "type": "function", 
                "function": {
                    "name": name, 
                    "description": description, 
                    "parameters": parameters
                    }
                },
            "func": func,
        }
        return func
    return decorator
   
# 这个不是 Json Schema，只是给 ai 看的 Schema
# 只是 OpenAI function calling 协议
# JSON Schema 只是其中 parameters 那一段：type、properties、required
def get_schemas():
    """返回给模型看的全部工具说明书"""
    return [t["schema"] for t in TOOLS.values()]

# 这个才是 Json Schema
# type、properties、required
def _params(**props):
    """简写：所有参数都是必填的字符串"""
    return {"type": "object",
            "properties": {k: {"type": "string", "description": v} for k, v in props.items()},
            "required": list(props)}


# tools: ls
@tool("list_dir", "列出某个目录下的文件和子目录。", _params(path="目录路径，当前目录写 ."))
def list_dir(path="."):
    p = resolve_in_workspace(path)
    if p is None:
        return "[错误] 路径在工作区之外"
    return "\n".join(sorted(x.name + ("/" if x.is_dir() else "") for x in p.iterdir())) or "(空目录)"


# tools: read_file
@tool("read_file", "读取一个文本文件的内容。", _params(path="文件路径"))
def read_file(path):
    p = resolve_in_workspace(path)
    if p is None:
        return "[错误] 路径在工作区之外"
    return p.read_text(encoding="utf-8")


# tools: write_file
@tool("write_file", "把内容写入文件，已存在则覆盖，目录不存在会自动创建。",
      _params(path="文件路径", content="要写入的完整内容"))
def write_file(path, content):
    p = resolve_in_workspace(path)
    if p is None:
        return "[错误] 路径在工作区之外"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"已写入 {path}（{len(content)} 字符）"


# tools: run_shell
@tool("run_shell", "在当前目录执行一条 shell 命令，返回退出码、标准输出和错误输出。",
      _params(command="要执行的命令"))
def run_shell(command):
    p = subprocess.run(command, shell=True, cwd=WORKSPACE,
                           capture_output=True, text=True, timeout=30)
    return f"[exit {p.returncode}]\n{p.stdout}{p.stderr}"


# tools: fetch_url
@tool("fetch_url", "抓取一个网页或接口的文本内容。url 必须以 http 或 https 开头。",
      _params(url="完整的 URL"))
def fetch_url(url):
    req = urllib.request.Request(url, headers={"User-Agent": "nami-agent"})
    with urllib.request.urlopen(req, timeout=15) as response:
        return response.read().decode("utf-8", errors="replace")

# 小练习1 tools: count_chars
@tool("count_chars", "统计一个字符串中的字符数。", _params(text="要统计的字符串"))
def count_chars(text):
    return len(text)

# 小练习2 tools: edit_file(path, old, new)
@tool("edit_file", "在文件中替换指定字符串。", _params(path="文件路径", old="要替换的字符串", new="新的字符串"))
def edit_file(path, old, new):
    p = resolve_in_workspace(path)
    if p is None:
        return "[错误] 路径在工作区之外"
    text = p.read_text(encoding="utf-8")
    count = text.count(old)
    if count == 0:
        return f"Error: 文件 {path} 中没有包含字符串 {old}"
    if count > 1:
        return f"Error: 文件 {path} 中包含多个字符串 {old}"
    p.write_text(text.replace(old, new), encoding="utf-8")
    return f"已替换 {path} 中的 {count} 个字符串 {old} 为 {new}"


# 统一执行器：错误也是一种结果
def execute(name, args):
    """执行工具，永远返回字符串，永远不抛异常"""
    if name not in TOOLS:
        return f"Error: 不存在工具 '{name}'，可用工具：{', '.join(TOOLS)}"
    try:
        result = str(TOOLS[name]["func"](**args))
    except Exception as e:
        return f"Error: {type(e).__name__}: {e}"

    if len(result) > MAX_OUTPUT:
        result = result[:MAX_OUTPUT] + f"\n...（已截断，共 {len(result)} 字符）"
    return result

