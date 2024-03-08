from configargparse import ArgParser, YAMLConfigFileParser
from plucogen import logging
from unittest import TestLoader
from pathlib import Path
from . import load_tests
import sys


rootParser = ArgParser(
    prog="test",
    default_config_files=["./.config_test.yml"],
    config_file_parser_class=YAMLConfigFileParser,
    args_for_writing_out_config_file=["-w", "--write-config"],
)

rootParser.add(
    "-c",
    "--config",
    required=False,  # type: ignore
    is_config_file=True,
    help="config file path",
)
rootParser.add(
    "--log-level",
    default="debug",
    help="set loglevel",  # type: ignore
    choices=logging.LogLevels._member_names_,
)
rootParser.add("-v", "--verbose", help="be verbose", action="count", default=0)  # type: ignore
rootParser.add("-t", "--tap", help="output results in TAP protocol", action="store_true")  # type: ignore
rootParser.add("-C", "--coverage-report", help="generate a coverage report in the given format", choices=["html", "json", "lcov", "xml"], type=str.lower)  # type: ignore
rootParser.add(
    "--coverage-output",
    help="generate the output in this folder or file. HTML needs a directory here",
    default="./.coverage_report",
    type=Path,
)
rootParser.add("pattern", help="Pattern(s) of tests to run", default=["*"], nargs="*")  # type: ignore

if __name__ == "__main__":
    #    logging.basicConfig(level=logging.DEBUG)

    options = rootParser.parse_args()
    tests = TestLoader().loadTestsFromModule(
        sys.modules[__name__], pattern=options.pattern
    )

    # Set loglevel
    logging.basicConfig(level=logging.LogLevels[options.log_level.lower()])

    if options.tap:
        from pycotap import TAPTestRunner

        testRunner = TAPTestRunner()
    else:
        from .base import TestRunner

        testRunner = TestRunner(verbosity=options.verbose)

    if options.coverage_report:
        from coverage import Coverage

        cov = Coverage(branch=True)
        cov.start()
        testRunner.run(tests)
        cov.stop()
        if options.coverage_report == "html":
            cov.html_report(directory=str(options.coverage_output.stem))
        elif options.coverage_report == "json":
            if options.coverage_output.suffixes == []:
                options.coverage_output /= "report.json"
            cov.json_report(outfile=str(options.coverage_output), pretty_print=True)
        elif options.coverage_report == "lcov":
            if options.coverage_output.suffixes == []:
                options.coverage_output /= "report.lcov"
            cov.lcov_report(
                outfile=str(options.coverage_output),
            )
        elif options.coverage_report == "xml":
            if options.coverage_output.suffixes == []:
                options.coverage_output /= "report.xml"
            cov.xml_report(
                outfile=str(options.coverage_output),
            )
    else:
        testRunner.run(tests)
