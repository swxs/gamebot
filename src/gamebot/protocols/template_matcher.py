from typing import Optional, Protocol, runtime_checkable

import numpy as np

from gamebot.protocols.types import MatchResult, Rect


@runtime_checkable
class TemplateMatcher(Protocol):
    def find(
        self,
        screen: np.ndarray,
        template_path: str,
        sens: float = 0.8,
        region: Optional[Rect] = None,
    ) -> Optional[MatchResult]: ...

    def find_all(
        self,
        screen: np.ndarray,
        template_path: str,
        sens: float = 0.8,
        region: Optional[Rect] = None,
    ) -> list[MatchResult]: ...

    def wait(
        self,
        capture,
        template_path: str,
        sens: float = 0.8,
        timeout: float = 10,
        interval: float = 0.5,
        region: Optional[Rect] = None,
    ) -> Optional[MatchResult]: ...
