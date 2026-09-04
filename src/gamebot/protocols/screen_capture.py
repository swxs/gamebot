from typing import Protocol, runtime_checkable

import numpy as np


@runtime_checkable
class ScreenCapture(Protocol):
    def capture(self) -> np.ndarray: ...
