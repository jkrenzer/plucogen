import copy
from abc import ABC, abstractmethod
from dataclasses import dataclass
from inspect import isabstract, isclass
from multiprocessing import Value
from os import PathLike
from types import ModuleType
from typing import Dict, List, Set, Type, Union

from pkg_resources import load_entry_point

from plucogen import api as _api
from plucogen.api.entrypoint import Entrypoints
from plucogen.api.v0 import _module_name
from plucogen.logging import getLogger

from .module_path import ModulePath

log = getLogger(__name__)


@dataclass
class InterfaceBase(object):
    registry: Union["InterfaceRegistry", None] = None
    module: Union[ModulePath, str] = ""
    name: str = ""

    @classmethod
    def get_registry(cls) -> "InterfaceRegistry":
        from .interface_registry import InterfaceRegistry

        return cls.registry or InterfaceRegistry

    @classmethod
    def get_module_name(cls):
        if isinstance(cls.module, ModuleType):
            return cls.module.__name__
        else:
            return cls.module

    @classmethod
    def module_available(cls) -> bool:
        return cls.get_registry().module_available(cls.get_module_name())

    @classmethod
    def create_interface(
        cls,
        module: Union[ModuleType, str],
        name: str,
        registry: Type["InterfaceRegistry"],
        bases=tuple(),
    ) -> Type["InterfaceBase"]:
        name = name.split(".")[0]
        return type(
            name.capitalize() + "Interface",
            (cls,) + bases,
            {"name": name, "module": module, "registry": registry},
        )

    @classmethod
    def import_module(cls) -> ModuleType:
        return cls.get_registry().import_module(cls.module)

    @classmethod
    def register(cls) -> None:
        cls.get_registry().register_api(cls)


from .interface_registry import InterfaceRegistry
