import unittest
import logging
from io import StringIO

logger = logging.getLogger()


class TestCase(unittest.TestCase):
    """Enhanced unittest TestCase class with logging"""

    def setUp(self, *args, **kwargs):
        super(TestCase, self).setUp(*args, **kwargs)
        self.stream = StringIO()
        self.handler = logging.StreamHandler(self.stream)
        logger.addHandler(self.handler)

    def tearDown(self, *args, **kwargs):
        super(TestCase, self).tearDown(*args, **kwargs)
        logger.removeHandler(self.handler)
