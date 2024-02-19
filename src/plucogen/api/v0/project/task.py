from typing import Any, Dict, List, Literal, Union, Optional

from pydantic import Field, model_validator

from plucogen.api.v0.pydantic import BaseModel
from plucogen.api.v0.resource import AnyResource


class ApiDeclaration(BaseModel):
    version: Literal[0] = 0
    type: Literal["task"] = "task"


class Action(BaseModel):
    module: str
    parameters: Dict[str, Union[str, Any]]
    name: Optional[str]
    description: Optional[str]

    @model_validator(mode="before")
    @classmethod
    def validate_short_form(cls, data: Any) -> Any:
        """This validator recognized a short form of the Action model."""
        if isinstance(data, dict):
            if len(data.keys()) == 1 and isinstance(list(data.values())[0], dict):
                new_data = {
                    "module": list(data.keys())[0],
                    "parameters": list(data.values())[0],
                }
                return new_data
        else:
            return data


class Task(BaseModel):
    api: ApiDeclaration = Field(default_factory=ApiDeclaration)
    name: str
    description: Optional[str]
    variables: Dict[str, Any] = Field(default_factory=dict)
    actions: List[Union[AnyResource, Action]]
