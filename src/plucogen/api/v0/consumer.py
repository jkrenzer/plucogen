from abc import abstractmethod
from argparse import Namespace
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Union
from urllib.parse import ParseResult as Url

from plucogen.api.v0.api import InterfaceBase as _ApiI
from plucogen.api.v0.api import Registry as _ApiR
from plucogen.api.v0.api import get_interface_registry
from plucogen.logging import getLogger

from .base import DataList
from .base import Interface as BaseInterface

log = getLogger(__name__)


@dataclass
class _ApiInterface(_ApiI):
    name = "consumer"
    module = __name__


_ApiInterface.register()


class Interface(BaseInterface):
    """
    Interface for consumers, which consume resources and
    output a data object with information derived from the
    consumed resources, e.g. files.
    """

    name = "consumer"
    module = __name__

    @dataclass
    class InputData(BaseInterface.InputData):
        """
        Consumer input data are pointers to resources, e.g.
        paths to files or URLs.
        """

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
    InterfaceT=_ApiInterface, module=__name__, forbidden_names=set()
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
