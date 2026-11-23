# 测试来源：按课程接口补写的基础测试。
# 在 NamiAgent 根目录复制以下命令执行：
# uv run --directory practice/lesson-01 python -m pytest -q tests/test_agent.py
# 整课测试：uv run --directory practice/lesson-01 python -m pytest -q
# 仅基础测试：uv run --directory practice/lesson-01 python -m pytest -q -k "not practice_exercise"

import copy
import json
from types import SimpleNamespace

from openai.types.chat import ChatCompletionMessage

import agent


class FakeClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.seen = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def create(self, **kwargs):
        self.seen.append(copy.deepcopy(kwargs["messages"]))
        response = self.responses.pop(0)
        if isinstance(response, str):
            message = ChatCompletionMessage(role="assistant", content=response)
        else:
            message = ChatCompletionMessage(role="assistant", content=None, tool_calls=response)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def call(identifier, name, arguments):
    return {"id": identifier, "type": "function",
            "function": {"name": name, "arguments": json.dumps(arguments)}}


def test_file_roundtrip(tmp_path):
    path = tmp_path / "hello.txt"
    agent.write_file(str(path), "你好")
    assert agent.read_file(str(path)) == "你好"


def test_finishes_when_model_has_no_tool_calls(monkeypatch, capsys):
    client = FakeClient(["任务完成"])
    monkeypatch.setattr(agent, "client", client)
    agent.run("说一句你好")
    assert len(client.seen) == 1
    assert [m["role"] for m in client.seen[0]] == ["system", "user"]
    assert client.seen[0][1]["content"] == "说一句你好"
    assert "任务完成" in capsys.readouterr().out


def test_tool_result_is_sent_back_to_model(monkeypatch):
    client = FakeClient([[call("c1", "read_file", {"path": "a.txt"})], "已读完"])
    monkeypatch.setattr(agent, "client", client)
    monkeypatch.setitem(agent.TOOL_FUNCS, "read_file", lambda path: "文件内容")
    agent.run("读 a.txt")
    messages = client.seen[1]
    assert [m["role"] for m in messages] == ["system", "user", "assistant", "tool"]
    assert messages[-1]["tool_call_id"] == "c1"
    assert messages[-1]["content"] == "文件内容"


def test_tool_error_is_reported_to_model(monkeypatch):
    def failing_read(path):
        raise ValueError("演示错误")

    client = FakeClient([[call("c1", "read_file", {"path": "a.txt"})], "已收到错误"])
    monkeypatch.setattr(agent, "client", client)
    monkeypatch.setitem(agent.TOOL_FUNCS, "read_file", failing_read)
    agent.run("读 a.txt")
    assert client.seen[1][-1]["role"] == "tool"
    assert "ValueError" in client.seen[1][-1]["content"]


def test_step_limit_stops_the_loop(monkeypatch):
    client = FakeClient([[call("c1", "read_file", {"path": "a"})],
                         [call("c2", "read_file", {"path": "a"})]])
    monkeypatch.setattr(agent, "client", client)
    monkeypatch.setattr(agent, "MAX_STEPS", 2)
    monkeypatch.setitem(agent.TOOL_FUNCS, "read_file", lambda path: "x")
    agent.run("一直读")
    assert len(client.seen) == 2
