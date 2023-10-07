import os
import core
from commons.Helper_productor import Productor
from .dag import Group


base_path = os.path.dirname(os.path.abspath(__file__))
dag_productor = Productor(core.path.SITE_ROOT, base_path, Group, Group, "*.py")
