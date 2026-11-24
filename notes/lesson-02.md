# 第 02 课：工具系统

学习日期：

对应课程：[工具系统](../docs/02-tools.md)

## 本课阅读的文件

- [docs/02-tools.md](../docs/02-tools.md)
- [lessons/lesson-02/tools.py](../lessons/lesson-02/tools.py)
- [lessons/lesson-02/agent.py](../lessons/lesson-02/agent.py)

## 本课编辑的文件

- `practice/lesson-02/tools.py`
- `notes/lesson-02.md`

## 本课练习目标

- [x] 注册 `count_chars(text)` 工具，并验证它能通过统一执行器调用。
- [x] 写下关键函数、数据结构或设计关系。
- [x] 完成下面的理解、改动和验证记录。

## 验证参考

完成练习后，从 NamiAgent 根目录先验证相关测试，再运行整课测试：

```bash
uv run --directory practice/lesson-02 python -m pytest -q tests/test_tools.py
uv run --directory practice/lesson-02 python -m pytest -q
```

本课测试已经写好，直接复制实现文件或测试文件开头的命令运行。测试使用假模型、假渠道或临时文件，不需要加载真实 Key。

## 学习理解

一个 run 就是一次 loop

通过装饰器（类比注解）注册 tools

下面是装饰器语法：
装饰器 = 「在函数定义时自动对它做一层包装」的语法糖。
核心机制：@ 只是函数调用
@deco
def f():
    ...
完全等价于：
def f():
    ...
f = deco(f)      # ← @ 就是把下面的函数当参数传进去，再用返回值覆盖同名变量
就这么简单。@ 没有任何魔法，纯语法糖。


@tool("read_file", "读取文件", _params(path="文件路径"))
def read_file(path): ...
等价于：
def read_file(path): ...
read_file = tool("read_file", "读取文件", _params(...))(read_file)
\#            └────────── 先调用 tool ──────────┘ └── 再调用它返回的东西 ──┘


## 练习记录

- 实际修改或新增的文件：
- 修改原因：
- 这次想验证的行为：

## 实际验证结果

实际运行的命令或检查方式：

```text
uv run --directory practice/lesson-02 python -m pytest -q
```

实际结果：

## 尚待理解的问题

- 暂无

## 本课提交记录

提交说明：
提交编号（可选）：

## 后续继续做什么

-
