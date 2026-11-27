# 测试命令：在 NamiAgent 根目录复制执行，不需要真实 API Key。
# 完整测试：uv run --directory practice/lesson-06 python -m pytest -q
# 只测基础实现：uv run --directory practice/lesson-06 python -m pytest -q -k "not practice_exercise"


# 私聊时 chat_id 是用户 ID
# 群聊时 chat_id 是群 ID

import json
import urllib.request

MAX_LEN = 4000 # Telegram bot 单条发送上限 4096，留点余量

class Telegram:
    def __init__(self, token, timeout = 30):
        self.base = f"https://api.telegram.org/bot{token}/"
        self.timeout = timeout
        self.offset = 0
        self.pending = []   # 等待确认期间收到的"别的消息"，稍后处理

    # 调用 Telegram 官方 API
    def _call(self, method, **params):
        req = urllib.request.Request(
            self.base + method, 
            data = json.dumps(params).encode(),  # 默认 UTF-8 编码
            headers = {"Content-Type": "application/json"}
            )

        # 如果 self.timeout + 10 秒内没有响应，就抛出异常
        with urllib.request.urlopen(req, timeout = self.timeout + 10) as r:
            body = json.loads(r.read())
# 一个 body 示例
# {
#   "ok": true,
#   "result": [
#     {
#       "update_id": 100001,
#       "message": {
#         "message_id": 42,
#         "from": {
#           "id": 123456789,
#           "is_bot": false,
#           "first_name": "Hpy",
#           "username": "hpy"
#         },
#         "chat": {
#           "id": 123456789,
#           "first_name": "Hpy",
#           "type": "private"
#         },
#         "date": 1790000000,
#         "text": "帮我看看当前目录有什么文件"
#       }
#     },
#     {
#       "update_id": 100002,
#       "message": {
#         "message_id": 43,
#         "from": { "id": 987654321, "is_bot": false, "first_name": "Bob" },
#         "chat": { "id": -1001234567890, "title": "Dev Group", "type": "group" },
#         "date": 1790000010,
#         "text": "群里的一句话"
#       }
#     },
#     {
#       "update_id": 100003,
#       "edited_message": {
#         "message_id": 40,
#         "chat": { "id": 123456789, "type": "private" },
#         "text": "被编辑过的消息"
#       }
#     }
#   ]
# }
        if not body.get("ok"):
            raise RuntimeError(f"Telegram API 错误：{body}")
        return body["result"]


    # 获取用户发送的最新消息
    def fetch(self, timeout = None):
        """只拉新消息。返回 [(chat_id, user_id, text)]，只要私聊文本。"""
        updates = self._call(
            "getUpdates",
            offset = self.offset,
            # 有消息就立马返回，没有就挂起，最多等 self.timeout 秒
            timeout = self.timeout if timeout is None else timeout
        )
        out = []
        for u in updates:
            # 确认已收到，下次不再返回
            # 下次从这个 update_id 开始拉取
            self.offset = u["update_id"] + 1
            m = u.get("message")
            if m and "text" in m and m["chat"]["type"] == "private":
                out.append((m["chat"]["id"], m["from"]["id"], m["text"]))
        return out 


    # 先交出积压消息，再轮询获取最新消息
    def poll(self, timeout = None):
        """先交出积压的消息，没有积压再去拉新的。"""
        if self.pending:
            out, self.pending = self.pending, []
            return out
        return self.fetch(timeout)


    # bot 发消息给用户
    def send(self, chat_id, text):
        text = text or "(空回复)"
        # Agent 的回复可能更长，所以 send 按 4000 字切开发送。
        for i in range(0, len(text), MAX_LEN):
            self._call("sendMessage", chat_id = chat_id, text = text[i:i + MAX_LEN])

