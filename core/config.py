from environs import Env

env = Env()
env.read_env()

# 窗口句柄名称
NAME = env.str("NAME", None)

# 0, 无限次运行
# 1~, 指定次数运行
NUMBER = env.int("NUMBER", 0)

# frontend 需要窗口可见
# pyauto 需要窗口可见
# backend 不需要窗口可见
HANDLER = env.str("HANDLER", "pyauto")

# testcase.run
# Hearthstone_Mercenaries.one_one
# alipay.signin
DAG = env.str("DAG", "test")

# 1920x1080_CN
PIX = env.str("PIX", "")
