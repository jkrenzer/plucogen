from unittest import TestCase, expectedFailure
import os

current_dir = os.path.dirname(__file__)


class TestApiV0Interface(TestCase):
    def test_wrong_interface_rejection(self):
        from plucogen.api.v0.api import register_api

        class MockInterface:
            name = "mock"

        self.assertRaises(ImportError, register_api, MockInterface)

    def test_wrong_interface_rejection(self):
        from plucogen.api.v0.api import register_api, InterfaceBase
        from abc import abstractmethod

        class MockInterface(InterfaceBase):
            name = "mock"
            module = "__does.__not.__exist"

            @abstractmethod
            def test():
                pass

        self.assertRaises(ImportError, register_api, MockInterface)

    def test_api_registration(self):
        from plucogen.api.v0.api import InterfaceBase, register_api, unregister_api
        from types import ModuleType
        import sys

        def t():
            return True

        m = ModuleType("mockTestModule")

        test_interface = InterfaceBase(name="test", module=m)

        m.t = t
        sys.modules[m.__name__] = m

        register_api(test_interface)

        from plucogen.api.v0.test import t as t2  # type: ignore

        self.assertTrue(t2())
        unregister_api(test_interface)
        with self.assertRaises(ImportError):
            from plucogen.api.v0.test import t as t3  # type: ignore

    def test_consumer(self):
        from plucogen.api.v0.consumer import file, Interface
        from pathlib import Path

        testFile = Path(current_dir) / "test_include.yaml"
        input = Interface.InputData(
            options=None, resources=[testFile], return_code=0, messages=[]
        )
        self.assertIsInstance(file.Interface.consume(input).data[0], str)

    def test_base_apis_registered(self):
        from plucogen.api.v0.api import Registry, InterfaceRegistry
        from inspect import isabstract

        self.assertTrue(issubclass(Registry, InterfaceRegistry))
        self.assertFalse(isabstract(Registry))
        mandatory_apis = {"cli", "consumer", "generator", "handler", "writer"}
        for a in mandatory_apis:
            with self.subTest("Checking API %s registered" % a, api=a):
                self.assertTrue(
                    Registry.is_available(a), "Mandatory API %s not registered!" % a
                )

    def test_entrypoint_generation(self):
        from plucogen.api.v0.api import entrypoints as e1
        from plucogen.cli.api import entrypoints as e2

        self.assertIsInstance(e1.get(), list)
        self.assertIsInstance(e2.get(), list)
