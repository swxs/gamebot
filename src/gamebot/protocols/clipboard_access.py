from typing import Protocol, runtime_checkable


@runtime_checkable
class ClipboardAccess(Protocol):
    def read(self) -> str: ...

    def write(self, text: str) -> bool: ...
