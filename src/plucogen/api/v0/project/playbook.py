from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import Field, validate_call

from plucogen.api.v0.pydantic import BaseModel
from plucogen.api.v0.resource import AnyResource, AnyUrl, Path, PathTemplate

from .action import Action
from .context import Context


class ApiDeclaration(BaseModel):
    version: Literal[0] = 0
    type: Literal["plucogen.v0.playbook"] = "plucogen.v0.playbook"


class Playbook(BaseModel):
    api: ApiDeclaration = Field(default_factory=ApiDeclaration)
    name: str
    description: Optional[str] = None
    variables: Dict[str, Any] = Field(default_factory=dict)
    actions: List[Union[AnyResource, Action]] = Field(default_factory=list)

    @validate_call
    def execute(self, context: Context = Context()) -> Dict[Union[int, str], Any]:
        # Get all actions
        actions: List[Action] = []
        local_variables = self.evaluate_templates(self.variables, context.variables)
        if context.tree == {}:
            context.tree = self.model_dump()
        context.variables.update(
            local_variables
        )  # Override global with local variables
        for action in self.actions:
            if isinstance(action, Action):
                actions.append(action)
            elif isinstance(action, PathTemplate):
                action = action.evaluate(**context.variables)
                raise NotImplementedError(
                    "Loading of information from PathTemplate is currently not implemented!"
                )
            elif isinstance(action, Path):
                raise NotImplementedError(
                    "Loading of information from Path is currently not implemented!"
                )
            elif isinstance(action, AnyUrl):
                raise NotImplementedError(
                    "Loading of information from Urls is currently not implemented!"
                )
            else:
                raise ValueError("Invalid action value!")
        results = {}
        for n, action in enumerate(actions):
            context.path = ("actions", n)
            results[n] = action.execute(context)
            if action.name:
                results[action.name] = results[n]
        return results
