# 测试命令：在 NamiAgent 根目录复制执行，不需要真实 API Key。
# 完整测试：uv run --directory practice/lesson-05 python -m pytest -q
# 只测基础实现：uv run --directory practice/lesson-05 python -m pytest -q -k "not practice_exercise"


from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from textwrap import indent

# Agent 的工作目录，默认是启动时的目录
WORKSPACE = Path(os.environ.get("NAMI_WORKSPACE",os.getcwd())).resolve()
SKILLS_DIR = WORKSPACE / "skills"


# 风险等级
class Risk(Enum):
    SAFE = "safe"         # 只读：直接放行
    CONFIRM = "confirm"   # 人工确认
    DENY = "deny"         # 拒绝


# 工具风险登记表：没登记的工具一律按 CONFIRM 人工确认处理
TOOL_RISK = {
    "list_dir": Risk.SAFE,
    "read_file": Risk.SAFE,
    "load_skill": Risk.SAFE,     # 只读，直接放行
    "write_file": Risk.CONFIRM,
    "run_shell": Risk.CONFIRM,
    "fetch_url": Risk.CONFIRM,
}

# 显示“本次会话一直允许”（always）的工具 注：run_shell 不在里面
# 「有资格被记住」——它是「哪些工具可以显示 [a] 选项」的白名单。
REMEMBERABLE = {"write_file"}

# 明显灾难性命令：拒绝执行 （只是一层保护，实际上仍然可以绕过）
SHELL_DENY_PATTERNS = [
    r"\brm\s+(-[a-zA-Z]*[rf][a-zA-Z]*\s+)+(/|~|\*)",  # rm -rf / ~ *
    r"\bsudo\b",
    r"\bmkfs\b",
    r"\bdd\s+if=",
    r":\(\)\s*\{",                                    # fork bomb
    r"(curl|wget)\b.*\|\s*(sh|bash)\b",               # curl ... | sh
    r">\s*/dev/sd", 
    r"\bshutdown\b",
    r"\breboot\b",
]


# 把 path 展开为绝对路径，然后判断在不在工作区内，不在就返回 None
def resolve_in_workspace(path_str: str) -> Path | None:
    """
    把路径解析为绝对路径；不在工作区内就返回 None
    resolve() 会展开 .. 和符号链接，所以 ../../etc/passwd 和指向外部的软链接都会被识别
    """
    p = Path(path_str).expanduser()  # 展开 ~ 符号
    if not p.is_absolute(): # 不是绝对路径 -> 是相对路径
        # / 是 Path 的重载运算符，表示「拼路径」
        p = WORKSPACE / p
    p = p.resolve()  # 展开 .. 和符号链接
    # 判断「p 是不是在 WORKSPACE 内」
    return p if p.is_relative_to(WORKSPACE) else None


# 决策结果
@dataclass
class Decision:
    allowed: bool
    reason: str = ""


# 显示模型将要执行的真实内容：不能是自述，因为自述可能会被误导
# === run_shell ===
#   $ ls -la

# === read_file ===
#   {'path': 'a.txt'}

# === write_file ===
#   路径：hello.py
#     print(1)
def render_call(name: str, args: dict, max_chars: int = 400) -> str:
    """确认界面：展示将要执行的真实内容，而不是模型的自述。"""
    if name == "run_shell":
        return f"  $ {args.get('command', '')}"
    if name == "write_file":
        content = args.get("content", "")
        preview = content[:max_chars]
        if len(content) > max_chars:
            preview += f"\n...（已截断，共 {len(content)} 字符）"
        return f"  路径：{args.get('path')}\n" + indent(preview, "    ")
    return f"  {args}"


# 权限管理器
class PermissionManager:
    # ask 缺省，默认为 None
    def __init__(self, ask=None):
        self.always_allowed: set[str] = set()
        # ask 可注入：ask(name, args) -> ("y" | "n" | "a", 拒绝原因)
        # 第 3 课用它方便测试，第 6、7 课会换成聊天确认和无人值守的预授权
        self.ask = ask or self._ask_terminal

    # ---------- 对外入口 ----------
    def check(self, name: str, args:dict) -> Decision:
        # 第 1 关： 明显灾难性命令 或 路径不在工作区内的所有命令
        reason = self._hard_limits(name, args)
        if reason:
            return Decision(False, reason)

        # 第 2 关： 根据风险等级分流 -> SAFE 放行 / DENY 拒绝 / CONFIRM 去第 3 关
        # 查字典 TOOL_RISK，没有就按 CONFIRM 处理
        # TOOL_RISK[name] 查不到会抛 KeyError，.get() 查不到会返回默认值
        risk = TOOL_RISK.get(name, Risk.CONFIRM)
        if risk is Risk.DENY:
            return Decision(False,  f"工具 {name} 被策略禁用。")
        if risk is Risk.SAFE or name in self.always_allowed:
            return Decision(True)

        # 第 3 关： 人工确认
        return self._confirm(name, args)


    # ---------- 内部实现 ----------
    # 第 1 关
    def _hard_limits(self, name: str, args: dict) -> str | None:
        if name in ("read_file", "write_file", "list_dir"):
            path = args.get("path", ".")
            p = resolve_in_workspace(path)
            if p is None:
                return f"路径 {path!r} 在工作区 {WORKSPACE} 之外，禁止访问"
            if name == "write_file" and p.is_relative_to(SKILLS_DIR):
                        return "技能目录是只读的, Agent 不能修改自己的技能。"
        if name == "run_shell":
            cmd = args.get("command", "")
            for pat in SHELL_DENY_PATTERNS: # 明显灾难性命令
                if re.search(pat, cmd): # 在 cmd 中找符合正则表达式 pat 的内容
                    # 找到返回 Match（真），找不到返回 None（假）
                    return f"命令命中危险模式，明显是灾难性命令，已被策略拦截：{cmd!r}"
        return None


    # 第 3 关
    def _confirm(self, name: str, args: dict) -> Decision:
        # 用户选择本次会话始终允许 always_allowed
        answer, note = self.ask(name, args)
        # ① 用户按 a，且这个工具有资格被记住 → 记住 + 放行
        if answer == "a" and name in REMEMBERABLE:
            self.always_allowed.add(name)
            return Decision(True)
        # ② 按 y 或 a → 放行（a 但没资格记住时，就当一次性的 y）
        if answer in ("y", "a"):
            return Decision(True)
        # ③ 其余（n）→ 拒绝，并把原因喂回给模型
        msg = "用户拒绝了这次操作。"
        if note:
            msg += f"原因: {note}"
        msg += "不要重试同一操作；请换一种方式，或向用户说明你想做什么、为什么。"
        return Decision(False, msg)


    # 在终端弹出一个确认框，等用户输入 y / n / a，然后返回答案。
    @staticmethod # 静态方法，就看成普通函数就好，不用看成类的成员函数
    def _ask_terminal(name: str, args: dict):
        if not sys.stdin.isatty():
            # 非交互环境（管道、脚本）没有人可以确认，默认拒绝
            return "n", "当前是非交互环境，无法确认"
        print(f"\n   Agent 想执行：{name}")
        print(render_call(name, args))
        options = "[y]允许 / [n]拒绝" + (" / [a]本次会话一直允许" if name in REMEMBERABLE else "")
        while True:
            ans = input(f"{options} > ").strip().lower()
            if ans in ("y", "n") or (ans == "a" and name in REMEMBERABLE):
                break
        note = input("拒绝原因（可选，回车跳过）> ").strip() if ans == "n" else ""
        return ans, note