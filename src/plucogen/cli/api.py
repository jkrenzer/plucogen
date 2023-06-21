from abc import abstractmethod
from plucogen.api.v0 import api as _api


class Interface(_api.InterfaceBase):
    from .parser import subParsers


Registry = _api.get_interface_registry(
    InterfaceT=Interface, module=__name__, forbidden_names=set()
)

entrypoints = _api.entrypoints.create_entrypoints("cli")
