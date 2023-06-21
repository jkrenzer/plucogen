from dataclasses import dataclass
from typing import List, Dict, Union, Set
from types import ModuleType
from plucogen.logging import getLogger
from inspect import isclass, isabstract

from plucogen import api as _api
from plucogen.api.v0 import _module_name

log = getLogger(__name__)


@dataclass
class InterfaceBase:
    module: Union[ModuleType, str]
    name: str
    registry: "InterfaceRegistry" = None

    @classmethod
    def get_interface(
        cls,
        module: Union[ModuleType, str],
        name: str,
        registry: "InterfaceRegistry" = None,
    ):
        name = name.split(".")[0]
        return type(
            name.capitalize() + "Interface",
            (cls,),
            {
                "name": name,
                "module": module,
                "registry": registry,
            },
        )


class InterfaceRegistry:
    forbidden_names: Set[str] = set("_forbidden")
    module_path: str = __name__
    interface = InterfaceBase

    _sub_apis: Dict = {}

    def __new__(cls):
        assert isinstance(cls.forbidden_names, set)
        assert cls.interface is not None
        return super.__new__(cls)

    @classmethod
    def assert_sane(cls, api_interface: InterfaceBase):
        if isclass(api_interface):
            if isabstract(api_interface):
                try:
                    api_interface()  # Do your homework already!
                except:
                    raise ImportError(
                        "Tried to import an abstract API class with type {} into {}!".format(
                            api_interface.__name__, cls.__name__
                        ),
                        name=api_interface.name,
                    )
            if not issubclass(api_interface, cls.interface):
                raise ImportError(
                    "Tried to import an API class with type {} into {}!".format(
                        api_interface.__name__, cls.__name__
                    ),
                    name=api_interface.name,
                )
        else:
            if not isinstance(api_interface, cls.interface):
                raise ImportError(
                    "Tried to import an API instance with type {} into {}!".format(
                        api_interface.__name__, cls.__name__
                    ),
                    name=api_interface.name,
                )

    @classmethod
    def get_module(cls, module: Union[str, ModuleType]):
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

    @classmethod
    def register_api(cls, api_interface: "InterfaceBase"):
        cls.assert_sane(api_interface)
        name = api_interface.name
        if not name in cls.forbidden_names and not name in cls._sub_apis.keys():
            from sys import modules

            module = cls.get_module(api_interface.module)
            if name == "":
                name = module.__name__
            local_name = cls.get_local_name(name)
            cls._sub_apis[local_name] = api_interface
            api_interface.registry = cls
            canonical_name = cls.get_canonical_name(name)
            if canonical_name not in modules:
                from importlib import import_module, invalidate_caches

                modules[canonical_name] = module
                assert module is import_module(
                    canonical_name
                )  # Working with the bones of the import system is dangerous so be very sure
                invalidate_caches()
                log.debug(
                    "Registered module %s as %s (%s)",
                    module.__name__,
                    local_name,
                    canonical_name,
                )
            else:
                log.debug(
                    "Registered already imported module as %s (%s)",
                    local_name,
                    canonical_name,
                )
        else:
            raise ImportError(
                "Tried to import an API with an already reserved or forbidden name!",
                name=local_name,
            )

    @classmethod
    def get_canonical_name(cls, name: str) -> str:
        if name.startswith(cls.module):
            return name
        else:
            return cls.module + "." + name

    @classmethod
    def get_local_name(cls, name: str) -> str:
        return name.removeprefix(cls.module + ".")

    @classmethod
    def get_interface(cls, name: str, *args, **kwargs) -> interface:
        if len(args) or len(kwargs):
            default = args[0] or kwargs["default"]
            return cls._sub_apis.get(name, default)
        else:
            return cls._sub_apis[name]

    @classmethod
    def unregister_api(cls, api_interface: "InterfaceBase"):
        cls.assert_sane(api_interface)
        name = api_interface.name
        canonical_name = cls.get_canonical_name(name)
        local_name = cls.get_local_name(name)
        if local_name in cls._sub_apis.keys():
            from sys import modules
            from importlib import invalidate_caches

            cls._sub_apis.pop(name)
            api_interface.registry = None
            canonical_name = cls.get_canonical_name(name)
            del modules[canonical_name]
            invalidate_caches()
            log.debug("Unregistered module %s", canonical_name)

    @classmethod
    def get_apis(cls):
        return cls._sub_apis.copy()

    @classmethod
    def is_available(cls, name: str) -> bool:
        from sys import modules

        canonical_name = cls.get_canonical_name(name)
        local_name = cls.get_local_name(name)
        log.debug(
            "Checking availability of API module %s (%s)", local_name, canonical_name
        )
        return local_name in cls._sub_apis and canonical_name in modules

    @classmethod
    def when_available(cls, name: str):
        """Decorator to ensure object is only defined when the api is available"""
        if cls.is_available(name):
            return lambda f: f

    @classmethod
    def get_interface_registry(cls, InterfaceT, module: str, forbidden_names: Set[str]):
        R = type(
            InterfaceT.__name__ + "Registry",
            (cls,),
            {
                "interface": InterfaceT,
                "module": module,
                "forbidden_names": forbidden_names,
            },
        )

        def reg(cls, module: str = None):
            if isinstance(module, (str, ModuleType)):
                cls.module = module
            R.register_api(cls)

        InterfaceT.register = classmethod(reg)
        return R


information = _api.ApiInformation(version=0)

entrypoints = _api.entrypoints.create_entrypoints(_module_name)

Registry = InterfaceRegistry.get_interface_registry(
    InterfaceT=InterfaceBase,
    module=_module_name,
    forbidden_names=set("__strictly_prohibited__"),
)

get_interface_registry = Registry.get_interface_registry
register_api = Registry.register_api
unregister_api = Registry.unregister_api
get_apis = Registry.get_apis
