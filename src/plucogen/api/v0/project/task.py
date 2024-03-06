from typing import Any, Dict, List, Literal, Union, Optional

from pydantic import Field

from plucogen.api.v0.pydantic import BaseModel
from plucogen.api.v0.resource import AnyResource

from .action import Action


class ApiDeclaration(BaseModel):
    version: Literal[0] = 0
    type: Literal["plucogen.v0.task"] = "plucogen.v0.task"


class Task(BaseModel):
    api: ApiDeclaration = Field(default_factory=ApiDeclaration)
    name: str
    description: Optional[str]
    variables: Dict[str, Any] = Field(default_factory=dict)
    actions: List[Union[AnyResource, Action]]
