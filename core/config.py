from environs import Env

env = Env()
env.read_env()

HANDLER = env.str("HANDLER", "pyauto")
DAG = env.str("DAG", "test")
