from pathlib import Path
from typing import Annotated, List, Union

from _typeshed import StrPath
from annotated_types import _StrType
from jinja2 import Environment
from jinja2.environment import TemplateExpression
from pydantic.networks import AnyUrl

Path = Path
Paths = List[Path]


class _PathTemplate(object):
    def __init__(self, *args) -> None:
        paths = []
        self._env = None
        for i, arg in enumerate(args):
            if isinstance(arg, str):
                if self._env is None:
                    self._env = Environment()
                paths.append(self._env.compile_expression(arg))
            else:
                paths.append(arg)
        self._raw_paths = paths

    def compile_with(self, cwd: Path = Path.cwd(), *args, **kwargs) -> Path:
        paths: List[StrPath] = []
        for path in self._raw_paths:
            if isinstance(path, TemplateExpression):
                str_path = str(path(*args, **kwargs))
                if isinstance(str_path, str):
                    if "*" in str_path:
                        if Path(str_path).is_absolute():
                            paths.extend(Path("/").glob(str_path))
                        else:
                            paths.extend(cwd.glob(str_path))
                    else:
                        paths.append(str_path)
                else:
                    raise TypeError(
                        f"Cannot parse template-path '{path._template}' to a valid StrPath!"
                    )
            else:
                paths.append(path)
        return Path(*paths)


PathTemplate = Annotated[_PathTemplate, _StrType]
PathTemplates = List[PathTemplate]

AnyPath = Union[Path, PathTemplate]
AnyPaths = List[AnyPath]

UrlTemplate = Annotated[str, _StrType]
UrlTemplates = List[UrlTemplate]

Resource = Union[Path, AnyUrl]
Resources = List[Resource]

ResourceTemplate = Union[PathTemplate, UrlTemplate]
ResourceTemplates = List[ResourceTemplate]

AnyResource = Union[Resource, ResourceTemplate]
AnyResources = List[AnyResource]
