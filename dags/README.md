# DAG 作者指南

加载路径：`dags/<目录>/<模块>.py`，`.env` 中 `DAG=testcase.pyauto_run`。

每个 DAG 模块必须导出 **`group`** 与 **`build_setup()`**。细节见仓库根目录 [AGENTS.md](../AGENTS.md)。

## Smoke

```env
NAME=窗口标题
DAG=testcase.pyauto_run
PIX=
NUMBER=1
```

```bash
gamebot
```

backend 路径：`DAG=testcase.backend_run`。
