# 手写练习的测试命令

第 01～11 课的实现文件只有测试命令注释，代码由你手写。各课 `tests/` 中的测试已经准备好，你无需编写测试。

打开正在写的 `.py` 文件，复制开头注释中的命令，在 NamiAgent 根目录执行即可。

例如第 03 课：

```bash
uv run --directory practice/lesson-03 python -m pytest -q
```

只测权限文件：

```bash
uv run --directory practice/lesson-03 python -m pytest -q tests/test_permissions.py
```

先验证课文基础实现、暂不检查扩展练习：

```bash
uv run --directory practice/lesson-03 python -m pytest -q -k "not practice_exercise"
```

把课号换成 01～11 即可。测试使用假模型和临时目录，不需要真实 API Key。实现尚未填写时，测试会报告缺少函数或接口；写好实现后再运行。

第 03～11 课的基础测试复用原课程；第 01、02 课基础测试和计划中的扩展练习测试为补写内容，测试文件注释中已标注来源。

每课看什么、实现什么见 [18课学习计划](../docs/learning-plan.md)，结果记录在 [对应课程笔记](../notes/README.md)。
