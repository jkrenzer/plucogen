from dataclasses import dataclass
from typing import List, Dict, Union, Set
from types import ModuleType
from plucogen.logging import getLogger
from inspect import isclass, isabstract

log = getLogger(__name__)


@dataclass
class Interface:
    module: ModuleType
    name: str


class InterfaceRegistry:
    forbidden_names: Set[str] = set("_forbidden")
    module_path: str = __name__
    interface = Interface

    _sub_apis: Dict = {}

    def __new__(cls):
        assert isinstance(cls.forbidden_names, set)
        assert cls.interface is not None
        return super.__new__(cls)

    @classmethod
    def assert_sane(cls, api_interface: Interface):
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
    def register_api(cls, api_interface: "Interface"):
        cls.assert_sane(api_interface)
        name = api_interface.name
        if not name in cls.forbidden_names and not name in cls._sub_apis.keys():
            from sys import modules

            cls._sub_apis[name] = api_interface
            module = cls.get_module(api_interface.module)
            globals()[name] = module
            new_name = cls.module + "." + name
            log.debug("Registered module %s as %s", module.__name__, new_name)
            modules[new_name] = module
        else:
            raise ImportError(
                "Tried to import an API with an already reserved or forbidden name!",
                name=name,
            )

    @classmethod
    def unregister_api(cls, api_interface: "Interface"):
        cls.assert_sane(api_interface)
        name = api_interface.name
        if name in cls._sub_apis.keys():
            from sys import modules

            cls._sub_apis.pop(name)
            del globals()[name]
            new_name = cls.module + "." + name
            del modules[new_name]

    @classmethod
    def get_apis(cls):
        return cls._sub_apis.copy()


def get_interface_registry(InterfaceT, module: str, forbidden_names: Set[str]):
    R = type(
        InterfaceT.__name__ + "Registry",
        (InterfaceRegistry,),
        {
            "interface": InterfaceT,
            "module": module,
            "forbidden_names": forbidden_names,
        },
    )
    InterfaceT.register = classmethod(lambda cls: R.register_api(cls))
    return R
