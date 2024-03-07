from abc import abstractmethod
from argparse import Namespace
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Union
from urllib.parse import ParseResult as Url

from plucogen.api.v0.api import create_interface_registry
from plucogen.logging import getLogger

from .base import DataList
from .base import Interface as _Interface

log = getLogger(__name__)


class Interface(_Interface):
    """
    Interface for consumers, which consume resources and
    output a data object with information derived from the
    consumed resources, e.g. files.
    """

    name = "consumer"
    module = __name__

    @dataclass
    class InputData(_Interface.InputData):
        """
        Consumer input data are pointers to resources, e.g.
        paths to files or URLs.
        """

        resources: List[Union[Path, Url]]

    @dataclass
    class OutputData(_Interface.OutputData):
        data: DataList
        Data = DataList

    @classmethod
    @abstractmethod
    def consume(input: InputData) -> OutputData:
        pass


Registry = create_interface_registry(
    InterfaceT=Interface, module=__name__, forbidden_names=set()
)

# if _ApiInterface.registry.is_available("cli"):
#     log.debug("Activaing CLI integration for consumers")
#     from plucogen.api.v0.cli.api import Interface as _CliI

#     class CliInterface(_CliI):
#         pass

#     CliInterface.subParsers.add_parser(
#         "consume", help="Consume resources and input the data", aliases="co"
#     )

#     CliInterface.register()
