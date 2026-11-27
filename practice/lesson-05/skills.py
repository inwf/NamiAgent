# 测试命令：在 NamiAgent 根目录复制执行，不需要真实 API Key。
# 完整测试：uv run --directory practice/lesson-05 python -m pytest -q
# 只测基础实现：uv run --directory practice/lesson-05 python -m pytest -q -k "not practice_exercise"


# extras = sorted(p.name for p in path.parent.iterdir() if p.name != "SKILL.md")
# 列出这个技能目录里，除了 SKILL.md 之外的所有东西

from permissions import SKILLS_DIR, WORKSPACE
from tools import tool

SKILL_MARK = "[skill]"
MAX_NOTES_CHARS = 3000


# parse_skill 返回 meta, body
# skill 由两部分组成：元数据（frontmatter）和正文（text）
# 也可以看成 meta + body
# 模型就是根据 meta 来选择对应的 skill 的
def parse_skill(text):
    """拆出 frontmatter ( --- 之间的 key: value ) 和正文。"""
    lines = text.splitlines()
    # 没有 frontmatter，直接返回空：(元信息, 全文)
    if not lines or lines[0].strip() != "---":
        return {}, text.strip()
    meta = {}
    for i, line in enumerate(lines[1:], start=1): # 从下标 1 开始
        if line.strip() == "---":
            return meta, "\n".join(lines[i + 1:]).strip()
        key, sep, value = line.partition(":") # 固定分成三份
        if sep:
            meta[key.strip()] = value.strip()
    # 没有闭合的 ---，也当作没有 frontmatter
    return {}, text.strip()


# 从 skills_dir 目录里读取 skills 的元数据和目录
# discover 返回一个字典
# {
#     key -> value,
#     "git-summary" -> {
#         "description": "总结 Git 改动",
#         "path": "git-summary/SKILL.md"
#     },
#     "git-commit" -> {
#         "description": "提交 Git 改动",
#         "path": "git-commit/SKILL.md"
#     },
# }
def discover(skills_dir = None):
    skills_dir = skills_dir or SKILLS_DIR
    found = {}
    if not skills_dir.is_dir(): # 如果不是目录，直接返回空字典
        return found
    # glob 类比 find -name SKILL.md
    for f in sorted(skills_dir.glob("*/SKILL.md")):
        meta, _ = parse_skill(f.read_text(encoding = "utf-8"))
        # 如果没有 name，就用目录名
        name = meta.get("name") or f.parent.name
        # 如果没有 description，就跳过
        if not meta.get("description"):
            print(f"[skills] 跳过 {f}：缺少 description")
            continue
        # found 是一个字典: key -> {description, path}
        found[name] = {"description": meta["description"], "path": f}
    return found



# 给 ai 看的 skills 按需加载的 system prompt
# 就是要放进 system prompt 的文本
def skills_section(found = None):
    found = discover() if found is None else found
    if not found:
        return ""
    lines = ["", "## 可用技能",
             "下面只列出技能的名字和用途。当任务和某个技能的用途匹配时，"
             "先调用 load_skill 读取完整说明，再按说明执行。"]
    lines += [f"- {n}：{s['description']}" for n, s in found.items()]
    return "\n".join(lines)

# 就是 AGENTS.md
def project_notes():
    """AGENTS.md: 项目级说明, 每次都放进 system prompt。"""
    p = WORKSPACE / "AGENTS.md"
    if not p.is_file():
        return ""
    text = p.read_text(encoding="utf-8")[:MAX_NOTES_CHARS]
    return f"\n\n## 项目说明 (来自 AGENTS.md)\n{text}"


# 读取某个 skill 的完整说明
@tool(
    name="load_skill",
    description="读取一个技能的完整说明。任务和「可用技能」列表里某个技能的用途匹配时调用。",
    parameters={
        "type": "object",
        "properties": {"name": {"type": "string", "description": "技能名"}},
        "required": ["name"]
        },
) # parameters 可以手搓，也可以用之前 tools.py 里的 _params 函数
def load_skill(name):
    found = discover()
    if name not in found:
        return f"Error: 没有名为 {name!r} 的技能，可用：{', '.join(found) or '无'}"
    # 找到该技能目录
    path = found[name]["path"]
    _, body = parse_skill(path.read_text(encoding = "utf-8"))
    # 列出这个技能目录里，除了 SKILL.md 之外的所有东西 -> extras 是列表
    extras = sorted(p.name for p in path.parent.iterdir() if p.name != "SKILL.md")
    rel = path.parent.relative_to(WORKSPACE)
    note = f"\n\n( 技能目录 {rel}/ 下还有：{', '.join(extras)} )" if extras else ""
    return f"{SKILL_MARK} {name}\n{body}{note}"


