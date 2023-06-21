from abc import ABC, abstractmethod
from dataclasses import dataclass
from .base import Interface as BaseInterface
from plucogen.api.v0.api import get_interface_registry, InterfaceBase as _ApiI
from argparse import Namespace


@dataclass
class _ApiInterface(_ApiI):
    name = ""
    module = __name__


_ApiInterface.register()


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


Registry = get_interface_registry(
    InterfaceT=Interface, module=__name__, forbidden_names=set()
)
