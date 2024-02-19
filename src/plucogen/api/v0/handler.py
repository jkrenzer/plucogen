from abc import ABC, abstractmethod
from dataclasses import dataclass

from plucogen.api.v0.api import InterfaceBase as _ApiI
from plucogen.api.v0.api import get_interface_registry

from .base import Interface as BaseInterface


@dataclass
class _ApiInterface(_ApiI):
    name = ""
    module = __name__


_ApiInterface.register()


class Interface(BaseInterface):
    from .consumer import Interface as ConsumerInterface

    InputData = ConsumerInterface.OutputData
    OutputData = ConsumerInterface.OutputData

    @classmethod
    @abstractmethod
    def handle(cls, input: InputData) -> OutputData:
        pass


Registry = get_interface_registry(
    InterfaceT=Interface, module=__name__, forbidden_names=set()
)
