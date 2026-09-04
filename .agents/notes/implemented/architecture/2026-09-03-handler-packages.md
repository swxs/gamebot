# Agent Note: Handler 包 + Protocol 架构

Status: implemented

## Problem

Handler 层为单体 `Base` 类 + `Productor` 工厂 + `HANDLER` 环境变量选型；API 不一致（`find_assents`、`get_hwnd` 缺失）；cli 注入 `handler`/`hwnd` 与 DAG v2 的 Context 模型割裂；难以组合多种输入栈（pyauto / win32 backend / opencv / clipboard）。

## Decision

- **Protocol** 定义能力契约（`gamebot/protocols/`，7 个 Protocol + `types.py`）
- **Package** 组合实现 Protocol（`gamebot/handlers/packages/<name>/`）
- **Group.setup(vars)** 含 `packages` 字典；**Context.pkg(name)** 链式查找，与业务 vars 分离
- **cli** 只调 `module.build_setup()`，不参与包装配；**hwnd** 由节点 `bind_from_env()` 触发（pyauto 路径绑 `capture`，backend 绑 `desktop`）
- **Breaking**：删除 `Base`、Productor、`HANDLER`；DAG 通过 `ctx.pkg()` 使用能力
- **P0 五包**：`pyauto_desktop`（鼠键）、`win32_window_capture`（截图）、`win32_backend`、`opencv_matcher`、`pyperclip_pkg`
- **找图点击**：`find_and_click(capture, pointer, template_path)` — 见 [ScreenCapture 与 PyAuto 拆分](2026-09-04-screen-capture-split.md)

## Alternatives considered

### Why not compatibility facade?

ticket 01 已切断 cli→handler 路径；facade 与 `ctx.pkg` 双轨并存，维护成本高。

### Why not win32_frontend?

硬编码分辨率、API 为类方法；本 effort 废弃，仅保留 pyauto + backend 两栈。

### Why separate TemplateMatcher package?

节点不直接 `import cv2`；匹配逻辑可独立测试与替换。

## Consequences

- **破坏性变更**：DAG 必须 `build_setup()` + `ctx.pkg()`；旧 `(handler, hwnd)` 与 `HANDLER` 配置失效
- **测试**：分层 pytest（dag pkg、protocol、package mock）；E2E 人工 smoke（`testcase/pyauto_run`、`backend_run`）
- **BrowserAutomation**：Protocol stub 已建，playwright 包留后续
- **CLI dashboard**：[CLI 本地 Dashboard](2026-09-04-cli-dashboard.md)
