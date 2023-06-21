from plucogen.generators import generatorParsers
from .. import logging
from plucogen.handlers.yaml import tags

log = logging.getLogger(__name__)


def main(options):
    log.warn(
        "This is an example how to implement a new generator. It does nothing by design."
    )


ourParser = generatorParsers.add_parser("example")
ourParser.set_defaults(func=main)

ourParser.add_argument(
    "-b",
    "--base-dir",
    default=".",
    help="directory relative to which relative paths will be interpreted",
)
ourParser.add_argument(
    "-o",
    "--output-dir",
    default=".",
    help="directory below which all generated files should be put",
)
ourParser.add_argument(
    "-d",
    "--definitions-dir",
    default="./defs",
    help="directory containing the definition YAML files",
)
ourParser.add_argument(
    "-s",
    "--sources-dir",
    default="./src",
    help="directory in which the sources and templates are stored",
)
