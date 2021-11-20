import os
from .config import *

SITE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIEL_PATH = os.path.join(SITE_ROOT, "dags", BOT_HOME, "files", PIX)
