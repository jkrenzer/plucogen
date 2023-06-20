from dataclasses import dataclass
from typing import List
from types import ModuleType


@dataclass
class Interface:
    module: ModuleType
    name: str
