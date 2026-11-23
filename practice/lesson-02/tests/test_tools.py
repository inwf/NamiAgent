# 测试来源：按课程接口补写的基础测试。
# 在 NamiAgent 根目录复制以下命令执行：
# uv run --directory practice/lesson-02 python -m pytest -q tests/test_tools.py
# 整课测试：uv run --directory practice/lesson-02 python -m pytest -q
# 仅基础测试：uv run --directory practice/lesson-02 python -m pytest -q -k "not practice_exercise"

import tools


def parameters():
    return {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}


def test_core_tools_have_schemas():
    schemas = tools.get_schemas()
    assert all(schema["type"] == "function" for schema in schemas)
    names = {schema["function"]["name"] for schema in schemas}
    assert {"list_dir", "read_file", "write_file", "run_shell", "fetch_url"} <= names


def test_registration_and_execution(monkeypatch):
    monkeypatch.setattr(tools, "TOOLS", dict(tools.TOOLS))

    @tools.tool("test_count", "测试注册机制", parameters())
    def count(text):
        return len(text)

    names = {schema["function"]["name"] for schema in tools.get_schemas()}
    assert "test_count" in names
    assert tools.execute("test_count", {"text": "hello"}) == "5"
    assert tools.execute("test_count", {"text": "你好"}) == "2"
    assert tools.execute("test_count", {"text": ""}) == "0"


def test_unknown_tool_returns_error():
    assert tools.execute("missing_test_tool", {}).startswith("Error")


def test_tool_exceptions_become_results(monkeypatch):
    monkeypatch.setattr(tools, "TOOLS", dict(tools.TOOLS))

    @tools.tool("test_failure", "测试错误反馈", parameters())
    def fail(text):
        raise ValueError("演示错误")

    result = tools.execute("test_failure", {"text": "x"})
    assert result.startswith("Error") and "ValueError" in result


def test_long_output_is_truncated(monkeypatch):
    monkeypatch.setattr(tools, "TOOLS", dict(tools.TOOLS))
    monkeypatch.setattr(tools, "MAX_OUTPUT", 12)

    @tools.tool("test_long", "测试返回长度", parameters())
    def long_result(text):
        return "x" * 1000

    result = tools.execute("test_long", {"text": "x"})
    assert result.startswith("x" * 12) and len(result) < 1000


def test_file_tools_roundtrip(tmp_path):
    path = tmp_path / "nested" / "hello.txt"
    tools.write_file(str(path), "你好")
    assert tools.read_file(str(path)) == "你好"
    assert "hello.txt" in tools.list_dir(str(path.parent))


# 补充练习测试：字符统计工具
def test_practice_exercise_count_chars():
    names = {schema["function"]["name"] for schema in tools.get_schemas()}
    assert "count_chars" in names
    assert tools.execute("count_chars", {"text": "hello"}) == "5"
    assert tools.execute("count_chars", {"text": "你好"}) == "2"
    assert tools.execute("count_chars", {"text": ""}) == "0"
