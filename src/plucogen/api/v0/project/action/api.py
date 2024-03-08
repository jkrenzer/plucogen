from typing import Any, Callable, Dict, Optional, Type, Union, cast

from pydantic import Field, model_validator, validate_call

from plucogen.api.v0.api import InterfaceBase as _ApiInterface
from plucogen.api.v0.api import create_interface_registry
from plucogen.api.v0.pydantic import BaseModel
from plucogen.api.v0.resource import ModulePath
from plucogen.logging import getLogger

from ..context import Context

log = getLogger(__name__)


class Interface(_ApiInterface):
    name = "action"
    module = __name__
    function: Callable

    def __init_subclass__(cls) -> None:
        if not hasattr(cls, "function") or not callable(cls.function):
            raise NotImplementedError(
                "Attribute 'function' of class must be a callable object!"
            )
        return super().__init_subclass__()


Registry = create_interface_registry(
    InterfaceT=Interface, module=__name__, forbidden_names=set()
)


class Action(BaseModel):
    module: ModulePath
    parameters: Dict[str, Union[str, Any]] = Field(default_factory=dict)
    name: Optional[str] = None
    description: Optional[str] = None

    # @model_validator(mode="before")  # type: ignore
    # @classmethod
    # def validate_short_form(cls: Any, data: Any) -> Any:
    #     """This validator recognized a short form of the Action model."""
    #     if isinstance(data, dict):
    #         if 'module' not in data.keys() and isinstance(list(data.values())[0], dict):
    #             new_data = {
    #                 "module": list(data.keys())[0],
    #                 "parameters": list(data.values())[0],
    #             }
    #             return new_data
    #     else:
    #         return data

    # @model_validator(mode="after")
    # def validate_module_viability(self: "Action") -> "Action":
    #     """Validate the module has an action interface"""

    #     if not Registry.is_available(self.module.as_str):
    #         raise ValueError(f"Module {self.module.as_str} is unknown!")
    #     return self

    @validate_call
    def execute(self, context: Context = Context()) -> Any:
        parameters = self.evaluate_templates(self.parameters, context.model_dump())
        interface = cast(Interface, Registry.get_apis().get(self.module.as_str, None))
        if interface is not None:
            function = cast(
                Interface, Registry.get_apis().get(self.module.as_str, None)
            ).function
            if function is not None:
                if callable(function):
                    log.debug(
                        f"Calling function {repr(function)} with parameters '{parameters}'"
                    )
                    return validate_call(function)(**parameters)
                else:
                    raise ValueError(
                        f"Attribute 'function' given by interface of {self.module.as_str} is not callable!"
                    )
            else:
                raise ValueError(f"Function {self.module.as_str} is unknown!")
        else:
            raise ValueError(f"Module {self.module.as_str} is unknown!")
