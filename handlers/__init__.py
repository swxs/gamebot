import os
import core
from commons.Helper_productor import Productor
from .base_handler import Base


class HandlerProductor(Productor):
    def __init__(
            self,
            base_module: object,
            start_dir: object,
            pattern: object = '*.py',
            top_level_dir: object = None,
            temp_module: object = None
    ):
        super().__init__(base_module, start_dir, pattern=pattern, top_level_dir=top_level_dir, temp_module=temp_module)
        self.root_dir = core.SITE_ROOT


base_path = os.path.join(core.SITE_ROOT, "handlers")
handler_productor = HandlerProductor(Base, base_path, "*.py", temp_module=Base)
