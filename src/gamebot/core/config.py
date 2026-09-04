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
