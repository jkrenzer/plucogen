from abc import ABC
from dataclasses import dataclass
from .base import BaseInterface
from argparse import Namespace
from typing import List, Union
from pathlib import Path
from urllib.parse import ParseResult as Url


class Interface(BaseInterface, ABC):
   
    @dataclass
    class OutputData:
        options: Namespace
        resources: List[Union[Path,Url]]

    @dataclass
    class InputData:
        options: Namespace
