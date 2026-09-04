import os
from .config import *

# repo 根目录（pyproject.toml 所在位置）
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
SRC_ROOT = os.path.join(PROJECT_ROOT, "src")
SITE_ROOT = PROJECT_ROOT


def dag_files_dir(category: str, pix: str = "") -> str:
    """模板图目录：dags/<category>/files/<pix>/"""
    base = os.path.join(SITE_ROOT, "dags", category, "files")
    if pix:
        return os.path.join(base, pix)
    return base


# 兼容旧拼写；新代码请用 dag_files_dir
FIEL_PATH = dag_files_dir(DAG.split(".")[0], PIX)
