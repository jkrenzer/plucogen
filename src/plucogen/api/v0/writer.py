from abc import ABC
from dataclasses import dataclass
from .base import BaseInterface

class Interface(BaseInterface, ABC):
   
    from .generator import Interface as GeneratorInterface
    InputData = GeneratorInterface.OutputData

    @dataclass
    class OutputData:
        return_code: int
