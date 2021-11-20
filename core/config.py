from environs import Env

env = Env()
env.read_env()

HANDLER = env.str("HANDLER", "pyauto")
DAG = env.str("DAG", "test")
BOT_HOME = env.str("BOT_HOME", "")
BOT = env.str("BOT", "")
PIX = env.str("PIX", "")
