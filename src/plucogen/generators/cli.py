from plucogen import logging
from plucogen.cli import parser

log = logging.getLogger(__name__)


def main(options):
    """Call from argparse options from the CLI, unittests or extension programs"""
    log.error("This function is not implemented yet!")
    return 1


generateSubParser = parser.subParsers.add_parser(
    "generate", help="generate files from templates and data"
)  # type: ignore

generateSubParser.set_defaults(func=main)

generateSubParser.add(
    "-m", "--module-path", nargs=1, help="path to load module from"  # type: ignore
)

generatorParsers = generateSubParser.add_subparsers(required=False)
