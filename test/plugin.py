from unittest import TestCase

class TestEntrypoints(TestCase):
    def test_generators_argparser(self):
        from importlib_metadata import entry_points
        from plucogen.generators import generatorParsers
        ourEntrypoints = entry_points(group='plucogen.plugin.generators', name='generatorArgParsers')
        self.assertIn('generatorArgParsers', ourEntrypoints.names)
        generatorArgParser = ourEntrypoints['generatorArgParsers'].load()
        self.assertIs(generatorArgParser, generatorParsers)