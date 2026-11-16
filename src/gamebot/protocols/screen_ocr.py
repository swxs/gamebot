from typing import Optional, Protocol, runtime_checkable

import numpy as np

from gamebot.protocols.types import OcrHit


@runtime_checkable
class ScreenOcr(Protocol):
    def read(self, image: np.ndarray) -> list[OcrHit]: ...

    def find_text(self, image: np.ndarray, text: str) -> Optional[OcrHit]: ...
