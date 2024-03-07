from test.base import test_case
from .config import TestConfig
from .playbook import TestPlaybook
from .action import TestAction

test_cases = (TestConfig, TestPlaybook, TestAction)
