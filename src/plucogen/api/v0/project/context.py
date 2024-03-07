from typing import Any, Dict, Tuple

from pydantic import Field

from plucogen.api.v0.pydantic import BaseModel


class Context(BaseModel):
    variables: Dict[str, Any] = Field(default_factory=dict)
    tree: Dict[str, Any] = Field(default_factory=dict)
    path: Tuple[Any, ...] = Field(default_factory=tuple)
