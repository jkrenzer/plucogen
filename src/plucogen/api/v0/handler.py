from abc import ABC, abstractmethod
from dataclasses import dataclass

from plucogen.api.v0.api import create_interface_registry

from .base import Interface as _Interface


class Interface(_Interface):
    from .consumer import Interface as ConsumerInterface

    InputData = ConsumerInterface.OutputData
    OutputData = ConsumerInterface.OutputData

    @classmethod
    @abstractmethod
    def handle(cls, input: InputData) -> OutputData:
        pass


Registry = create_interface_registry(
    InterfaceT=Interface, module=__name__, forbidden_names=set()
)
