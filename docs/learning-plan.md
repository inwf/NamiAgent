# NamiAgent 18课学习计划

按 18 课顺序学习，每课依次完成：阅读文章和源码 → 修改练习文件 → 验证结果 → 记录笔记与提交。每课可以按自己的进度分多次完成。

先用网页端体验一次完整流程，然后从第 01 课开始。网页端默认使用第 11 课；第 12～18 课是产品拆解文章，没有新的代码目录。

本计划的运行命令统一使用 uv 和项目根目录的 `.env`。课程文章中的安装、环境变量和启动示例，可以用这里已经配置好的命令替换。

## 文件放在哪里

- 阅读文章：`docs/`。
- 阅读参考代码：`lessons/lesson-01/` 到 `lessons/lesson-11/`。
- 编辑练习副本：`practice/lesson-01/` 到 `practice/lesson-11/`。
- 每课编辑笔记：`notes/lesson-01.md` 到 `notes/lesson-18.md`，已准备好 [18课笔记模板索引](../notes/README.md)。

`practice` 的意思是“练习”。例如第 02 课，阅读 `lessons/lesson-02/tools.py`，编辑 `practice/lesson-02/tools.py`，在 `notes/lesson-02.md` 记录理解和验证结果。启动自己的练习时运行 `practice/lesson-XX/agent.py`；网页端默认运行 `lessons/lesson-11`。

第 01～11 课的实现文件只有测试命令注释，供你对照资料手写；测试文件已完整准备好，无需你编写测试。先完成文章中的基础实现并通过基础测试，再做本课练习目标中的扩展。进入下一课时，可以整理上一课自己完成的相关实现，再编写新增模块。测试使用课程接口，因此函数名、参数和返回格式应与本课目标一致。

18课的笔记模板、学习对照表和最后总结模板已经准备好，直接打开对应的 `notes/lesson-XX.md` 填写。练习目录也已准备完成，直接在实现文件的测试命令注释下面编写代码即可，`tests/` 中的测试已写好。

源码写好后，复制文件开头注释中的命令，在项目根目录执行。例如第 03 课：

```bash
uv run --directory practice/lesson-03 python -m pytest -q
```

完整命令表和按文件测试的用法见 [手写练习与测试命令](../practice/README.md)。

第 12～18 课直接填写对应的笔记模板，并逐步完善 `notes/comparison.md`；第 18 课还需填写 `notes/final-summary.md`。

以下表格中，第 01～11 课的代码名都省略了目录前缀：**阅读列在 `lessons/lesson-XX/`，编辑列在 `practice/lesson-XX/`。** 每一行都要另外填写本课的 `notes/lesson-XX.md`。

## 18课阅读与练习总览

| 课次 | 先读文章，再读这些参考文件 | 实际编辑的练习文件 | 本课练习目标 |
|---|---|---|---|
| 01 | [最小循环](01-minimal-loop.md)；[agent.py](../lessons/lesson-01/agent.py) | `agent.py` | 在 `run()` 中打印每轮消息数量、工具名称和结果长度。 |
| 02 | [工具系统](02-tools.md)；[tools.py](../lessons/lesson-02/tools.py)、[agent.py](../lessons/lesson-02/agent.py) | `tools.py` | 注册 `count_chars(text)` 工具，并验证它能通过统一执行器调用。 |
| 03 | [权限](03-permissions.md)；[permissions.py](../lessons/lesson-03/permissions.py)、[tools.py](../lessons/lesson-03/tools.py)、[test_permissions.py](../lessons/lesson-03/tests/test_permissions.py) | `permissions.py` | 新增对 `shutdown`、`reboot` 命令的拒绝规则。 |
| 04 | [上下文管理](04-context.md)；[context.py](../lessons/lesson-04/context.py)、[agent.py](../lessons/lesson-04/agent.py)、[test_context.py](../lessons/lesson-04/tests/test_context.py) | `context.py` | 长输出改为保留前 3/4、后 1/4，验证短输出和工具消息配对不受影响。 |
| 05 | [Skills](05-skills.md)；[skills.py](../lessons/lesson-05/skills.py)、[test_skills.py](../lessons/lesson-05/tests/test_skills.py) | `skills/git-summary/SKILL.md` | 写一个介绍如何总结 Git 改动的技能，并验证元数据能被解析。 |
| 06 | [聊天渠道](06-chat-apps.md)；[agent.py](../lessons/lesson-06/agent.py)、[bot.py](../lessons/lesson-06/bot.py)、[telegram.py](../lessons/lesson-06/telegram.py)、[tests/fake.py](../lessons/lesson-06/tests/fake.py) | `bot.py` | 添加 `/help`，用假渠道验证它直接返回帮助信息。 |
| 07 | [定时任务](07-scheduler-heartbeat.md)；[scheduler.py](../lessons/lesson-07/scheduler.py)、[test_scheduler.py](../lessons/lesson-07/tests/test_scheduler.py) | `scheduler.py` | 支持 `every 1d`、`every 2d` 的时间规则。 |
| 08 | [MCP](08-mcp.md)；[mcp_client.py](../lessons/lesson-08/mcp_client.py)、[demo_mcp_server.py](../lessons/lesson-08/demo_mcp_server.py)、[test_mcp.py](../lessons/lesson-08/tests/test_mcp.py) | `demo_mcp_server.py` | 增加 `echo(text)` MCP 工具，验证发现与调用过程。 |
| 09 | [子 Agent](09-subagents.md)；[subagent.py](../lessons/lesson-09/subagent.py)、[agent.py](../lessons/lesson-09/agent.py)、[test_subagent.py](../lessons/lesson-09/tests/test_subagent.py) | `subagent.py` | 为 `delegate()` 添加 `kind` 校验，拒绝非法类型。 |
| 10 | [计划](10-planning.md)；[planning.py](../lessons/lesson-10/planning.py)、[test_planning.py](../lessons/lesson-10/tests/test_planning.py) | `planning.py` | 拒绝内容重复的计划步骤，并验证拒绝后原计划保留。 |
| 11 | [记忆](11-memory.md)；[memory.py](../lessons/lesson-11/memory.py)、[context.py](../lessons/lesson-11/context.py)、[test_memory.py](../lessons/lesson-11/tests/test_memory.py) | `memory.py` | 重复添加同一条长期记忆时返回提示，避免重复保存。 |
| 12 | [Claude Code](12-claude-code.md)；回看第 11 课的 [permissions.py](../lessons/lesson-11/permissions.py)、[skills.py](../lessons/lesson-11/skills.py) | `notes/lesson-12.md`；`notes/comparison.md` | 建立对照表，记录文章中的权限、扩展和记忆设计。 |
| 13 | [Codex](13-codex.md)；[web/app.py](../web/app.py)、第 11 课的 [agent.py](../lessons/lesson-11/agent.py)、[permissions.py](../lessons/lesson-11/permissions.py) | `notes/lesson-13.md`、`notes/comparison.md` | 根据文章对照核心、界面、审批和沙箱分别解决的问题。 |
| 14 | [Pi](14-pi.md)；第 11 课的 [tools.py](../lessons/lesson-11/tools.py)、[context.py](../lessons/lesson-11/context.py) | `notes/lesson-14.md`、`notes/comparison.md` | 比较工具数量、上下文与扩展方式的取舍。 |
| 15 | [Grok Bot](15-grok-bot.md)；第 11 课的 [bot.py](../lessons/lesson-11/bot.py)、[scheduler.py](../lessons/lesson-11/scheduler.py) | `notes/lesson-15.md`、`notes/comparison.md` | 比较本地聊天渠道、远程电脑与定时任务的关系。 |
| 16 | [DeepSeek Harness](16-deepseek-harness.md)；第 11 课的 [mcp_client.py](../lessons/lesson-11/mcp_client.py)、[subagent.py](../lessons/lesson-11/subagent.py) | `notes/lesson-16.md`、`notes/comparison.md` | 画出文章中插件、工具、模型、子 Agent 的关系。 |
| 17 | [OpenClaw 与 Hermes](17-openclaw-hermes.md)；第 11 课的 [bot.py](../lessons/lesson-11/bot.py)、[memory.py](../lessons/lesson-11/memory.py) | `notes/lesson-17.md`、`notes/comparison.md` | 比较个人助手的渠道、定时任务和记忆设计。 |
| 18 | [总对照表](18-comparison.md)；自己的 `notes/lesson-01.md` 到 `notes/lesson-17.md` | `notes/lesson-18.md`、`notes/comparison.md`；`notes/final-summary.md` | 总结整体调用流程、已有能力和一个下一阶段想实现的功能。 |

第 12～18 课根据仓库文章做对照，文章以 2026 年 10 月为时间背景。

## 第 01～11 课具体怎么动手

### 第 01 课：看清循环

阅读 `run()` 时，按顺序找：初始化 `messages` → 调模型 → 添加 assistant 消息 → 判断 `tool_calls` → 执行工具 → 添加 tool 消息 → 下一轮。

编辑 `practice/lesson-01/agent.py`，在这三个位置加简短日志：调用模型前的消息数量、执行工具前的工具名、执行工具后的结果字符数。保留原有消息结构和循环结束条件。

从项目根目录运行自己的副本，任务参数要写到命令末尾：

```bash
mkdir -p generated/lesson-01
uv run --env-file .env python practice/lesson-01/agent.py "在 generated/lesson-01/hello.py 写一个打印 hello 的程序，并运行它"
```

上面的运行需要 `.env` 中的真实 Key，可以用来观察日志。现在也提供了第 01 课的假模型基础测试，写好源码后可先运行 `uv run --directory practice/lesson-01 python -m pytest -q`，验证文件读写、工具结果回传、错误反馈和步数上限，不需要真实 Key。

### 第 02 课：新增一个工具

阅读 `tool()`、`get_schemas()`、`execute()`。在练习的 `tools.py` 中，用已有的 `@tool` 注册方式增加 `count_chars(text)`，返回 `len(text)`。

字符统计工具的测试已写在 `practice/lesson-02/tests/test_tools.py`，写好实现后直接运行，验证：`hello` 返回字符串 `5`，`你好` 返回字符串 `2`，空字符串返回 `0`；同时验证新工具出现在 `get_schemas()` 中。这个练习不需要调用模型。

### 第 03 课：让权限规则产生可验证的差异

阅读 `PermissionManager.check()`、`SHELL_DENY_PATTERNS` 和现有测试里的 `make()` 假确认函数。测试已准备好：即便假确认函数会回答允许，`shutdown`、`reboot` 命令也应被拒绝，而且不会询问用户。你只需增加拒绝规则。

测试只向权限检查传入命令字符串，使用 `pm.check()` 验证结果。

### 第 04 课：改变截断策略

阅读 `truncate_tool_result()`、`clear_old_tool_results()`、`split_for_compact()`，理解三种处理各在什么情况下使用。

编辑练习的 `truncate_tool_result()`：在需要截断时，将保留的字符预算分成前 3/4、后 1/4。测试使用显式小预算，例如 `limit=40`，验证保留前 30、后 10 个原文字符，并继续显示省略提示；短字符串原样返回。

最后运行整课测试，确认已有的消息配对与会话保存检查仍通过。

### 第 05 课：用文件增加能力

填写已准备的 `practice/lesson-05/skills/git-summary/SKILL.md`，填写 `name`、`description` 和正文。正文写三条总结 Git 改动的规则，例如说明修改目的、受影响文件和验证结果。

元数据解析、发现与加载的测试已写好。你只需填写技能文件，然后运行注释中的测试命令。

体验自己写的技能时，从练习目录启动，让 `skills/` 位于该练习的工作区中：

```bash
uv run --directory practice/lesson-05 --env-file ../../.env python agent.py
```

### 第 06 课：把一个聊天命令接到渠道

阅读 `Session`、`handle_message()`、`make_chat_ask()` 和 `FakeChannel`。在白名单检查之后、创建普通会话之前处理 `/help`，直接通过渠道返回帮助信息，列出 `/help` 和已有的 `/reset`。

准备好的 `tests/test_bot.py` 会用假渠道验证白名单用户能收到帮助、非白名单用户仍被忽略，以及 `/help` 不创建普通模型会话。按这一方式完成练习时无需接入真实 Telegram。

### 第 07 课：增加按天重复的规则

阅读 `next_run()`、`Scheduler.add()` 和 `Scheduler.due()`。把 `next_run()` 的单位扩展为分钟、小时、天，并更新对应的规则说明。

准备好的 `tests/test_scheduler.py` 会用固定时间验证 `every 1d`、`every 2d` 分别增加一天、两天；保留原有分钟、小时和每日固定时间的测试。

### 第 08 课：给 MCP 服务器增加一个接口

按 `initialize()` → `list_tools()` → `call_tool()` 追踪一次客户端调用，再阅读服务器的 `TOOLS`、`call()`、`handle()`。

在练习的 `demo_mcp_server.py` 中增加 `echo(text)` 的工具说明和执行分支，返回输入文字。`tests/test_mcp.py` 的列表断言已调整，`echo` 调用测试也已准备好。运行的是仓库自带的本地 stdio 服务器。

### 第 09 课：校验子 Agent 的类型

阅读 `toolset()`、`_current()`、`_spawn()`、`delegate()`。先记清：`explore` 只拿只读工具，`worker` 可以拿写文件和运行命令的工具，实际副作用操作仍走用户确认。

在练习的 `delegate()` 中添加 `kind` 校验，只接受 `explore`、`worker`，非法值返回明确的 `Error`，且不创建子 Agent。类型校验、只读工具、并行和嵌套限制的测试都已准备好，写完实现后直接运行。

### 第 10 课：拒绝重复的计划步骤

阅读 `update_plan()`、`enter_plan_mode()`、`submit_plan()` 和测试里的计划批准流程。

在练习的 `update_plan()` 中增加重复步骤检查：两个步骤的 `step` 文本相同就返回 `Error`，检查放在更新当前计划之前。现成测试会验证重复步骤被拒绝，且 Session 原有计划没有被覆盖。

### 第 11 课：避免重复记忆

阅读 `remember()`、`load_entries()`、`memory_section()`、`search_sessions()`，再看 `context.py` 如何保存会话。

在练习的 `remember(action="add")` 中，按已有的空白归一化方式处理文本；发现相同条目时返回提示，保留一条记录。重复添加、空白归一化、替换、删除和长度限制的测试均已准备好，运行命令即可验证。

## 运行与验证

第 02～11 课可以从项目根目录运行自己的命令行副本，例如：

```bash
uv run --env-file .env python practice/lesson-02/agent.py
```

这些版本用终端交互输入任务。新增技能的第 05 课按上文的练习目录启动命令体验。

第 01～11 课的现成测试放在各课 `tests/` 目录，运行时检查同目录中的手写实现。第 03～11 课的基础测试复用原课程；第 01、02 课及扩展练习测试由我补写。来源和复制运行的命令都标在测试文件开头。

```bash
uv run --directory practice/lesson-03 python -m pytest -q
uv run --directory practice/lesson-03 python -m pytest -q tests/test_permissions.py
uv run --directory practice/lesson-03 python -m pytest -q -k test_read_needs_no_confirm
```

将 `03` 换成本课课号。测试使用假模型和临时工作区，不需要加载 `.env`。实现尚未填写时会报告缺少接口；完成实现后再根据测试断言继续修改。

你只需修改实现文件，测试已经包含基础行为和本计划中的扩展练习。先检查基础实现时，可复制下面这条命令；扩展也完成后运行完整测试：

```bash
uv run --directory practice/lesson-03 python -m pytest -q -k "not practice_exercise"
```

默认 `NAMI_WORKSPACE=.` 表示进程启动目录：从 NamiAgent 根目录启动，文件工作区就是项目；使用 `--directory practice/lesson-05` 时，文件工作区就是该练习目录。`.env` 始终放在项目根目录，用 `--env-file` 指定其路径。

## 每课完成后提交什么

每课提交本课的实现改动和 `notes/lesson-XX.md`；现成测试可以随初始配置一起提交。第 12～18 课提交笔记、对照表和最后的总结即可。

本课的笔记填写四件事：看了哪些文件、改了哪些文件、运行了什么验证、还有什么问题。记录实际完成的结果。笔记里的密钥和私人对话用占位符代替。

当前本地分支是 `main`，`origin` 指向 `https://github.com/inwf/NamiAgent.git`。第一次保存这次环境和学习目录配置时：

```bash
git status --short
git diff
git add -u
git add .env.example .python-version pyproject.toml uv.lock docs/learning-plan.md notes/ practice/
git diff --cached
git commit -m "配置 uv、启动方式与学习目录"
git push -u origin main
```

完成第 1 课的练习后：

```bash
git status --short
git diff
git add practice/lesson-01/ notes/lesson-01.md
git diff --cached
git commit -m "第01课：观察 Agent 的工具调用循环"
git push
```

后续把目录、笔记名称和提交信息替换为本课实际完成的内容。

`.gitignore` 忽略本地密钥文件、虚拟环境、缓存、日志、测试报告、状态目录、`generated/` 中的生成产物和旧的根目录演示 `hello.py`；`.env.example`、`.python-version`、`pyproject.toml`、`uv.lock`、课程源码、笔记、练习代码应该提交。新增忽略规则不会移除已经跟踪的文件，提交内容以 `git diff --cached` 为准。

## 生成文件放在哪里

生成的示例、临时文件和运行输出放在项目内的 `generated/`。该目录已被 Git 忽略；你的手写实现仍放在 `practice/`，学习笔记放在 `notes/`，它们正常提交。`NAMI_WORKSPACE=.` 保持使用启动目录。
