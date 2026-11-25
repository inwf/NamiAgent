# 第 03 课：权限

学习日期：

对应课程：[权限](../docs/03-permissions.md)

## 本课阅读的文件

- [docs/03-permissions.md](../docs/03-permissions.md)
- [lessons/lesson-03/permissions.py](../lessons/lesson-03/permissions.py)
- [lessons/lesson-03/tools.py](../lessons/lesson-03/tools.py)
- [lessons/lesson-03/tests/test_permissions.py](../lessons/lesson-03/tests/test_permissions.py)

## 本课编辑的文件

- `practice/lesson-03/permissions.py`
- `notes/lesson-03.md`

## 本课练习目标

- [x] 新增对 `shutdown`、`reboot` 命令的拒绝规则。
- [x] 写下关键函数、数据结构或设计关系。
- [x] 完成下面的理解、改动和验证记录。

## 验证参考

完成练习后，从 NamiAgent 根目录先验证相关测试，再运行整课测试：

```bash
uv run --directory practice/lesson-03 python -m pytest -q tests/test_permissions.py
uv run --directory practice/lesson-03 python -m pytest -q
```

测试使用假模型、假渠道或临时文件，不需要加载真实 Key。

## 学习理解

- 本课解决的问题：
- 关键函数与数据结构：
- 用自己的话说明调用顺序或设计关系：

笔记：

有些命令就是不能放到 always 中 (always 连显示都不显示给用户)

未登记的工具默认走人工确认

确认界面展示真实参数，不展示模型的自述。 用户要看到的是将要执行的 rm notes/*.tmp，不是模型说的"我来清理一下临时文件"。

resolve_in_workspace 是整个路径安全的核心。 不能用字符串判断（比如检查路径里有没有 ..），因为绝对路径、~、软链接都能绕过。先 resolve() 得到真实路径，再判断它是不是在工作区之内。

黑名单不是边界。 SHELL_DENY_PATTERNS 只能拦住直白的危险写法。python -c "import shutil; shutil.rmtree('/')"、拼接字符串、base64 解码后再执行，都能绕过正则。它的作用是挡住模型"手滑"生成的明显错误，不是防御一个有意绕过的人。

## 练习记录

- 实际修改或新增的文件：
- 修改原因：
- 这次想验证的行为：

## 实际验证结果

实际运行的命令或检查方式：

```text
uv run --directory practice/lesson-03 python -m pytest -q
```

实际结果：

## 尚待理解的问题

- 无

## 本课提交记录

提交说明：
提交编号（可选）：

## 后续继续做什么

-
