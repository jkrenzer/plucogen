from abc import abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Union
from .base import Interface as BaseInterface, DataList
from plucogen.logging import getLogger
from plucogen.api.v0.api import (
    get_interface_registry,
    InterfaceBase as _ApiI,
    Registry as _ApiR,
)
from argparse import Namespace
from pathlib import Path
from urllib.parse import ParseResult as Url

log = getLogger(__name__)


@dataclass
class _ApiInterface(_ApiI):
    name = "consumer"
    module = __name__


_ApiInterface.register()


class Interface(BaseInterface):
    @dataclass
    class InputData(BaseInterface.InputData):
        resources: List[Union[Path, Url]]

    @dataclass
    class OutputData(BaseInterface.OutputData):
        data: DataList
        Data = DataList

    @classmethod
    @abstractmethod
    def consume(input: InputData) -> OutputData:
        pass


Registry = get_interface_registry(
    InterfaceT=Interface, module=__name__, forbidden_names=set()
)

if _ApiInterface.registry.is_available("cli"):
    log.debug("Activaing CLI integration for consumers")
    from plucogen.api.v0.cli.api import Interface as _CliI

    class CliInterface(_CliI):
        pass

    CliInterface.subParsers.add_parser(
        "consume", help="Consume resources and input the data", aliases="co"
    )

    CliInterface.register()
