from plucogen.api import ApiInformation
from plucogen.logging import getLogger
from .api import get_interface_registry, Interface
from typing import Dict, Union
from types import ModuleType

log = getLogger(__name__)

api_information = ApiInformation(version=0)


Registry = get_interface_registry(
    InterfaceT=Interface,
    module=__name__,
    forbidden_names=set("__strictly_prohibited__"),
)


register_api = Registry.register_api
unregister_api = Registry.unregister_api
get_apis = Registry.get_apis
