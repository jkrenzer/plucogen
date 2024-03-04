import copy
from multiprocessing import Value
from os import PathLike
from dataclasses import dataclass
from inspect import isabstract, isclass
from types import ModuleType
from typing import Dict, List, Set, Union, Type
from itertools import zip_longest

from plucogen import api as _api
from plucogen.api.v0 import _module_name
from plucogen.logging import getLogger

log = getLogger(__name__)


class ModulePath(object):
    separator: str = "."

    @classmethod
    def _enforce_absolute(cls, path: List[str]) -> List[str]:
        return list(filter(None, path))

    @classmethod
    def _enforce_relative(cls, path: List[str], level=1) -> List[str]:
        return ["" for n in range(level)] + cls._enforce_absolute(path)

    @classmethod
    def _rectify(cls, path: List[str]) -> List[str]:
        path = list(path)
        return path[:1] + cls._enforce_absolute(path[1:])

    @classmethod
    def split_str(cls, string: str) -> List[str]:
        raw_result: List[str] = string.split(cls.separator)
        return cls._rectify(raw_result)

    def relative(self) -> bool:
        return self._path[:1] == [""]

    def absolute(self) -> bool:
        return not self.relative()

    def __str__(self) -> str:
        return self.separator.join(self._path)

    def upperCamelCase(self) -> str:
        return "".join([p.capitalize() for p in self._enforce_absolute(self._path)])

    def __init__(self, *args: Union[str, "ModulePath"]) -> None:
        self._path: List[str] = list()
        log.debug("Building ModulePath from %s", args)
        if all(map(lambda a: isinstance(a, str), args)):
            if len(args) > 1:
                self._path = self._rectify(args)
            elif len(args) == 1:
                if len(args[0]) > 0:
                    self._path = self.split_str(args[0])
        elif len(args) == 1 and isinstance(args[0], self.__class__):
            self._path = self._rectify(args[0]._path)
        log.debug("Analysis yielded structure %s", self._path)

    def __getitem__(self, at: Union[int, slice]) -> Union["ModulePath", None]:
        if isinstance(at, int) and -len(self._path) <= at < len(self._path):
            return ModulePath(*[self._path.__getitem__(at)])
        elif isinstance(at, slice):
            return ModulePath(*self._path.__getitem__(at))
        else:
            return None

    def local_name(self) -> Union["ModulePath", None]:
        return self[-1]

    def __add__(self, other: Union["ModulePath", str]) -> "ModulePath":
        if isinstance(other, str):
            other_path: List[str] = self.split_str(other)
        else:
            other_path = self._enforce_absolute(other._path)
        return ModulePath(*(self._path + other_path))

    def __sub__(self, other: Union["ModulePath", str]) -> "ModulePath":
        if isinstance(other, str):
            other_path: List[str] = self.split_str(other)
        else:
            other_path = self._rectify(other._path)
        result = []
        for p, q in zip(self._path, other_path):
            if p == q:
                continue
            elif q == None:
                result.append(p)
            elif p == None:
                result.append(q)
            else:
                raise ValueError("The subtracted path must be an ancestor!")
        return ModulePath(*result)

    def subtract(
        self, other: "ModulePath", strict: bool = True
    ) -> Union["ModulePath", None]:
        if strict:
            return self.__sub__(other)
        else:
            try:
                return self.__sub__(other)
            except ValueError as e:
                return None

    def ancestor_of(self, other: "ModulePath") -> bool:
        return False if self.subtract(other, strict=False) is None else True

    def parent(self) -> "ModulePath":
        return ModulePath(*self._path[:-1])

    def get_common_prefix(self, other: "ModulePath") -> "ModulePath":
        return ModulePath(*(p for p, q in zip(self._path, other._path) if p == q))

    def relative_to(self, other: "ModulePath") -> Union["ModulePath", None]:
        return self.subtract(other, strict=False)


@dataclass
class InterfaceBase:
    registry: "InterfaceRegistry"
    module: Union[ModuleType, str]
    name: str = ""

    @classmethod
    def register(cls):
        pass

    @classmethod
    def get_interface(
        cls,
        module: Union[ModuleType, str],
        name: str,
        registry: "InterfaceRegistry",
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
    module: str = __name__
    interface = InterfaceBase
    path: ModulePath = ModulePath()
    _parent: Union[Type["InterfaceRegistry"], None] = None
    _children: List[Type["InterfaceRegistry"]] = list()

    _sub_apis: Dict = dict()

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
    def get_module(cls, module: Union[ModulePath, ModuleType, str]):
        from importlib import import_module, invalidate_caches

        name = ""
        if isinstance(module, ModuleType):
            name = module.__name__
        elif isinstance(module, ModulePath):
            name = str(module)
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
            api_interface.registry = cls
            canonical_name = cls.get_canonical_name(name)
            cls._sub_apis[canonical_name] = api_interface
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
                name=name,
            )

    @classmethod
    def get_local_name(cls, name: str) -> str:
        log.debug(
            "Getting local name for %s as %s", name, ModulePath(name).local_name()
        )
        return str(ModulePath(name).local_name())

    @classmethod
    def get_canonical_name(cls, name: str) -> str:
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
        if local_name in cls._sub_apis.keys():
            from importlib import invalidate_caches
            from sys import modules

            cls._sub_apis.pop(name)
            api_interface.registry = None
            canonical_name = cls.get_canonical_name(name)
            del modules[canonical_name]
            invalidate_caches()
            log.debug("Unregistered module %s", canonical_name)

    @classmethod
    def get_apis(cls):
        return copy.deepcopy(cls._sub_apis)

    @classmethod
    def get_all_apis(cls):
        child_sub_apis = dict()
        for child in cls._children:
            log.debug("Fetching APIs from %s", child.__name__)
            child_sub_apis.update(child._sub_apis)
        child_sub_apis.update(cls._sub_apis)
        return child_sub_apis

    @classmethod
    def get_interface_registry_name(cls, module: str) -> str:
        return (ModulePath(module) + "Registry").upperCamelCase()

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
    def get_interface_registry(
        cls,
        InterfaceT,
        module: str,
        path: Union[ModulePath, str, None] = None,
        forbidden_names: Set[str] = set(),
    ):
        name = InterfaceT.name or ModulePath(module).local_name()
        path = path or cls.path + name
        R = type(
            cls.get_interface_registry_name(module),
            (cls,),
            {
                "interface": InterfaceT,
                "module": module,
                "path": path,
                "_parent": cls,
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
            R.register_api(c)

        InterfaceT.register = classmethod(reg)
        InterfaceT.Registry = R
        return R


information = _api.ApiInformation(version=0)

entrypoints = _api.entrypoints.create_entrypoints(_module_name)

Registry = InterfaceRegistry.get_interface_registry(
    InterfaceT=InterfaceBase,
    module=_module_name,
    path=ModulePath("v0"),
    forbidden_names=set("__strictly_prohibited__"),
)

get_interface_registry = Registry.get_interface_registry
register_api = Registry.register_api
unregister_api = Registry.unregister_api
get_apis = Registry.get_apis
