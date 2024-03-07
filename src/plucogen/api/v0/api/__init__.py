from plucogen import api as _api
from plucogen.api.v0 import _module_name
from plucogen.logging import getLogger

from .interface_base import InterfaceBase
from .interface_registry import InterfaceRegistry
from .module_path import ModulePath

log = getLogger(__name__)

information = _api.ApiInformation(version=0)


Registry = InterfaceRegistry.create_interface_registry(
    InterfaceT=InterfaceBase,
    module=_module_name,
    path=ModulePath("plucogen.v0"),
    forbidden_names=set("__strictly_prohibited__"),
)

entrypoints = Registry.entrypoints
create_interface_registry = Registry.create_interface_registry
register_api = Registry.register_api
unregister_api = Registry.unregister_api
get_apis = Registry.get_apis
import_module = Registry.import_module
