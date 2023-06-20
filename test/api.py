from unittest import TestCase


class TestApiV0Interface(TestCase):
    def test_wrong_interface_rejection(self):
        from plucogen.api.v0 import register_api

        class MockInterface:
            name = "mock"

        self.assertRaises(ImportError, register_api, MockInterface)

    def test_api_registration(self):
        from plucogen.api.v0 import register_api, unregister_api
        from plucogen.api.v0.api import Interface
        from types import ModuleType
        import sys

        def t():
            return True

        m = ModuleType("mockTestModule")

        test_interface = Interface(name="test", module=m)

        m.t = t
        sys.modules[m.__name__] = m

        register_api(test_interface)

        from plucogen.api.v0.test import t as t2  # type: ignore

        self.assertTrue(t2())
        unregister_api(test_interface)
        with self.assertRaises(ImportError):
            from plucogen.api.v0.test import t as t3  # type: ignore
