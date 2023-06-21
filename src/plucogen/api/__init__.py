from dataclasses import dataclass
from .entrypoint import Entrypoints

from plucogen.logging import getLogger

log = getLogger(__name__)


@dataclass
class ApiInformation:
    version: int


_module_name = __name__

entrypoints = Entrypoints.create_entrypoints(_module_name)

from . import v0
