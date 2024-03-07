from abc import abstractmethod
from typing import Union

from typer import Typer

from plucogen.api.v0.api import create_interface_registry
from plucogen.logging import getLogger

from .base import Interface as _Interface

log = getLogger(__name__)


class Interface(_Interface):
    """
    Interface for cli options and arguments
    presented to the user
    """

    name = "cli"
    module = __name__

    def __init_subclass__(cls, *args, **kwargs):
        if not hasattr(cls, "app") or not isinstance(cls.app, Typer):
            raise NotImplementedError(
                "Class attribute 'app' must be set to a Typer instance!"
            )


Registry = create_interface_registry(
    InterfaceT=Interface, module=__name__, forbidden_names=set()
)
