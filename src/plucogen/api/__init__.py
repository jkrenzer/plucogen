from dataclasses import dataclass

from plucogen.logging import getLogger

from .entrypoint import Entrypoints

log = getLogger(__name__)


@dataclass
class ApiInformation:
    version: int


_module_name = __name__

entrypoints = Entrypoints.create_entrypoints(_module_name)

from . import v0
