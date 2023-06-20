from abc import abstractmethod, ABC
from dataclasses import dataclass

class Interface(ABC):

    @dataclass
    class InputData(ABC):
        pass

    @dataclass
    class OutputData(ABC):
        pass
    
    @abstractmethod
    def main(input: InputData) -> OutputData:
        pass