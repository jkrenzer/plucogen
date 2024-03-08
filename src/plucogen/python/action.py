from importlib.metadata import EntryPoint
from typing import Any, Dict, List

from pydantic import Field, validate_call

from plucogen.api.v0.project.action.api import Interface as _Interface


def execute(
    call: str, args: List[Any] = [], kwargs: Dict[str, Any] = {}, validate: bool = True
) -> Any:
    # Get the callable
    ep = EntryPoint(name="", value=call, group="")
    function = ep.load()
    if callable(function):
        if validate:
            return validate_call(function)(*args, **kwargs)
        else:
            return function(*args, **kwargs)
    else:
        raise ValueError(f"'{call}' is not a callable!")


class Interface(_Interface):
    name = "python"
    module = __name__
    function = execute


Interface.register()
