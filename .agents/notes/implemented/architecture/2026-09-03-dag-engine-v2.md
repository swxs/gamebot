# Agent Note: DAG 引擎 v2

Status: implemented

## Problem

v1 DAG 引擎使用 `Selector` 做条件边、节点函数签名为 `(handler, hwnd) -> bool`，状态无法通过 Group 作用域共享；API 与 wayfinder 决策不一致，难以扩展嵌套流程与并行分支。

## Decision

重写 `src/gamebot/dag.py`：

- **Group**：嵌套子图容器；`setup(vars)` 注入变量模板；`get`/`set`/`vars` 链式查找 + 本地 shadow；每轮 `for` restore vars
- **Node**：`Node(name, func, pre=None, post=None)`；转移语义 `current.post → next.pre → next.func`；func False 时 pending 仅重试 func
- **Context**：统一 hook 签名 `(ctx: Context) -> bool`；`ctx.get`/`ctx.set`/`ctx.vars`
- **并行分支**：`node >> [a, b, c]` 先 post，再按序 pre 过滤，只对赢家执行 func
- **移除 Selector**；`next_list` 简化为 `List[Node]`
- **cli**：读 `module.group`；`group.setup({"handler": ..., "hwnd": ...})`
- **dags/**：引擎 PR 删除全部旧脚本，留 `.gitkeep`

## Alternatives considered

### Why not keep Selector?

Selector 与 Node.pre 职责重叠；去掉 Selector 可简化 `connect`/`forward` 与遍历引擎。链式守卫迁移为目标 Node 的 `pre`；并行分支用 pre 过滤。

### Why not keep (handler, hwnd) signature?

与 Group vars 统一：handler/hwnd 作为 vars 普通 key，节点只依赖 Context，便于测试与嵌套作用域。

### Why not migrate Hearthstone in this PR?

引擎先行；旧 DAG 删除，后续 effort 交付最小 testcase + `dags/README.md`。

## Consequences

- **破坏性变更**：所有用户 DAG 需重写为 `(ctx) -> bool` 并导出 `group`
- **测试**：`tests/test_dag.py` 覆盖 10 项核心语义，不依赖真实 UI
- **遗留**：Handler `get_hwnd` 等问题未在本变更修复；无用户 DAG 时 cli 仍无法端到端跑通
