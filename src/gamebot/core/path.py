import os
from .config import *

# repo 根目录（pyproject.toml 所在位置）
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
SRC_ROOT = os.path.join(PROJECT_ROOT, "src")
SITE_ROOT = PROJECT_ROOT
FIEL_PATH = os.path.join(SITE_ROOT, "dags", DAG, "files", PIX)
