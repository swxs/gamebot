from typing import Protocol, runtime_checkable


@runtime_checkable
class ControlTree(Protocol):
    def read_tree(self) -> str: ...
