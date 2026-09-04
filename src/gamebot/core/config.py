from environs import Env

env = Env()
env.read_env()

# 窗口句柄名称
NAME = env.str("NAME", None)

# 0, 无限次运行
# 1~, 指定次数运行
NUMBER = env.int("NUMBER", 0)

# testcase.pyauto_run / testcase.backend_run
DAG = env.str("DAG", "testcase.pyauto_run")

# 1920x1080_CN
PIX = env.str("PIX", "")

# dashboard HTTP 端口，默认 8765
DASHBOARD_PORT = env.int("DASHBOARD_PORT", 8765)

# 1 = CLI 启动时自动打开浏览器
DASHBOARD_OPEN = env.bool("DASHBOARD_OPEN", False)
