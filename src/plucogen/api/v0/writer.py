from abc import abstractmethod
from dataclasses import dataclass

from plucogen.api.v0.api import InterfaceBase as _ApiI
from plucogen.api.v0.api import create_interface_registry

from .base import Interface as _Interface


@dataclass
class _ApiInterface(_ApiI):
    name = ""
    module = __name__


_ApiInterface.register()


class Interface(_Interface):
    from .generator import Interface as GeneratorInterface

    InputData = GeneratorInterface.OutputData

    OutputData = _Interface.OutputData

    @classmethod
    @abstractmethod
    def write(cls, input: InputData) -> OutputData:
        pass


Registry = create_interface_registry(
    InterfaceT=Interface, module=__name__, forbidden_names=set()
)


class Test(Interface):
    name = "Testy"
    module = __name__

    @classmethod
    def write(cls, input: Interface.InputData) -> Interface.OutputData:
        pass


Test.register()
