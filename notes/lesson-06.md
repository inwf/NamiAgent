# 第 06 课：聊天渠道

学习日期：

对应课程：[聊天渠道](../docs/06-chat-apps.md)

## 本课阅读的文件

- [docs/06-chat-apps.md](../docs/06-chat-apps.md)
- [lessons/lesson-06/agent.py](../lessons/lesson-06/agent.py)
- [lessons/lesson-06/bot.py](../lessons/lesson-06/bot.py)
- [lessons/lesson-06/telegram.py](../lessons/lesson-06/telegram.py)
- [lessons/lesson-06/tests/fake.py](../lessons/lesson-06/tests/fake.py)

## 本课编辑的文件

- `practice/lesson-06/bot.py`
- `notes/lesson-06.md`

## 本课练习目标

- [x] 添加 `/help`，用假渠道验证它直接返回帮助信息。
- [x] 写下关键函数、数据结构或设计关系。
- [x] 完成下面的理解、改动和验证记录。

## 验证参考

完成练习后，从 NamiAgent 根目录先验证相关测试，再运行整课测试：

```bash
uv run --directory practice/lesson-06 python -m pytest -q tests/test_bot.py
uv run --directory practice/lesson-06 python -m pytest -q
```

测试使用假模型、假渠道或临时文件，不需要加载真实 Key。

## 学习理解

- 本课解决的问题：
- 关键函数与数据结构：
- 用自己的话说明调用顺序或设计关系：

## 练习记录

- 实际修改或新增的文件：
- 修改原因：
- 这次想验证的行为：

### 一个 body 示例

```json
{
  "ok": true,
  "result": [
    {
      "update_id": 100001,
      "message": {
        "message_id": 42,
        "from": {
          "id": 123456789,
          "is_bot": false,
          "first_name": "Hpy",
          "username": "hpy"
        },
        "chat": {
          "id": 123456789,
          "first_name": "Hpy",
          "type": "private"
        },
        "date": 1790000000,
        "text": "帮我看看当前目录有什么文件"
      }
    },
    {
      "update_id": 100002,
      "message": {
        "message_id": 43,
        "from": { "id": 987654321, "is_bot": false, "first_name": "Bob" },
        "chat": { "id": -1001234567890, "title": "Dev Group", "type": "group" },
        "date": 1790000010,
        "text": "群里的一句话"
      }
    },
    {
      "update_id": 100003,
      "edited_message": {
        "message_id": 40,
        "chat": { "id": 123456789, "type": "private" },
        "text": "被编辑过的消息"
      }
    }
  ]
}
```

### fetch 和 poll 要分开的原因

等待期间收到的其他消息先存起来。 在等你回 y/n 的这段时间里，你可能顺手发了别的消息，或者别的聊天来了消息。这些不能丢，也不能被误当成确认，所以放进 pending，等当前任务结束后由 poll() 交出来处理。这就是 fetch 和 poll 要分开的原因：等确认时只拉新消息，不碰积压的。


### 出错要回滚

终端版出错了，程序崩掉，你看得见。常驻版必须扛住单次失败继续运行，否则一次网络抖动就要你去服务器上重启。

但只"接住异常"还不够。设想模型返回了两个 tool_calls，执行完第一个，第二次调用模型时网络断了。此时 messages 的末尾停在一个不完整的状态，下一次请求很可能被 API 拒绝，这个聊天就"坏掉"了。

所以在运行前备份 messages，出错就整轮撤销。注意这只能撤销对话记录，已经写入的文件、已经执行的命令不会被撤销。回复里写的是"本轮已撤销"，但你心里要清楚撤销的范围。


## 实际验证结果

实际运行的命令或检查方式：

```text
uv run --directory practice/lesson-06 python -m pytest -q
```

实际结果：

## 尚待理解的问题

-

## 本课提交记录

提交说明：
提交编号（可选）：

## 后续继续做什么

-
