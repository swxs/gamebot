# AGENTS.md

本文件为 AI 编码助手提供 **gamebot** 项目的上下文与操作指南。

## 项目概述

gamebot 是一个 **Windows 平台的游戏自动化脚本框架**。通过图像识别（OpenCV 模板匹配）定位 UI 元素，再模拟鼠标/键盘操作完成重复性游戏任务。

核心思路：

1. 入口只接收 DAG 模块路径：`gamebot example.todomvc`
2. 启动参数写在该模块的 `build_setup()` 里，不读 dotenv
3. DAG 在 `build_setup()` 中安装 Handler **Package**（pyauto / win32 / opencv / playwright 等）
4. 节点通过 `ctx.pkg(name)` 调用 Protocol 能力；桌面窗口由 `bind_title(title)` 绑定，标题不来自 `name`
5. DAG 用状态图描述流程（`Group` / `Node` + `>>`）；CLI 按 `number` 跑有限次，并写下跑通产物

**平台限制**：仅支持 Windows（依赖 `pywin32`、`pyautogui` 等）。

## 编写合同

DAG 作者（主要是大模型）可以依赖这些规则。

- 模块导出 `group` 与 `build_setup()`。`build_setup()` 返回 dict。
- 入口只有模块路径。`name` 是运行名字，必填、非空，不用来找窗口。
- 启动键：`name`、`number`（省略为 1，小于 1 拒绝启动）、`pix`（省略为 `""`）、`dashboard_port`（省略为 8765）、`dashboard_open`（省略为否）。
- 节点 `(ctx) -> bool`。返回 `false` 即这次失败。框架不在节点失败后自动重试。
- 要操作桌面窗口时，节点调用 `bind_title(title)`。浏览器示例不绑定桌面窗口。
- 桌面能力：截图、找图点击、区域内查找、`find_all`（没有则空列表）、`wait`（默认 10 秒、每 0.5 秒，超时返回 `None`）、双击、拖拽、滚轮、组合键、屏幕 OCR、Windows 控件树（含控件文字）、剪贴板、窗口焦点。四角失败保护只停真实光标。
- 找不到目标时，`find_all`、屏幕 OCR、控件树给空结果，不因此让节点失败。等到出现的超时，以及浏览器动作或浏览器断言不成立，算这次失败。
- 浏览器能力与找图点击并列，走 `ctx.pkg("browser")`：打开网址，按选择器或 `{by, value, name}` 填写、点击、按键、拖拽。`by` 可以是 `role`、`text`、`label`、`placeholder`、`alt`、`title`、`test_id`、`css`。含动作前等待、浏览器断言和 trace。trace 不是跑通判据。
- 每步把产物写到 `runs/<name>/`：`previous.png`（没有上一步则为空）、`current.png`、`tree.txt`、`steps.json`（最近 5 步）。有已打开的浏览器页面时，`current.png` 用页面截图，否则用已绑定窗口的客户区。页面是否走完以这两张图为准。
- 浏览器示例：`gamebot example.todomvc`。`name` 为 `TodoMVC`，`number` 为 1。人把 `https://demo.playwright.dev/todomvc` 摆到空列表；走完是指当前客户区上恰好有一条「跑通」。控件树里没有这几个字，不单独判失败。
- pytest 测引擎。真实窗口和真实 Chromium 不是测试门禁。

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
    ├── handlers/packages/        # 栈级 Package + Handler（win32、pyauto、opencv、pyperclip、playwright）
    └── core/
```

模板图路径：`dags/<category>/files/<pix>/`，`pix` 来自 `ctx.get("pix")`，用 `dag_files_dir(category, pix)`。

## 环境配置

不读 `.env`。启动：

```powershell
gamebot example.todomvc
```

终端打印 `dashboard: http://127.0.0.1:8765/`。dashboard 给人看运行，模型看 `runs/<name>/` 里的产物。

## 依赖与运行

```bash
uv venv .venv
uv pip install -e ".[dev]"
gamebot example.todomvc
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

P0 栈：`pyauto`（鼠键）、`win32`（backend / capture / controls / ocr）、`opencv`（matcher）、`pyperclip`（clipboard）、`playwright`（chromium，optional extra）。

同 Protocol 多实现：多个 pkg 键（如 `pointer_direct` / 未来 `pointer_human`）。同栈多 Handler 共享一次 `check_deps`（如 backend + capture 均属 `Win32Package`）。

需 hwnd：`Win32Package.install_capture()`、`install_backend()` 或 `install_controls()` → 节点内 `bind_title(title)`。`PyAutoPackage.install_pointer_direct()` 无 bind。浏览器包不绑定桌面窗口。

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
2. `build_setup()` 返回 `name` 和 `{"packages": {...}, ...}`。桌面流程另放业务键 `window` 作为 `bind_title` 的标题
3. 桌面 DAG 的首节点调用 `bind_title`。浏览器 DAG 不绑定窗口
4. 模板图放 `dags/<category>/files/<pix>/`

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
- `test_packages.py`：mock bind / find / clipboard / OCR
- `test_evidence.py`：产物只留最近 5 步
- `test_browser.py`：假页面上的浏览器调用
- `test_cli.py`：模块加载与启动参数校验

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
        "name": "main",
        "window": "窗口标题",
        "packages": {
            "desktop": PyAutoPackage.install_pointer_direct(),
            "capture": Win32Package.install_capture(),
            "matcher": OpenCVPackage.install_matcher(),
        },
    }


def bind_window(ctx):
    ctx.pkg("capture").bind_title(ctx.get("window"))
    return True


def my_action(ctx):
    ctx.set("step", ctx.get("step", 0) + 1)
    return True


group = Group(name="main")
with group as group:
    group >> Node("bind", bind_window) >> Node("work", my_action)
```

详见 [Handler 包 + Protocol](.agents/notes/implemented/architecture/2026-09-03-handler-packages.md)。
