from dataclasses import dataclass
from plucogen.api.v0.api import InterfaceBase as _ApiI


@dataclass
class Interface(_ApiI):
    name = "cli"
    module = __name__


Interface.register()

from . import api
from . import parser
from .__main__ import main
