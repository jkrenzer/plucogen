from abc import abstractmethod
from dataclasses import dataclass
from .base import Interface as BaseInterface
from plucogen.api.v0.api import get_interface_registry, InterfaceBase as _ApiI


@dataclass
class _ApiInterface(_ApiI):
    name = ""
    module = __name__


_ApiInterface.register()


class Interface(BaseInterface):
    from .generator import Interface as GeneratorInterface

    InputData = GeneratorInterface.OutputData

    OutputData = BaseInterface.OutputData

    @classmethod
    @abstractmethod
    def write(input: InputData) -> OutputData:
        pass


Registry = get_interface_registry(
    InterfaceT=Interface, module=__name__, forbidden_names=set()
)
