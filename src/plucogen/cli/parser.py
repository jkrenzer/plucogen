import configargparse
from plucogen import logging, _module_name

log = logging.getLogger(__name__)

rootParser = configargparse.ArgParser(
    prog=_module_name,
    default_config_files=["./.plucogen.yml", "./.plucogen.yaml"],
    config_file_parser_class=configargparse.YAMLConfigFileParser,
    args_for_writing_out_config_file=["-w", "--write-config"],
)
rootParser.set_defaults(func=lambda _: rootParser.print_help())

add_subparsers = rootParser.add_subparsers

subParsers = add_subparsers(dest="command")  # type: ignore

rootParser.add(
    "-c",
    "--config",
    required=False,  # type: ignore
    is_config_file=True,
    help="config file path",
)
rootParser.add(
    "--log-level",
    default="info",
    help="set loglevel",  # type: ignore
    choices=logging.log_levels,
)
rootParser.add("-v", help="be verbose", action="store_true")  # type: ignore

def parse_args(args):
    return rootParser.parse_args(args)
