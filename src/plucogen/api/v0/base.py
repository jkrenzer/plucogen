from abc import abstractmethod, ABC
from dataclasses import dataclass
from .api import Interface as ApiI


class Interface(ABC, ApiI):
    @dataclass
    class InputData(ABC):
        pass

    @dataclass
    class OutputData(ABC):
        pass
