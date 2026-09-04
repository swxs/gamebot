from typing import Protocol, runtime_checkable


@runtime_checkable
class KeyboardInput(Protocol):
    def press(self, key: str) -> bool: ...

    def type_text(self, text: str) -> bool: ...
