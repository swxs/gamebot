# Agent Note: Handler 栈 + Protocol 架构

Status: implemented

## Problem

Handler 层为单体 `Base` 类 + `Productor` 工厂；Package 目录按「一个 Protocol 一个文件夹」组织，**环境依赖检查**与 **Protocol 实现**混在同一文件；同栈多 Handler（如 win32 backend + capture）无法共享 `check_deps`；同 Protocol 多实现（如 pyauto 直接点击 vs 拟人点击）缺少扩展位。

## Decision

### 分层

| 层级 | 路径 | 职责 |
|------|------|------|
| **Protocol** | `gamebot/protocols/` | 固定操作契约（不变） |
| **Package（栈）** | `handlers/packages/<stack>/package.py` | `check_deps()` + `install_*()` 工厂；DAG setup 时按 Handler `__package__` **去重**调用 |
| **Handler** | 同栈下独立模块（如 `backend.py`、`pointer_direct.py`） | 实现一个或多个 Protocol；注册到 `ctx.pkg(name)` 的实例 |

基类与 setup 钩子：`_package.py` 中 `Package` + `check_packages()`；`Group.setup()` 安装 packages 后立即调用。

### 栈布局（P0）

```
handlers/packages/
  _package.py          # Package 基类、check_packages
  _hwnd.py             # win32 窗口查找共享
  win32/
    package.py         # Win32Package — check_deps + install_backend / install_capture
    _bound.py          # Win32BoundMixin（bind_from_env）
    backend.py         # Win32BackendHandler — WindowControl + ScreenCapture + Clipboard + Keyboard
    capture.py         # Win32CaptureHandler — ScreenCapture
  pyauto/
    package.py         # PyAutoPackage
    pointer_direct.py  # PyAutoPointerDirectHandler — PointerInput + KeyboardInput
  opencv/
    package.py, matcher.py, _cv.py
  pyperclip/
    package.py, clipboard.py
```

### 关键规则

- **`ctx.pkg(name)` 仍是 Handler 实例**，不是 Package 类
- **同 Protocol 多实现** → 多个 pkg 键（如未来 `pointer_direct` / `pointer_human`），各自 `install_*()`
- **同栈多 Handler** → 共享 `__package__ = Win32Package`，`check_deps` 只跑一次
- **一个 Handler 可多 Protocol** — `Win32BackendHandler` 同时满足 WindowControl、ScreenCapture、ClipboardAccess、KeyboardInput

### DAG 安装示例

```python
"desktop": PyAutoPackage.install_pointer_direct(),
"capture": Win32Package.install_capture(),
"matcher": OpenCVPackage.install_matcher(),
"clipboard": PyperclipPackage.install_clipboard(),
# backend 路径：desktop = Win32Package.install_backend()，无需单独 capture
```

### 找图点击

`find_and_click(capture, pointer, template_path)` — 见 [ScreenCapture 与 PyAuto 拆分](2026-09-04-screen-capture-split.md)

## Alternatives considered

### Why not check_deps inside install_*?

setup 阶段集中失败更清晰；同一栈装多个 handler 时不重复 import 探测。

### Why not one folder per Protocol?

win32 backend 天然跨 Protocol；栈级 Package 更贴合 pip extra（`[win32]`、`[pyauto]`）与依赖边界。

### Why not keep compatibility aliases?

已移除；对外仅暴露 `*Package.install_*()` 工厂与 Handler 类名，避免 Package/Handler 同名混淆。

## Consequences

- **破坏性变更（对外 API）**：旧路径 `pyauto_desktop/`、`win32_backend/` 等目录删除；推荐 `install_*` 工厂
- **Group.setup**：新增 `check_packages` 调用；缺依赖时 setup 即报错
- **测试**：`test_packages.test_check_packages_dedupes_stack`；mock bind 路径改为 `_hwnd`
- **BrowserAutomation**：Protocol stub 留后续 playwright 栈
