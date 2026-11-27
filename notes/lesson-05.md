# 第 05 课：Skills

学习日期：

对应课程：[Skills](../docs/05-skills.md)

## 本课阅读的文件

- [docs/05-skills.md](../docs/05-skills.md)
- [lessons/lesson-05/skills.py](../lessons/lesson-05/skills.py)
- [lessons/lesson-05/tests/test_skills.py](../lessons/lesson-05/tests/test_skills.py)

## 本课编辑的文件

- `practice/lesson-05/skills/git-summary/SKILL.md`
- `notes/lesson-05.md`

## 本课练习目标

- [x] 写一个介绍如何总结 Git 改动的技能，并验证元数据能被解析。
- [x] 写下关键函数、数据结构或设计关系。
- [x] 完成下面的理解、改动和验证记录。

## 验证参考

完成练习后，从 NamiAgent 根目录先验证相关测试，再运行整课测试：

```bash
uv run --directory practice/lesson-05 python -m pytest -q tests/test_skills.py
uv run --directory practice/lesson-05 python -m pytest -q
```

测试使用假模型、假渠道或临时文件，不需要加载真实 Key。

## 学习理解

- 本课解决的问题：
- 关键函数与数据结构：
- 用自己的话说明调用顺序或设计关系：

parse_skill 返回 meta, body
skill 由两部分组成：元数据（frontmatter）和正文（text）
也可以看成 meta + body
模型就是根据 meta 来选择对应的 skill 的

.glob("*/SKILL.md")
表示在 skills_dir 目录下，查找符合 */SKILL.md 模式的文件（类比 find -name "SKILL.md"）

discover 返回一个字典

```py
{
    key -> value,
    "git-summary" -> {
        "description": "总结 Git 改动",
        "path": "git-summary/SKILL.md"
    },
    "git-commit" -> {
        "description": "提交 Git 改动",
        "path": "git-commit/SKILL.md"
    },
}
```

### 上下文管理

技能内容不参与"清理旧工具结果(tool_result)"
技能说明也是工具结果，如果被清理掉，模型就会在任务进行到一半时"忘记规矩"

按需加载的价值一半在于"该加载时加载"，另一半在于"不该加载时不加载"。

### Agent 能不能自己写技能？

两种选择都说得通，代价不同：

| | 技能只读（本课） | Agent 自己写技能（Hermes） |
|---|---|---|
| 好处 | 技能都是你读过的，注入写不进去 | 越用越顺手，不用你手写规则 |
| 代价 | 规则全靠你手写、手动维护 | 一次被注入的内容可能固化成技能，之后每次都触发 |
| 适合 | 能执行命令、动文件的 Agent | 对自动沉淀要求高、能接受定期审查的场景 |

如果想要后者，比较稳妥的折中是：让 Agent 把新技能写到一个"待审核"目录，你看过之后再挪进 `skills/`。

## 练习记录

- 实际修改或新增的文件：
- 修改原因：
- 这次想验证的行为：

## 实际验证结果

实际运行的命令或检查方式：

```text
uv run --directory practice/lesson-05 python -m pytest -q
```

实际结果：

## 尚待理解的问题

-

## 本课提交记录

提交说明：
提交编号（可选）：

## 后续继续做什么

-
