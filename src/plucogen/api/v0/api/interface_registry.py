import copy
from multiprocessing import Value
from os import PathLike
from dataclasses import dataclass
from inspect import isabstract, isclass
from types import ModuleType
from typing import Dict, List, Set, Union, Type


from pkg_resources import load_entry_point

from plucogen import api as _api
from plucogen.api.entrypoint import Entrypoints
from plucogen.api.v0 import _module_name
from plucogen.logging import getLogger

from .module_path import ModulePath


log = getLogger(__name__)


class InterfaceRegistry:
    forbidden_names: Set[str] = set("_forbidden")
    module: str = __name__
    interface: Union[Type["InterfaceBase"], None] = None
    entrypoints: Type[Entrypoints]
    path: ModulePath = ModulePath()
    _parent: Union[Type["InterfaceRegistry"], None] = None
    _children: List[Type["InterfaceRegistry"]] = list()

    _sub_apis: Dict[str, "InterfaceBase"] = dict()

    @classmethod
    def register_entry_points(cls) -> None:
        if cls.entrypoints is not None:
            for entry in cls.entrypoints.get():
                log.debug(
                    f"Found entrypoint {entry.name} reffering to interface {entry.value}"
                )
                interface: Type["InterfaceBase"] = entry.load()
                if not entry.name == interface.name:
                    log.warn(
                        f"Entrypoint name {entry.name} does not match declared interface name {interface.name} in {interface.__name__}! Skipping!"
                    )
                    continue
                else:
                    log.info(
                        f"Registering entrypoint api for {entry.name} with module {interface.module}"
                    )
                    cls.register_api(interface)
        for child in cls._children:
            child.register_entry_points()

    @classmethod
    def __new__(cls):
        assert isinstance(cls.forbidden_names, set)
        assert cls.interface is not None
        if cls.entrypoints is None:
            cls.entrypoints = _api.entrypoints.create_entrypoints(cls.module)
        cls.register_entry_points()
        return super.__new__(cls)

    @classmethod
    def module_available(cls, path: ModulePath | str) -> bool:
        from importlib.util import find_spec

        if isinstance(path, str):
            path = ModulePath(path)
        if find_spec(path.as_str) is None:
            return False
        else:
            return True

    @classmethod
    def assert_sane(cls, api_interface: Union["InterfaceBase", Type["InterfaceBase"]]):
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
            if not issubclass(api_interface, cls.interface or InterfaceBase):
                raise ImportError(
                    "Tried to import an API class with type {} into {}!".format(
                        api_interface.__name__, cls.__name__
                    ),
                    name=api_interface.name,
                )

            if not api_interface.module_available():
                raise ImportError(
                    f"Tried to import an API based on an non-existing or non-reachable module {module_name} !",
                    name=api_interface.name,
                )
        else:
            if not isinstance(api_interface, cls.interface or InterfaceBase):
                raise ImportError(
                    "Tried to import an API instance with type {} into {}!".format(
                        api_interface.__name__, cls.__name__
                    ),
                    name=api_interface.name,
                )

    @classmethod
    def import_module(cls, module: Union[ModulePath, ModuleType, str]):
        from importlib import import_module, invalidate_caches

        cls.register_entry_points()
        apis = cls.get_all_apis()

        name: str = ""
        if isinstance(module, ModuleType):
            name = module.__name__
        elif isinstance(module, ModulePath):
            name = str(module)
        elif isinstance(module, str):
            if module in apis:
                name = str(apis[module].module)
            else:
                name = module
        else:
            raise ImportError("Tried to import a non-module object into the API!")
        log.info("Importing module %s", name)
        result = import_module(name)
        invalidate_caches()
        log.debug("Imported module %s", name)
        return result

    @classmethod
    def register_api(cls, api_interface: "Union[InterfaceBase, Type[InterfaceBase]]"):
        cls.assert_sane(api_interface)
        name = api_interface.name

        if not name in cls.forbidden_names and not name in cls._sub_apis.keys():
            if name == "":
                name = api_interface.get_module_name()
            api_interface.registry = cls
            canonical_name = cls.get_canonical_name(name)
            cls._sub_apis[canonical_name] = api_interface
            log.debug(
                "Registered module %s with canonical name %s in %s",
                api_interface.get_module_name(),
                canonical_name,
                cls.__name__,
            )
        else:
            raise ImportError(
                "Tried to import an API with an already reserved or forbidden name!",
                name=name,
            )

    @classmethod
    def get_local_name(cls, name: str) -> str:
        lname = str(ModulePath(name).local_name())
        log.debug("Getting local name for %s as %s", name, lname)
        return lname

    @classmethod
    def get_canonical_name(cls, name: str) -> str:
        log.debug(
            "Get canonical name for %s with class %s parent path %s",
            name,
            cls.__name__,
            str(cls.path),
        )
        return str(cls.path + cls.get_local_name(name))

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
        if canonical_name in cls._sub_apis.keys():
            from importlib import invalidate_caches
            from sys import modules

            cls._sub_apis.pop(canonical_name)
            api_interface.registry = None
            invalidate_caches()
            log.debug(
                "Unregistered module %s with canonical name %s in %s",
                api_interface.get_module_name(),
                canonical_name,
                cls.__name__,
            )

    @classmethod
    def get_apis(cls):
        cls.register_entry_points()
        return copy.copy(cls._sub_apis)

    @classmethod
    def get_all_apis(cls) -> Dict[str, "InterfaceBase"]:
        cls.register_entry_points()
        child_sub_apis = dict()
        for child in cls._children:
            log.debug("Fetching APIs from %s", child.__name__)
            child_sub_apis.update(child._sub_apis)
        child_sub_apis.update(cls._sub_apis)
        return child_sub_apis

    @classmethod
    def get_registries(cls) -> Dict[ModulePath, "Type[InterfaceRegistry]"]:
        registries = {str(cls.path): cls}
        for child in cls._children:
            registries[str(child.path)] = child
            registries.update(child.get_registries())
        log.debug(f"Collected registries: {str(registries)}")
        return registries

    @classmethod
    def get_registry(
        cls, path: Union[ModulePath, str]
    ) -> Union[Type["InterfaceRegistry"], None]:
        if isinstance(path, str):
            path = ModulePath(path)
        return cls.get_registries().get(str(path), None)

    @classmethod
    def load_api_module(cls, canonical_name: str):
        from sys import modules

        api_interface = cls._sub_apis[canonical_name]
        log.info("Importing Module %s", canonical_name)
        module = cls.import_module(api_interface.module)
        local_name = cls.get_local_name(canonical_name)
        if canonical_name not in modules:
            from importlib import import_module, invalidate_caches

            modules[canonical_name] = module
            assert module is import_module(
                canonical_name
            )  # Working with the bones of the import system is dangerous so be very sure
            invalidate_caches()
            log.debug(
                "Imported module %s as %s (%s)",
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

    @classmethod
    def load_api_modules(cls):
        cls.register_entry_points()
        for canonical_name, _ in cls._sub_apis.items():
            cls.load_api_module(canonical_name=canonical_name)

    @classmethod
    def get_interface_registry_name(cls, module: str) -> str:
        return (ModulePath(module) + "Registry").upperCamelCase()

    @classmethod
    def is_available(cls, name: str) -> bool:
        canonical_name = cls.get_canonical_name(name)
        local_name = cls.get_local_name(name)
        log.debug(
            "Checking availability of API module %s (%s)", local_name, canonical_name
        )
        return (
            canonical_name in cls._sub_apis
            and cls._sub_apis[canonical_name].module_available()
        )

    @classmethod
    def when_available(cls, name: str):
        """Decorator to ensure object is only defined when the api is available"""
        if cls.is_available(name):
            return lambda f: f

    @classmethod
    def create_interface_registry(
        cls,
        InterfaceT,
        module: str,
        path: Union[ModulePath, str] = "",
        forbidden_names: Set[str] = set(),
    ) -> Type["InterfaceRegistry"]:
        name = InterfaceT.name or ModulePath(module).local_name()
        path = path or cls.path + name

        from .interface_base import InterfaceBase

        interface = cls.interface or InterfaceBase
        I = interface.create_interface(module=module, name=str(name), registry=cls)
        cls.register_api(I)
        R = type(
            cls.get_interface_registry_name(module),
            (cls,),
            {
                "interface": InterfaceT,
                "module": module,
                "path": path,
                "_parent": cls,
                "entrypoints": _api.entrypoints.create_entrypoints(module),
                "_children": list(),
                "forbidden_names": forbidden_names,
                "_sub_apis": dict(),
            },
        )
        cls._children.append(R)

        log.debug(
            "Created new registry %s for module %s at path %s",
            R.__name__,
            module,
            str(path),
        )

        def reg(c, module: str = None):
            log.debug(
                "%s registered with %s in %s with the alias %s",
                c.__name__,
                R.__name__,
                c.module,
                c.name,
            )
            if isinstance(module, (str, ModuleType)):
                c.module = module
            c.Registry.register_api(c)

        InterfaceT.register = classmethod(reg)
        InterfaceT.Registry = R
        return R


from .interface_base import InterfaceBase
