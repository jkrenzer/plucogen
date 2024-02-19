from typing import Any, Dict, List, Literal, Union

from pydantic import Field

from plucogen.api.v0.project.playbook import Playbook
from plucogen.api.v0.pydantic import BaseModel
from plucogen.api.v0.resource import (
    AnyPath,
    AnyResource,
    AnyResources,
    Path,
    PathTemplate,
)


class ApiDeclaration(BaseModel):
    version: Literal[0] = 0
    type: Literal["project"] = "project"


class Configuration(BaseModel):
    api: ApiDeclaration
    base_dir: Path = Path(".")
    build_dir: AnyPath = PathTemplate("./build")
    play_books: List[Union[AnyResource, Playbook]] = [
        PathTemplate("./playbooks/*"),
    ]
    globals: Dict[str, Any] = Field(default_factory=dict)
    sub_projects: AnyResources = Field(default_factory=list)
