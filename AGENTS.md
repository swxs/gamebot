# AGENTS.md

本文件为 AI 编码助手提供 **gamebot** 项目的上下文与操作指南。

## 项目概述

gamebot 是一个 **Windows 平台的游戏自动化脚本框架**。通过图像识别（OpenCV 模板匹配）定位 UI 元素，再模拟鼠标/键盘操作完成重复性游戏任务。

核心思路：

1. 用 `.env` 配置目标窗口、DAG 模块、模板图子目录
2. DAG 在 `build_setup()` 中安装 Handler **Package**（pyauto / win32 backend / opencv matcher 等）
3. 节点通过 `ctx.pkg(name)` 调用 Protocol 能力；窗口绑定由显式节点 `bind_from_env()` 完成
4. DAG 用状态图描述流程（`Group` / `Node` + `>>`）；`gamebot` CLI 循环执行直到 `NUMBER` 次

**平台限制**：仅支持 Windows（依赖 `pywin32`、`pyautogui` 等）。

## 目录结构

```
gamebot/
├── pyproject.toml
├── dags/                         # 用户 DAG（须 export group + build_setup）
├── tests/
└── src/gamebot/
    ├── cli.py
    ├── dag.py
    ├── dashboard/              # CLI 本地浏览器 dashboard（SSE）
    ├── protocols/                # ScreenCapture、TemplateMatcher 等 Protocol
    ├── handlers/packages/        # 栈级 Package + Handler（win32、pyauto、opencv、pyperclip）
    └── core/
```

模板图路径：`dags/<category>/files/<PIX>/`，可用 `core.path.dag_files_dir(category, PIX)`。

## 环境配置

复制 `.env.example` 为 `.env`（`.env` 已在 `.gitignore`，不提交）：

```powershell
copy .env.example .env
```

```env
NAME=窗口标题
NUMBER=0
DAG=testcase.pyauto_run
PIX=
DASHBOARD_PORT=8765
DASHBOARD_OPEN=1
```

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `NAME` | `None` | 窗口标题；留空时 bind 节点绑定**当前前台窗口** |
| `NUMBER` | `0` | 循环次数，`0` 无限 |
| `DAG` | `testcase.pyauto_run` | 模块路径，如 `testcase.backend_run` |
| `PIX` | `""` | 模板图子目录名 |
| `DASHBOARD_PORT` | `8765` | dashboard HTTP 端口 |
| `DASHBOARD_OPEN` | `False` | `1`/`true` 时启动 CLI 自动打开浏览器 |

```env
DASHBOARD_PORT=8765
DASHBOARD_OPEN=1
```

启动 `gamebot` 后终端打印 `dashboard: http://127.0.0.1:8765/`；浏览器内实时显示 DAG 图与参数（SSE）。

## 依赖与运行

```bash
uv venv .venv
uv pip install -e ".[dev]"
gamebot
pytest
```

Optional extras：`[pyauto]`、`[win32]`、`[opencv]`、`[playwright]`、`[all]`。

## 架构要点

### Handler 栈 + Protocol

| 层级 | 路径 | 职责 |
|------|------|------|
| Protocol | `gamebot/protocols/` | 能力契约（`@runtime_checkable`） |
| Package（栈） | `handlers/packages/<stack>/package.py` | `check_deps()` + `install_*()`；setup 时去重检查依赖 |
| Handler | 同栈下 `*.py` | 实现 Protocol；`ctx.pkg(name)` 取实例 |
| 安装 | `Group.setup({"packages": {...}, ...})` | pkg 名 → Handler 实例；自动 `check_packages` |
| 访问 | `ctx.pkg("desktop")` | 链式向上查找，子 Group 可 shadow |

P0 栈：`pyauto`（鼠键）、`win32`（backend / capture）、`opencv`（matcher）、`pyperclip`（clipboard）。

同 Protocol 多实现：多个 pkg 键（如 `pointer_direct` / 未来 `pointer_human`）。同栈多 Handler 共享一次 `check_deps`（如 backend + capture 均属 `Win32Package`）。

需 hwnd：`Win32Package.install_capture()` 或 `install_backend()` → 节点内 `bind_from_env()`。`PyAutoPackage.install_pointer_direct()` 无 bind。

### DAG 状态图（`dag.py`）

- 转移：`A.post → B.pre → B.func`；并行 `[B,C,D]` 先 post 再按序 pre
- 节点签名：`(ctx: Context) -> bool`
- 详见 [DAG 引擎 v2](.agents/notes/implemented/architecture/2026-09-03-dag-engine-v2.md)

### 图像识别流程

```python
ctx.pkg("matcher").find_and_click(ctx.pkg("capture"), ctx.pkg("desktop"), template_path, sens=0.8)
```

等价于 capture → find → click（capture 客户区坐标，pyauto 点击前转屏幕坐标）。

## 常见任务

### 新增 DAG

1. 在 `dags/<category>/` 创建模块，导出 `group` 与 `build_setup()`
2. `build_setup()` 返回 `{"packages": {...}, ...}` 及业务 vars
3. 首节点或前置节点：`bind_window` 绑定 `capture`（pyauto 路径）或 `desktop`（win32 backend 路径）
4. 模板图放 `dags/<category>/files/<PIX>/`

### 调试

```bash
pytest tests/test_dag.py tests/test_packages.py
```

## 编码规范

1. 最小改动；匹配现有风格（中文注释）
2. Windows 专用 API，不引入跨平台抽象
3. 命名沿用：`FIEL_PATH`、`find_assents` 拼写仅在遗留上下文提及
4. 节点 `(ctx) -> bool`；等待用 `time.sleep`
5. 不提交 `.env`、截图缓存、虚拟环境

## 测试

- `test_dag.py`：引擎 + `ctx.pkg`
- `test_dashboard.py`：图序列化、快照、HTTP/SSE
- `test_protocols.py`：Protocol isinstance
- `test_packages.py`：mock bind / find / clipboard

## Git 与提交

- 仅在用户明确要求时 commit
- 不要提交 `.env` 或密钥

## 快速参考

```python
from gamebot.dag import Group, Node
from gamebot.handlers.packages.pyauto import PyAutoPackage
from gamebot.handlers.packages.win32 import Win32Package
from gamebot.handlers.packages.opencv import OpenCVPackage


def build_setup():
    return {
        "packages": {
            "desktop": PyAutoPackage.install_pointer_direct(),
            "capture": Win32Package.install_capture(),
            "matcher": OpenCVPackage.install_matcher(),
        },
    }


def bind_window(ctx):
    ctx.pkg("capture").bind_from_env()
    return True


def my_action(ctx):
    ctx.set("step", ctx.get("step", 0) + 1)
    return True


group = Group(name="main")
with group as group:
    group >> Node("bind", bind_window) >> Node("work", my_action)
```

详见 [Handler 包 + Protocol](.agents/notes/implemented/architecture/2026-09-03-handler-packages.md)。
