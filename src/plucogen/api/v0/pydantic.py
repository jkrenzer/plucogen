from typing import Any, Dict

from pydantic import BaseModel as _BaseModel

from plucogen.api.v0.template import Template


class BaseModel(_BaseModel):
    @classmethod
    def evaluate_templates(cls, data: Any, variables: Dict[str, Any] = {}) -> Any:
        if isinstance(data, str):
            data = Template(data).evaluate(**variables)
        elif isinstance(data, dict):
            data = {k: cls.evaluate_templates(v, variables) for k, v in data.items()}
        elif isinstance(data, (list, tuple)):
            data = type(data)([cls.evaluate_templates(v, variables) for v in data])
        else:
            data = data
        return data
