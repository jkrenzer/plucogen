from plucogen.api.v0.resource import PathTemplate, Path
from test.base import TestCase


class TestConfig(TestCase):
    def test_config(self):
        from plucogen.api.v0.project import Configuration

        config_dict = {}
        config = Configuration(**config_dict)
        self.assertIsInstance(config, Configuration)
