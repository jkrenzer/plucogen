from typing import Any, Dict, List, Literal, Optional

from pydantic import Field

from plucogen.api.v0.pydantic import BaseModel
from plucogen.api.v0.resource import AnyResource


class ApiDeclaration(BaseModel):
    version: Literal[0] = 0
    type: Literal["playbook"] = "playbook"


class Playbook(BaseModel):
    api: ApiDeclaration = Field(default_factory=ApiDeclaration)
    name: str
    description: Optional[str]
    variables: Dict[str, Any] = Field(default_factory=dict)
    tasks: List[AnyResource, Task]
