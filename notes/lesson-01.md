# 第 01 课：最小 Agent 循环

日期：
对应课程：[最小循环](../docs/01-minimal-loop.md)

本课阅读的文件：

- [第 01 课文章](../docs/01-minimal-loop.md)
- [参考 agent.py](../lessons/lesson-01/agent.py)

本课编辑的文件：

- [练习 agent.py](../practice/lesson-01/agent.py)
- 本文件 `notes/lesson-01.md`

## 本课练习目标

- [x] 按顺序追踪 `run()` 中的模型调用、工具执行和结果回传。
- [x] 添加每轮消息数量、工具名称和结果长度的日志。
- [x] 运行一个简单任务，记录实际输出。
- [x] 填写下面的理解、改动和验证结果，再提交。

## 学习理解

- 用自己的话解释本课解决的问题：三个tools完成agent的mvp
- 核心函数和调用顺序：run()是agent的核心循环

## 练习记录

- 修改或新增的文件：
- 这次修改想验证什么：

## 验证结果

先运行假模型基础测试（不需要真实 Key）：

```bash
uv run --directory practice/lesson-01 python -m pytest -q
```

验证参考（完成练习后运行，需要 `.env` 中的真实 Key）：

```bash
mkdir -p generated/lesson-01
uv run --env-file .env python practice/lesson-01/agent.py "在 generated/lesson-01/hello.py 写一个打印 hello 的程序，并运行它"
```

下面填写自己实际执行的命令和结果。

运行命令：

```bash
uv run --env-file .env python practice/lesson-01/agent.py "读取 practice/lesson-01/agent.py，用三句话总结这个程序"

uv run --env-file .env python practice/lesson-01/agent.py "在 generated/lesson-01/hello.py 写一个打印 hello 的程序，并运行它"
```

模型可能会迷路，这也是一直在运行pwd的原因

实际结果：

## 还没想清楚的地方

- 无

## 本课提交记录

提交说明：
提交编号（可选）：

## 下一次继续做什么

- 第二课
