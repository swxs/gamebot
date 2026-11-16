# DAG 作者指南

加载路径：`dags/<目录>/<模块>.py`。入口只接收模块路径，例如 `gamebot example.todomvc`。

每个 DAG 模块必须导出 **`group`** 与 **`build_setup()`**。启动参数写在 `build_setup()` 里。细节见仓库根目录 [AGENTS.md](../AGENTS.md)。

## 示例

```bash
gamebot example.todomvc
gamebot testcase.pyauto_run
```
