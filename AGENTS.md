# AGENTS.md

本文件为 AI 编码助手提供 **gamebot** 项目的上下文与操作指南。

## 项目概述

gamebot 是一个 **Windows 平台的游戏自动化脚本框架**。通过图像识别（OpenCV 模板匹配）定位 UI 元素，再模拟鼠标/键盘操作完成重复性游戏任务。

核心思路：

1. 用 `.env` 配置目标窗口、Handler 类型、要运行的 DAG 脚本
2. Handler 负责截图、找图、点击（三种实现：`pyauto` / `frontend` / `backend`）
3. DAG 用状态图描述自动化流程（`Group` / `Node` / `Selector` + `>>` 运算符连边）
4. `main.py` 加载 DAG 并在独立线程中循环执行，直到达到 `NUMBER` 次

**平台限制**：仅支持 Windows（依赖 `pywin32`、`pyautogui` 等）。

## 目录结构

```
gamebot/
├── main.py                 # 入口：加载 handler + DAG，启动执行线程
├── core/
│   ├── config.py           # 从 .env 读取配置
│   └── path.py             # 路径常量（SITE_ROOT、FIEL_PATH）
├── commons/
│   └── Helper_productor.py # 插件工厂：自动发现并注册 Handler / DAG 子类
├── handlers/
│   ├── base_handler.py     # Handler 基类（截图、模板匹配接口）
│   ├── pyauto_handler.py   # 基于 pyautogui + mss 的前台操作
│   ├── frontend_handler.py # 基于 win32api 的前台操作
│   ├── backend_handler.py  # 基于 SendMessage 的后台操作（窗口可不可见）
│   └── utils/              # cv_utils、hwnd_utils、point_utils、path_utils
└── dags/
    ├── dag.py              # 状态图引擎（Group、Node、Selector）
    ├── testcase/run.py     # 纯逻辑测试 DAG（无真实 UI 操作）
    ├── alipay/signin.py    # 支付宝签到（未完成/示例）
    └── Hearthstone_Mercenaries/one_one.py  # 炉石佣兵战纪示例
```

每个 DAG 目录下可放置 `files/<PIX>/` 子目录，存放该分辨率/语言下的模板图片（按钮、UI 元素等）。

## 环境配置

在项目根目录创建 `.env` 文件（已被 `.gitignore` 忽略）：

```env
# 目标窗口标题（必填）
NAME=窗口标题

# 运行次数：0 = 无限循环，>=1 = 指定次数
NUMBER=0

# Handler 类型：pyauto | frontend | backend
HANDLER=pyauto

# DAG 模块路径（对应 dags/ 下的 Python 模块，用点号分隔）
DAG=testcase.run

# 模板图片子目录名（如 1920x1080_CN），留空则 files/ 下无子目录
PIX=1920x1080_CN
```

### 配置项说明

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `NAME` | `None` | 窗口标题，用于查找 HWND；未设置时程序退出 |
| `NUMBER` | `0` | 循环次数，`0` 表示无限 |
| `HANDLER` | `pyauto` | `frontend`/`pyauto` 需窗口可见；`backend` 可后台运行 |
| `DAG` | `test` | 模块路径，如 `Hearthstone_Mercenaries.one_one` |
| `PIX` | `""` | 模板图片目录后缀 |

模板图片路径：`dags/<DAG模块路径>/files/<PIX>/<相对路径>`，由 `core.path.FIEL_PATH` 拼接。

## 依赖与运行

- **Python**：3.8（见 `Pipfile`）
- **包管理**：Pipenv（`Pipfile` 中 `[packages]` 当前为空，需自行安装以下依赖）

```bash
pipenv install environs opencv-python pyautogui mss pywin32 numpy
pipenv run python main.py
```

或在 VS Code 中使用 `.vscode/launch.json` 中的 **RUN[BOT-MAIN]** 配置调试。

## 架构要点

### Handler 工厂（`commons/Helper_productor.py`）

`Productor` 扫描目录下所有 `*.py`，自动注册继承自基类的子类，通过 `productor[name]` 按类的 `name` 属性获取。

- `handlers/__init__.py`：`handler_productor[HANDLER]` → 返回 Handler **类**
- `dags/__init__.py`：`dag_productor` 注册所有 `Group` 子类（当前未在 main 中使用）

新增 Handler 步骤：

1. 在 `handlers/` 下新建 `xxx_handler.py`
2. 继承 `Base`，设置 `name = "xxx"`
3. 实现 `screen`、`move_to`、`left_click_at_point` 等必要方法
4. 工厂会自动发现，无需手动注册

### DAG 状态图（`dags/dag.py`）

| 类型 | 用途 |
|------|------|
| `Group` | 子图容器，支持嵌套；可用 `with group:` 切换上下文 |
| `Node` | 动作节点，`func(handler, hwnd) -> bool`；返回 `True` 表示成功并推进 |
| `Selector` | 条件边，放在 `>>` 前作为守卫条件 |

连接语法：

```python
group = Group(name="main")
with group as group:
    sub = Group(name="sub")
    a = Node("a", func_a)
    b = Node("b", func_b)
    group >> a >> sub >> b
```

- `>>`：从前驱连到后继
- 列表 `[node_a, node_b]`：并行分支，引擎选第一个满足条件的
- 节点函数签名统一为 `(handler, hwnd) -> bool`
- 模块必须导出 `dag` 或 `group` 变量（`main.py` 读取 `module.dag`）

参考实现：`dags/testcase/run.py`（使用 `Group`，可独立运行测试）。

### 图像识别流程

1. `handler.screen(filename)` 截图
2. `handler.find_assents(total, target_path, sens=0.8)` 模板匹配（基类已实现）
3. `cv_utils.diff_image` 使用 `cv2.matchTemplate` + 阈值 `sens`
4. 匹配成功后随机选取一个命中点，返回 `Point` 坐标

## 编码规范

修改代码时请遵循：

1. **最小改动**：只改与任务相关的文件，不顺带重构
2. **匹配现有风格**：中文注释、函数式 DAG 节点、Handler 继承 `Base`
3. **Windows 专用 API**：不要引入跨平台抽象，除非明确要求
4. **命名沿用现状**：即使存在拼写问题（如 `FIEL_PATH`、`find_assents`、`find_ellement_and_click`），修改时保持一致或在专门的重构任务中统一修正
5. **节点函数**：保持 `(handler, hwnd)` 签名，返回 `bool`；需要等待 UI 时用 `time.sleep`
6. **模板图片**：放在对应 DAG 的 `files/<PIX>/` 下，路径在代码中用相对字符串（如 `'buttons/start.png'`）
7. **不要提交**：`.env`、截图缓存（`**/**/screen.png`）、虚拟环境

## 常见任务

### 新增一个 DAG

1. 在 `dags/<category>/` 下创建模块，如 `my_game/task.py`
2. 定义节点函数和 `Group`/`Node`/`Selector` 图结构
3. 导出 `dag = Group(name="main")` 或确保 `main.py` 能访问 `module.dag`
4. 在 `files/<PIX>/` 下放置模板图片
5. `.env` 中设置 `DAG=my_game.task`

### 调试 DAG 逻辑（不依赖真实窗口）

直接运行测试 DAG：

```bash
pipenv run python -m dags.testcase.run
```

### 查找窗口 HWND

使用 `handlers/utils/hwnd_utils.py` 中的 `get_hwnd_list()` 列出可见窗口，或 `get_hwnd_with_name(name)` 按标题精确匹配。

## 已知问题与注意事项

AI 助手在修改代码前应了解以下现状：

1. **`DAG` vs `Group`**：`dags/dag.py` 只定义了 `Group`，但 `alipay/signin.py` 和 `Hearthstone_Mercenaries/one_one.py` 仍 import `DAG`（旧名），会导致 ImportError。应统一为 `Group`。
2. **`find_ellement_and_click` 未在 Handler 基类实现**：炉石示例 DAG 调用了此方法，但 `Base`/`PyAuto`/`BackEnd` 中不存在。需要补充实现或改用 `find_assents` + 点击组合。
3. **`main.py` 调用 `handler.get_hwnd()`**：当前 Handler 类未定义 `get_hwnd` 类方法；`BackEnd` 仅在实例方法 `start(name=...)` 中获取 HWND。
4. **`main.py` 期望 `module.dag`**：而 `testcase/run.py` 导出的是 `group` 不是 `dag`。
5. **`alipay/signin.py`**：引用了未定义的函数和 `DAG.copy()`（`Group.copy` 已被注释），属于未完成代码。
6. **`backend_handler.py` 的 `screen()`**：`cv2.imread(self.hwnd, filename)` 参数顺序有误。
7. **`path_utils.py`**：函数签名含 `self` 但未定义类，且未 import `os`/`core`。
8. **Pipfile 依赖为空**：实际依赖需从 import 推断并手动安装。

修复上述问题时，优先保持与 `dags/testcase/run.py` + `Group` 体系一致。

## 测试

项目当前 **没有** 自动化测试套件。验证方式：

- 运行 `dags/testcase/run.py` 检查状态图遍历逻辑
- 在目标游戏窗口可见时，用真实 `.env` 配置跑 `main.py`
- 调整模板匹配的 `sens` 阈值以适配不同截图条件

不要添加只断言恒真的 trivial 测试，除非用户明确要求。

## Git 与提交

- 仅在用户明确要求时创建 commit
- 不要提交 `.env` 或含密钥的文件
- 不要修改 git config，不要 force push

## 快速参考

```python
# 节点函数模板
def my_action(handler, hwnd):
    time.sleep(0.2)
    return handler.find_assents(...)  # 或自定义逻辑

# DAG 骨架
from dags.dag import Group, Node, Selector

dag = Group(name="main")
with dag as dag:
    start = Node("start", my_action)
    end = Node("end", lambda h, w: True)
    dag >> start >> end
```
