# 18课笔记模板

每课打开对应笔记，阅读预填的文件清单，按任务学习后填写理解、练习、实际验证结果和提交记录。

课程顺序和具体练习见 [18课学习计划](../docs/learning-plan.md)。

| 课次 | 主题 | 笔记模板 |
|---|---|---|
| 01 | 最小循环 | [lesson-01.md](lesson-01.md) |
| 02 | 工具系统 | [lesson-02.md](lesson-02.md) |
| 03 | 权限 | [lesson-03.md](lesson-03.md) |
| 04 | 上下文管理 | [lesson-04.md](lesson-04.md) |
| 05 | Skills | [lesson-05.md](lesson-05.md) |
| 06 | 聊天渠道 | [lesson-06.md](lesson-06.md) |
| 07 | 定时任务 | [lesson-07.md](lesson-07.md) |
| 08 | MCP | [lesson-08.md](lesson-08.md) |
| 09 | 子 Agent | [lesson-09.md](lesson-09.md) |
| 10 | 计划 | [lesson-10.md](lesson-10.md) |
| 11 | 记忆 | [lesson-11.md](lesson-11.md) |
| 12 | Claude Code | [lesson-12.md](lesson-12.md) |
| 13 | Codex | [lesson-13.md](lesson-13.md) |
| 14 | Pi | [lesson-14.md](lesson-14.md) |
| 15 | Grok Bot | [lesson-15.md](lesson-15.md) |
| 16 | DeepSeek Harness | [lesson-16.md](lesson-16.md) |
| 17 | OpenClaw 与 Hermes | [lesson-17.md](lesson-17.md) |
| 18 | 总对照表 | [lesson-18.md](lesson-18.md) |

还可以使用：[通用模板](TEMPLATE.md)、[学习对照表模板](comparison.md)、[最后总结模板](final-summary.md)。

## practice 是什么

`practice` 的意思是“练习”，这里存放你自己修改的课程代码副本。例如第 02 课：

```text
NamiAgent/
├── lessons/lesson-02/tools.py   课程参考实现
├── practice/lesson-02/tools.py  你的练习代码
└── notes/lesson-02.md           本课笔记和验证记录
```

第 01～11 课的空白练习文件已经准备好，直接在 `practice/lesson-XX/` 中手写实现。启动自己的练习时运行 `practice/lesson-XX/agent.py`；网页端默认运行 `lessons/lesson-11` 的参考实现。

统一测试命令和完整课号列表见 [手写练习与测试命令](../practice/README.md)。
