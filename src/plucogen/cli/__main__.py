from pathlib import Path
from click import Choice
from typer import Option
from typing import Annotated, Optional
from plucogen import logging
from plucogen.api.v0 import Registry

from .api import app

log = logging.getLogger(__name__)

@app.callback()
def root(
    config: Annotated[Optional[Path], Option(
        help="Path to the config-file to load"
    )] = None,
    log_level: Annotated[
        str,
        Option(
            help="Log-level to run the application with",
            click_type=Choice(logging.LogLevels._member_names_, case_sensitive=False),
            show_default=True,
        ),
    ] = logging.LogLevels.info.name,

    verbose: Annotated[bool, Option(
        help="Output verbose information"
    )] = False,
):
    # Set loglevel
    log_level_int = logging.LogLevels[log_level]
    logging.basicConfig(level=log_level_int)
    log.info("Started logging. Messages above where buffered since program startup.")


def main():
    return app()


if __name__ == "__main__":  # pragma: no cover
    main()
