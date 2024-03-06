from abc import abstractmethod
from typer import Typer

from plucogen.api.v0.api import create_interface_registry
from plucogen.logging import getLogger

from .base import Interface as BaseInterface

log = getLogger(__name__)


class Interface(BaseInterface):
    """
    Interface for cli options and arguments
    presented to the user
    """

    name = "cli"
    module = __name__
    app: Typer = Typer()

    @classmethod
    def run(cls) -> int:
        return cls.app()


Registry = create_interface_registry(
    InterfaceT=Interface, module=__name__, forbidden_names=set()
)
