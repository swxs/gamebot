import os
import core
from commons.Helper_productor import Productor
from .dag import DAG

class DagProductor(Productor):
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


base_path = os.path.join(core.SITE_ROOT, "dags")
dag_productor = DagProductor(DAG, base_path, "*.py", temp_module=DAG)
