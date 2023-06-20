from plucogen.api import ApiInformation
from plucogen.logging import getLogger
from .api import Interface as ApiInterface
from typing import Dict, Union
from types import ModuleType

log = getLogger(__name__)

api_information = ApiInformation(version=0)

_forbidden_names = set("_forbidden")
_sub_apis: Dict = {}


def assert_version(api_interface: ApiInterface):
    if not isinstance(api_interface, ApiInterface):
        raise ImportError(
            "Tried to import an API with the wrong interface version!",
            name=api_interface.name,
        )


def get_module(module: Union[str, ModuleType]):
    from importlib import import_module, invalidate_caches

    name = ""
    if isinstance(module, ModuleType):
        name = module.__name__
    elif isinstance(module, str):
        name = module
    else:
        raise ImportError("Tried to import a non-module object into the API!")
    result = import_module(name)
    invalidate_caches()
    log.debug("Imported module %s", name)
    return result


def register_api(api_interface: ApiInterface):
    assert_version(api_interface)
    name = api_interface.name
    if not name in _forbidden_names and not name in _sub_apis.keys():
        from sys import modules

        _sub_apis[name] = api_interface
        module = get_module(api_interface.module)
        globals()[name] = module
        new_name = __name__ + "." + name
        log.debug("Registered module %s as %s", module.__name__, new_name)
        modules[new_name] = module
    else:
        raise ImportError(
            "Tried to import an API with an already reserved or forbidden name!",
            name=name,
        )


def unregister_api(api_interface: ApiInterface):
    assert_version(api_interface)
    name = api_interface.name
    if name in _sub_apis.keys():
        from sys import modules

        _sub_apis.pop(name)
        del globals()[name]
        new_name = __name__ + "." + name
        del modules[new_name]


def get_apis():
    return _sub_apis.copy()
