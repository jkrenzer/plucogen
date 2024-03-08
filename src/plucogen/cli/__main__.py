from timeit import default_timer as timer

_preparation_timer = timer()

from pathlib import Path
from typing import Annotated, Optional

from click import Choice
from typer import Option, echo

from plucogen import logging
from plucogen.api.v0 import Registry

from .api import app

log = logging.getLogger(__name__)

_time_execution = False


@app.callback()
def root(
    config: Annotated[
        Optional[Path], Option(help="Path to the config-file to load")
    ] = None,
    log_level: Annotated[
        str,
        Option(
            help="Log-level to run the application with",
            click_type=Choice(logging.LogLevels._member_names_, case_sensitive=False),
            show_default=True,
        ),
    ] = logging.LogLevels.info.name,
    verbose: Annotated[bool, Option(help="Output verbose information")] = False,
    time_execution: Annotated[
        Optional[bool],
        Option(help="Print the execution time of the desired command after finisch"),
    ] = False,
):
    # Set loglevel
    log_level_int = logging.LogLevels[log_level]
    logging.basicConfig(level=log_level_int)
    log.info("Started logging. Messages above where buffered since program startup.")

    # Set timer
    global _time_execution
    _time_execution = time_execution


def main():
    result = None
    start = timer()
    try:
        result = app()
    except SystemExit as e:
        end = timer()
        global _time_execution
        if _time_execution:
            echo(f"Preparation time: {start-_preparation_timer}")
            echo(f"Execution time: {end-start}s")
            echo(f"Total time: {end-_preparation_timer}s")
        raise e


if __name__ == "__main__":  # pragma: no cover
    main()
