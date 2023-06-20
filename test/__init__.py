from unittest import TestSuite
from typing import List
from .jinja import TestJinjaExtensions
from .render import TestRender
from .yaml import TestTagInclude, TestTagTemplate, TestYaml
from .cli import TestCLI
from .plugin import TestEntrypoints
from .api import TestApiV0Interface

test_cases = (
    TestCLI,
    TestJinjaExtensions,
    TestRender,
    TestTagInclude,
    TestTagTemplate,
    TestYaml,
    TestEntrypoints,
    TestApiV0Interface,
)


def load_tests(loader, tests, pattern: List[str] = ["*"]):
    suite = TestSuite()
    loader.testNamePatterns = pattern
    for test_class in test_cases:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    return suite
