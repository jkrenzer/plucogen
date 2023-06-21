from abc import abstractmethod, ABC
from dataclasses import dataclass, field
from .api import InterfaceBase as _ApiI
from typing import List
from collections.abc import Iterable
from argparse import Namespace


@dataclass
class Message:
    text: str
    sender: str

    @classmethod
    def create(cls, text: str, sender: str = __name__):
        return cls(text=text, sender=sender)


class DataList(list):
    def valid_index(self, index: int):
        return len(self) > index and index > 0

    def get(self, index: int = 0, default=None):
        if self.valid_index(index):
            return self[index]
        else:
            return default

    def require(self, index: int = 0, message: str = "Required data not provided!"):
        if self.valid_index(index):
            return self[index]
        else:
            IndexError(message)

    def __init__(self, *args):
        if len(args) == 1 and isinstance(args, Iterable) and not isinstance(args, str):
            return super().__init__(args[0])
        else:
            return super().__init__([*args])

    def set(self, value, index: int = 0):
        if self.valid_index(index):
            self[index] = value


class Interface(ABC, _ApiI):
    @dataclass
    class InputData:
        options: Namespace
        return_code: int
        messages: List[Message]

    OutputData = InputData
