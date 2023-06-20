from abc import ABC
from dataclasses import dataclass
from typing import Dict, List, Union
from .base import Interface as BaseInterface
from argparse import Namespace


class Interface(BaseInterface, ABC):
    
    from .reader import Interface as ReaderInterface
    InputData = ReaderInterface.OutputData

    @dataclass
    class OutputData:
        options: Namespace
        data: Union[Dict, List]
