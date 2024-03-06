from abc import ABC, abstractmethod
from argparse import Namespace
from dataclasses import dataclass

from plucogen.api.v0.api import create_interface_registry

from .base import Interface as BaseInterface


class Interface(BaseInterface):
    from .consumer import Interface as ConsumerInterface

    InputData = ConsumerInterface.OutputData

    @dataclass
    class OutputData(BaseInterface.OutputData):
        code: str

    @classmethod
    @abstractmethod
    def generate(cls, input: InputData) -> OutputData:
        pass


Registry = create_interface_registry(
    InterfaceT=Interface, module=__name__, forbidden_names=set()
)
