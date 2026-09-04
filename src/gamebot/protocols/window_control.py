from typing import Protocol, runtime_checkable


@runtime_checkable
class WindowControl(Protocol):
    def focus(self) -> bool: ...

    def restore(self) -> bool: ...

    def minimize(self) -> bool: ...
