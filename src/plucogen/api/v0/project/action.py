from typing import Any, Dict, Union, Optional, Type

from pydantic import model_validator

from plucogen.api.v0.pydantic import BaseModel
from plucogen.api.v0.resource import ModulePath


class Action(BaseModel):
    module: ModulePath
    parameters: Dict[str, Union[str, Any]]
    name: Optional[str]
    description: Optional[str]

    @model_validator(mode="before")  # type: ignore
    @classmethod
    def validate_short_form(cls: Any, data: Any) -> Any:
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

    @model_validator(mode="after")
    def validate_module_viability(self: "Action") -> "Action":
        """Validate the module has an action interface"""
        from plucogen.api.v0 import Registry

        if not Registry.is_available(self.module):
            raise ValueError(f"Module {self.module} is unknown!")
        return self
