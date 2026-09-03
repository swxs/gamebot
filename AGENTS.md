# AGENTS.md

本文件为 AI 编码助手提供 **gamebot** 项目的上下文与操作指南。

## 项目概述

gamebot 是一个 **Windows 平台的游戏自动化脚本框架**。通过图像识别（OpenCV 模板匹配）定位 UI 元素，再模拟鼠标/键盘操作完成重复性游戏任务。

核心思路：

1. 用 `.env` 配置目标窗口、Handler 类型、要运行的 DAG 脚本
2. Handler 负责截图、找图、点击（三种实现：`pyauto` / `frontend` / `backend`）
3. DAG 用状态图描述自动化流程（`Group` / `Node` + `>>` 运算符连边）
4. `gamebot` CLI 加载 DAG 并在独立线程中循环执行，直到达到 `NUMBER` 次

**平台限制**：仅支持 Windows（依赖 `pywin32`、`pyautogui` 等）。

## 目录结构

```
gamebot/
├── pyproject.toml          # 包定义、依赖、console_scripts
├── dags/                   # 用户 DAG 脚本（file_loader 加载）
├── tests/                  # pytest 单元测试
└── src/gamebot/
    ├── cli.py              # 入口：gamebot 命令
    ├── dag.py              # 状态图引擎（Group、Node、Context）
    ├── core/               # 配置、路径
    ├── handlers/           # Handler 实现
    └── commons/            # Productor 工厂
```

每个 DAG 目录下可放置 `files/<PIX>/` 子目录，存放模板图片。

## 环境配置

在项目根目录创建 `.env` 文件：

```env
NAME=窗口标题
NUMBER=0
HANDLER=pyauto
DAG=testcase.run
PIX=1920x1080_CN
```

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `NAME` | `None` | 窗口标题；未设置时程序退出 |
| `NUMBER` | `0` | 循环次数，`0` 表示无限 |
| `HANDLER` | `pyauto` | `frontend` / `pyauto` / `backend` |
| `DAG` | `test` | 模块路径，如 `my_game.task` |
| `PIX` | `""` | 模板图片子目录名 |

模板图片路径：`dags/<模块路径>/files/<PIX>/`，由 `core.path.FIEL_PATH` 拼接。

## 依赖与运行

```bash
uv venv .venv
uv pip install -e ".[dev]"
gamebot                    # 或 python -m gamebot.cli
pytest
```

VS Code：`.vscode/launch.json` 中 **RUN[BOT-MAIN]** 使用 `"module": "gamebot.cli"`。

## 架构要点

### Handler 工厂（`commons/Helper_productor.py`）

`Productor` 扫描 `handlers/`，通过 `handler_productor[HANDLER]` 获取 Handler **类**。

### DAG 状态图（`src/gamebot/dag.py`）

| 类型 | 用途 |
|------|------|
| `Group` | 子图容器，支持嵌套；`setup(vars)` 注入变量；`get`/`set`/`vars` 管理作用域 |
| `Node` | 动作节点，`func(ctx) -> bool`；可选 `pre`/`post` 守卫 |
| `Context` | 节点 hook 参数；`ctx.get`/`ctx.set`/`ctx.vars` |

**转移语义**（从 A 到 B）：

```
A.post → B.pre → B.func
```

- 任一 False → 停留；func False → pending，下次仅重试 func
- 并行 `>> [B, C, D]`：先 `A.post`，再按序找第一个 `pre` 为 True 的候选，只对赢家跑 func

**连接语法**：

```python
from gamebot.dag import Group, Node

group = Group(name="main")
with group as group:
    sub = Group(name="sub")
    a = Node("a", func_a, pre=guard_a)
    b = Node("b", func_b)
    group >> a >> sub >> b
    group >> a >> [b, other]
```

- 模块导出 **`group = Group(...)`**（cli 读 `module.group`）
- 节点函数签名：**`(ctx: Context) -> bool`**
- handler/hwnd 由 cli 写入 vars：`ctx.get("handler")`、`ctx.get("hwnd")`

详见 [Agent Note: DAG 引擎 v2](.agents/notes/implemented/architecture/2026-09-03-dag-engine-v2.md)。

### 图像识别流程

1. `handler.screen(filename)` 截图
2. `handler.find_assents(total, target_path, sens=0.8)` 模板匹配
3. 匹配成功后随机选取命中点并点击

## 编码规范

1. **最小改动**：只改与任务相关的文件
2. **匹配现有风格**：中文注释、Handler 继承 `Base`
3. **Windows 专用 API**：不引入跨平台抽象，除非明确要求
4. **命名沿用现状**：`FIEL_PATH`、`find_assents` 等拼写保持一致
5. **节点函数**：`(ctx) -> bool`；UI 等待用 `time.sleep`
6. **不要提交**：`.env`、截图缓存、虚拟环境

## 常见任务

### 新增一个 DAG

1. 在 `dags/<category>/` 下创建模块，如 `my_game/task.py`
2. 定义节点函数与 `Group`/`Node` 图结构
3. 导出 `group = Group(name="main")`
4. 在 `files/<PIX>/` 下放置模板图片
5. `.env` 中设置 `DAG=my_game.task`

### 调试 DAG 逻辑

```bash
pytest tests/test_dag.py
```

## 已知问题

1. **`handler.get_hwnd()`**：Handler 类未定义类方法；cli 调用会失败，需后续修复
2. **`find_ellement_and_click`**：未在 Handler 基类实现
3. **无用户 DAG**：引擎 PR 已删除旧脚本；需迁移 effort 添加 `dags/testcase/run.py`

## 测试

```bash
pytest
```

`tests/test_dag.py` 覆盖线性流、pre/post、pending、vars、嵌套 Group、并行 pre 过滤等。

## Git 与提交

- 仅在用户明确要求时创建 commit
- 不要提交 `.env` 或含密钥的文件

## 快速参考

```python
from gamebot.dag import Group, Node

def my_action(ctx):
    handler = ctx.get("handler")
    hwnd = ctx.get("hwnd")
    ctx.set("step", ctx.get("step", 0) + 1)
    return True

group = Group(name="main")
with group as group:
    start = Node("start", my_action)
    end = Node("end", lambda ctx: True)
    group >> start >> end
```
