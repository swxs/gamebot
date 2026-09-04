# Agent Note: ScreenCapture 与 PyAuto 拆分

Status: implemented

## Problem

`PyAutoDesktopPackage` 混合了 hwnd 绑定、BitBlt 截图与 pyautogui 鼠键，违反 Protocol 单一职责：pyautogui 栈不需要 hwnd，截图才是 `ScreenCapture` 契约。

## Decision

- **`pyauto_desktop`**：仅 `PointerInput` + `KeyboardInput`（pyautogui），**无 bind、无 capture**
- **`win32_window_capture`**（新包）：`ScreenCapture` — BitBlt 客户区截图；`bind_from_env()`（`NAME` 或前台窗口）；`client_to_screen()` 供屏幕坐标点击
- **`opencv_matcher.find_and_click(capture_pkg, pointer_pkg, …)`**：capture → find → 必要时 `client_to_screen` → click；capture 与 pointer 同一实例时跳过坐标转换（win32 backend 路径）
- **testcase**：pyauto 路径装 `capture` + `desktop`；`bind_window` 绑 `capture`；backend 仍用合一的 `Win32BackendPackage`

## Alternatives considered

### Why not keep capture inside pyauto?

hwnd 生命周期与 pyautogui 输入无关；分离后 pyauto DAG 无需为鼠键配置 `NAME`。

### Why not use mss full-screen for pyauto?

模板匹配需与窗口客户区坐标一致；BitBlt + `ClientToScreen` 与现有模板资源对齐。

## Consequences

- **破坏性变更**：`find_and_click` 签名改为两包；`PyAutoDesktopPackage.unbound()` 移除
- **P0 包**：增补 `win32_window_capture`；[Handler 包 + Protocol](2026-09-03-handler-packages.md) 中 pyauto 描述已过时，以本笔记为准
- **测试**：`test_packages.py` 覆盖 capture bind 与坐标转换分支
