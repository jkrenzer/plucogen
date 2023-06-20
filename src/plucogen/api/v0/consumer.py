from abc import abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Union
from .base import Interface as BaseInterface
from .api import get_interface_registry
from argparse import Namespace
from pathlib import Path
from urllib.parse import ParseResult as Url


class Interface(BaseInterface):
    @dataclass
    class InputData:
        options: Namespace
        resources: List[Union[Path, Url]]

    @dataclass
    class OutputData:
        options: Namespace
        data: Union[Dict, List]

    @classmethod
    @abstractmethod
    def consume(input: InputData) -> OutputData:
        pass


Registry = get_interface_registry(
    InterfaceT=Interface, module=__name__, forbidden_names=set()
)
