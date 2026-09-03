import os

from gamebot import core
from gamebot.commons.Helper_productor import Productor
from .base_handler import Base

base_path = os.path.dirname(os.path.abspath(__file__))
handler_productor = Productor(core.SRC_ROOT, base_path, Base, Base, "*.py")
