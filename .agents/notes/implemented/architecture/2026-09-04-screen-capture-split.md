# Agent Note: ScreenCapture 与 PyAuto 拆分

Status: implemented

## Problem

早期 `PyAutoDesktopPackage` 混合 hwnd 绑定、BitBlt 截图与 pyautogui 鼠键，违反 Protocol 单一职责。

## Decision

- **`pyauto` 栈 / `PyAutoPointerDirectHandler`**：仅 `PointerInput` + `KeyboardInput`，无 bind、无 capture
- **`win32` 栈 / `Win32CaptureHandler`**：`ScreenCapture` — BitBlt 客户区；`bind_title(title)`；`client_to_screen()`
- **`win32` 栈 / `Win32BackendHandler`**：backend 路径合一实现 WindowControl + ScreenCapture + Clipboard + Keyboard
- **`opencv` 栈 / `OpenCVMatcherHandler.find_and_click(capture, pointer, …)`**：capture → find → 必要时 `client_to_screen` → click；capture 与 pointer 同一实例时跳过坐标转换
- **testcase**：pyauto 路径 `PyAutoPackage.install_pointer_direct()` + `Win32Package.install_capture()`；backend 路径 `Win32Package.install_backend()`

栈级组织见 [Handler 栈 + Protocol](2026-09-03-handler-packages.md)。

## Alternatives considered

### Why not keep capture inside pyauto?

hwnd 与 pyautogui 输入无关；分离后 pyauto DAG 鼠键路径无需为 `NAME` 配置窗口（截图节点单独 bind `capture`）。

### Why not use mss full-screen for pyauto?

模板匹配需窗口客户区坐标；BitBlt + `ClientToScreen` 与现有模板资源对齐。

## Consequences

- **破坏性变更**：`find_and_click` 两包签名；旧目录 `pyauto_desktop`、`win32_window_capture` 已并入 `pyauto/`、`win32/`
- **测试**：`test_packages.py` 覆盖 capture bind 与坐标转换分支
