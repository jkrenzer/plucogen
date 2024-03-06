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
    PathTemplates,
)


class ApiDeclaration(BaseModel):
    version: Literal[0] = 0
    type: Literal["plucogen.v0.config"] = "plucogen.v0.config"


class Configuration(BaseModel):
    api: ApiDeclaration = Field(default_factory=ApiDeclaration)
    globals: Dict[str, Any] = Field(default_factory=dict)
    project_file_patterns: PathTemplates = [
        PathTemplate("./.plucogen/config.yaml"),
        PathTemplate("./.plucogen/config.yml"),
        PathTemplate("./plucogen.yaml"),
        PathTemplate("./plucogen.yml"),
    ]
