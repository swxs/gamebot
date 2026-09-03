from gamebot.handlers import handler_productor
from gamebot.handlers.base_handler import Base


def test_handler_productor_discovers_handlers():
    assert issubclass(handler_productor["pyauto"], Base)
    assert issubclass(handler_productor["backend"], Base)
    assert issubclass(handler_productor["frontend"], Base)
    assert handler_productor["pyauto"].name == "pyauto"
