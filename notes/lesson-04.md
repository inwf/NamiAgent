# 第 04 课：上下文管理

学习日期：

对应课程：[上下文管理](../docs/04-context.md)

## 本课阅读的文件

- [docs/04-context.md](../docs/04-context.md)
- [lessons/lesson-04/context.py](../lessons/lesson-04/context.py)
- [lessons/lesson-04/agent.py](../lessons/lesson-04/agent.py)
- [lessons/lesson-04/tests/test_context.py](../lessons/lesson-04/tests/test_context.py)

## 本课编辑的文件

- `practice/lesson-04/context.py`
- `notes/lesson-04.md`

## 本课练习目标

- [x] 长输出改为保留前 3/4、后 1/4，验证短输出和工具消息配对不受影响。
- [x] 写下关键函数、数据结构或设计关系。
- [x] 完成下面的理解、改动和验证记录。

## 验证参考

完成练习后，从 NamiAgent 根目录先验证相关测试，再运行整课测试：

```bash
uv run --directory practice/lesson-04 python -m pytest -q tests/test_context.py
uv run --directory practice/lesson-04 python -m pytest -q
```

测试使用假模型、假渠道或临时文件，不需要加载真实 Key。

## 学习理解

- 本课解决的问题：
- 关键函数与数据结构：
- 用自己的话说明调用顺序或设计关系：


不要一上来就做"摘要压缩"。按代价从低到高，分三层：截断 → 清理 → 摘要

三种常见压缩策略
- 截断工具结果
- 清理旧的工具结果
- 摘要压缩



## 清理旧的工具结果大概流程

[0] system     你是一个能使用工具的助手。
[1] user       读一下 a.txt 和 b.txt，然后告诉我哪个更长
[2] assistant  （调 read_file a.txt）
[3] tool       a.txt 的内容……（很长）        ← 下标 3
[4] assistant  （调 read_file b.txt）
[5] tool       b.txt 的内容……（很长）        ← 下标 5
[6] assistant  （调 count_chars）
[7] tool       120                          ← 下标 7

tool_idx = [3, 5, 7]
keep = 1
old = tool_idx[:-1] = [3, 5]     ← 这两个要清

清理后的 JSON
```json
[
  {
    "role": "system",
    "content": "你是一个能使用工具的助手。"
  },
  {
    "role": "user",
    "content": "读一下 a.txt 和 b.txt，然后告诉我哪个更长"
  },
  {
    "role": "assistant",
    "tool_calls": [
      {
        "id": "call_1",
        "type": "function",
        "function": {
          "name": "read_file",
          "arguments": "{\"path\": \"a.txt\"}"
        }
      }
    ]
  },
  {
    "role": "tool",
    "tool_call_id": "call_1",
    "content": "[旧工具结果已清理，如需要请重新调用工具]"
  },
  {
    "role": "assistant",
    "tool_calls": [
      {
        "id": "call_2",
        "type": "function",
        "function": {
          "name": "read_file",
          "arguments": "{\"path\": \"b.txt\"}"
        }
      }
    ]
  },
  {
    "role": "tool",
    "tool_call_id": "call_2",
    "content": "[旧工具结果已清理，如需要请重新调用工具]"
  },
  {
    "role": "assistant",
    "tool_calls": [
      {
        "id": "call_3",
        "type": "function",
        "function": {
          "name": "count_chars",
          "arguments": "{\"text\": \"...\"}"
        }
      }
    ]
  },
  {
    "role": "tool",
    "tool_call_id": "call_3",
    "content": "120"
  }
]
```

### 压缩摘要大概流程：
1. split_for_compact  → 把消息切成 old（旧的）和 recent（最近的）
2. render_for_summary(old)  → 把 old 转成纯文本（纯字符串）
3. 发给模型，让它压缩成 500 字摘要
4. 用「摘要 + recent」替换原来的全部历史


### 其他补充

为什么不是每一轮都清理旧工具结果？ 因为修改历史消息会改变请求的前缀。如果你用的服务商支持前缀缓存，频繁改动前面的内容会让缓存失效。所以只在 token 数逼近上限时才动手。

摘要是有损的。 摘要质量取决于你的 prompt 和模型，关键细节（比如某个具体的路径、参数）有可能丢。重要信息不要只靠摘要保存。

## 练习记录

- 实际修改或新增的文件：
- 修改原因：
- 这次想验证的行为：

## 实际验证结果

实际运行的命令或检查方式：

```text
# 学习后填写
```

实际结果：

## 尚待理解的问题

-

## 本课提交记录

提交说明：
提交编号（可选）：

## 后续继续做什么

-
