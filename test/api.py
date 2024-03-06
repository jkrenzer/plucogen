from plucogen.api.v0.base import Interface
from .base import TestCase
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
        from plucogen.api import v0
        from plucogen.api.v0.api import (
            InterfaceBase,
            Registry,
            register_api,
            unregister_api,
        )
        from types import ModuleType
        import sys

        from . import api_mock_module as m

        test_interface = InterfaceBase.create_interface(
            name="test", module=m.__name__, registry=Registry
        )

        register_api(test_interface)

        test = v0.import_module("plucogen.v0.test")
        t2 = test.t  # type: ignore

        self.assertTrue(t2())
        unregister_api(test_interface)
        with self.assertRaises(ImportError):
            test = v0.import_module("plucogen.v0.test")

    def test_consumer(self):
        from plucogen.api import v0
        from plucogen.logging import getLogger

        log = getLogger(__name__)

        file = v0.import_module("plucogen.v0.consumer.file")
        Interface = file.Interface

        from pathlib import Path

        testFile = Path(current_dir) / "test_include.yaml"
        input = Interface.InputData(
            options=None, resources=[testFile], return_code=0, messages=[]
        )
        self.assertIsInstance(file.Interface.consume(input).data[0], str)

    def test_base_apis_registered(self):
        from plucogen.api import v0
        from plucogen.api.v0.api import Registry, InterfaceRegistry
        from inspect import isabstract

        self.assertTrue(issubclass(Registry, InterfaceRegistry))
        self.assertFalse(isabstract(Registry))
        versions = {"v0"}
        prefix = "plucogen.api"
        mandatory_apis = {"cli", "consumer", "generator", "handler", "writer"}
        for v in versions:
            for a in mandatory_apis:
                a_str = f"{prefix}.{v}.{a}"
                with self.subTest("Checking API %s registered" % a, api=a_str):
                    self.assertTrue(
                        Registry.is_available(a_str),
                        "Mandatory API %s not registered!" % a_str,
                    )

    def test_entrypoint_generation(self):
        from plucogen.api.v0.api import entrypoints as e1
        from plucogen.cli.api import entrypoints as e2

        self.assertIsInstance(e1.get(), list)
        self.assertIsInstance(e2.get(), list)
