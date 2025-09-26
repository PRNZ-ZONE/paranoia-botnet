from abc import ABC

from rich.console import Console
from rich.prompt import Prompt


class BaseFunction(ABC):
    def __init__(self):
        self.console = Console(color_system="auto")
        self.prompt = Prompt(console=self.console)
        self.sessions_count = 0

    @property
    def __name__(self):
        return self.__class__.__name__ + "_Function"


__all__ = ["BaseFunction"]
