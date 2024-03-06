from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import Field

from plucogen.api.v0.pydantic import BaseModel
from plucogen.api.v0.resource import AnyResource

from .task import Task


class ApiDeclaration(BaseModel):
    version: Literal[0] = 0
    type: Literal["plucogen.v0.playbook"] = "plucogen.v0.playbook"


class Playbook(BaseModel):
    api: ApiDeclaration = Field(default_factory=ApiDeclaration)
    name: str
    description: Optional[str]
    variables: Dict[str, Any] = Field(default_factory=dict)
    tasks: List[Union[AnyResource, "Task"]]
