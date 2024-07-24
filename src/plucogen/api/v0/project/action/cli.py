from typing import Annotated, Any, List
from typer import Argument, Option, Typer, echo, Exit
from click import Tuple
from plucogen.api.v0.cli import Interface as _CliInterface
from plucogen.api.v0.project.context import Context
from plucogen.api.v0.resource import ModulePath

from .api import Action

app = Typer(help="Execute an action")


class Interface(_CliInterface):
    name = "action"
    app = app


Interface.register()


@app.command()
def run(
    module: Annotated[str, Argument(help="Module to run")],
    parameter: Annotated[
        List[Tuple],
        Option(
            default_factory=tuple,
            help="Parameter given as tuple of a string name and a string literally evaluated by Python to a type (Remember to escape-quote string type!!).",
            click_type=Tuple([str, str]),
        ),
    ],
) -> Any:
    from ast import literal_eval

    parameters = {}
    for p in parameter:
        try:
            parameters[p[0]] = literal_eval(p[1])
        except SyntaxError as e:
            marked_text = e.text[: e.offset] + "<!>" + e.text[e.end_offset - 1 :]
            echo(
                f"Syntax error in parameter {p[0]}'s expression '{e.text}' at <!> mark: '{marked_text}'",
                err=True,
            )
            raise Exit(1)

    action = Action(
        module=module,
        parameters=parameters,
    )
    context = Context()
    result = action.execute(context)
    echo(result, nl=False)
