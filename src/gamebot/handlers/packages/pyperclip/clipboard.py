import pyperclip


class PyperclipHandler:

    def read(self) -> str:
        return pyperclip.paste()

    def write(self, text: str) -> bool:
        pyperclip.copy(text)
        return True
