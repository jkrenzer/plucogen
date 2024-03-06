from pathlib import Path
from typing import Annotated, Any, List, Union

from os import PathLike
from jinja2.environment import Environment, Template
from pydantic import GetPydanticSchema, GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic_core import core_schema, CoreSchema
from pydantic.networks import AnyUrl

from plucogen.logging import getLogger
from .api.module_path import ModulePath as _ModulePath

Paths = List[Path]

log = getLogger(__name__)


class _PathTemplate(object):
    def __init__(self, *args) -> None:
        log.debug(f"Building PathTemplate from {args}")
        self._raw_paths = args or []

    def evaluate(self, cwd: Path = Path.cwd(), *args, **kwargs) -> Path:
        paths: List[PathLike] = []
        env = Environment()
        for path in self._raw_paths:
            str_path = str(env.from_string(path).render(*args, **kwargs))
            if isinstance(str_path, str):
                if "*" in str_path:
                    path = Path(str_path)
                    if path.is_absolute():
                        paths.extend(path.parent.glob(path.name))
                    else:
                        paths.extend(cwd.glob(str_path))
                else:
                    paths.append(str_path)
            else:
                raise TypeError(
                    f"Cannot parse template-path '{str(path)}' to a valid PathLike!"
                )
        return Path(*paths)


_HandleAsStr = GetPydanticSchema(
    lambda tp, handler: core_schema.no_info_after_validator_function(
        lambda p: str(p), handler(str)
    )
)


class PathTemplate(_PathTemplate):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls,
            handler(str),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: str(instance)
            ),
        )


class ModulePath(_ModulePath):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls,
            handler(str),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: str(instance)
            ),
        )


AnyPath = Union[Path, PathTemplate]
UrlTemplate = Annotated[str, _HandleAsStr]
Resource = Union[AnyPath, AnyUrl]
ResourceTemplate = Union[PathTemplate, UrlTemplate]
AnyResource = Union[Resource, ResourceTemplate]

PathTemplates = List[PathTemplate]
AnyPaths = List[AnyPath]
UrlTemplates = List[UrlTemplate]
Resources = List[Resource]
ResourceTemplates = List[ResourceTemplate]
AnyResources = List[AnyResource]
ModulePaths = List[ModulePath]
