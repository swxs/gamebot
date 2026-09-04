# Agent Note: CLI 本地 Dashboard

Status: implemented

## Problem

CLI 仅打印节点名，运行中无法感知 DAG 拓扑、当前节点与 vars；调试依赖终端输出，嵌套 Group 与 pending 状态不直观。

## Decision

`gamebot` 启动后在同进程拉起 **localhost HTTP dashboard**（`gamebot/dashboard/`）：

- **布局**：左主区流程图（上下布局）↔ 树形可切换；右侧参数四段表（env / runtime / packages / vars），面板可向右收起
- **同步**：SSE `/api/stream` 步进推送；`/api/graph` 一次下发拓扑；`StateHub` 线程安全
- **快照**：`current`/`pending` 为 `group.node`；vars 含 root + 当前节点所属 Group 本地 vars
- **图序列化**：隐藏 `__start`；嵌套 Group 流程图用虚线容器
- **生命周期**：HTTP 随 CLI 始终启；`DASHBOARD_OPEN=1` 才 `webbrowser.open`；断流冻结 + 顶栏「已停止」；`DASHBOARD_PORT` 默认 8765、占用即失败
- **配置**：`.env.example` 模板；`.env` 不提交

## Alternatives considered

### Why not WebSocket?

单向推送足够；stdlib `http.server` + SSE 无新依赖。

### Why not 端口自动递增？

Wayfinder 决策：冲突应显式改 `DASHBOARD_PORT`，避免连到未知旧实例。

### Why not TUI？

首期只做浏览器；终端内 TUI 留后续。

## Consequences

- **依赖**：无新 pip 包；dashboard 静态页在 `dashboard/static/index.html`
- **测试**：`tests/test_dashboard.py`（序列化、HTTP、端口占用）
- **CLI**：`ListenThread` 每步 `publish`；主线程 `join` 等待结束
