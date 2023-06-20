from abc import ABC
from dataclasses import dataclass
from .base import Interface as BaseInterface
from argparse import Namespace


class Interface(BaseInterface, ABC):
   
    from .consumer import Interface as ConsumerInterface
    InputData = ConsumerInterface.OutputData

    @dataclass
    class OutputData:
        options: Namespace
        code: str
