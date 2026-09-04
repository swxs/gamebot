from typing import Optional, Protocol, runtime_checkable

import numpy as np

from gamebot.protocols.types import MatchResult


@runtime_checkable
class TemplateMatcher(Protocol):
    def find(
        self,
        screen: np.ndarray,
        template_path: str,
        sens: float = 0.8,
    ) -> Optional[MatchResult]: ...
