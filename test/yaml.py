import os
from plucogen.handlers.yaml import load_yaml_file, load_yaml_string
from typing import Dict

from .base import TestCase

current_dir = os.path.dirname(__file__)


class TestYaml(TestCase):
    def test_yaml_load_string(self):
        data = load_yaml_string("a: 1")
        reference_data = {"a": 1}
        self.assertEqual(data, reference_data)

    def test_yaml_load_file(self):
        data_file = os.path.join(current_dir, "test_yaml_load_file.yaml")
        data = load_yaml_file(data_file)
        reference_data = {"a": 1}
        self.assertEqual(data, reference_data)

    def test_yaml_path_resolver(self):
        from plucogen.handlers.yaml.tags import yaml_object, Tag, yaml

        @yaml_object(yaml)
        class Test(Tag):
            yaml_tag = "!test"

        @classmethod
        def from_yaml(cls, constructor, node):
            obj = cls()
            return obj

        yaml_str = """
            a: 1
            b:
              num: 2
              test:
                testObj: true
        """

        Test.register_path(["b", "test"])
        data = load_yaml_string(yaml_str)
        self.assertIsInstance(data, Dict)
        test = isinstance(data, Dict) and data["b"]["test"] or None
        self.assertIsInstance(test, Test)


class TestTagInclude(TestCase):
    def test_construction(self):
        from plucogen.handlers.yaml.tags import Include

        self.assertIsInstance(Include("test.yaml"), Include)

    def test_loading(self):
        import plucogen.handlers.yaml.tags

        reference_file = os.path.join(current_dir, "test_include.yaml")
        reference_data = load_yaml_file(reference_file)
        include_data = load_yaml_string(
            """
            i: !include
                file: {}
            """.format(
                reference_file
            )
        )
        self.assertEqual(reference_data, include_data["i"])  # type: ignore

    def test_loading_subdir(self):
        import plucogen.handlers.yaml.tags

        reference_file = os.path.join(current_dir, "test_include.yaml")
        include_file = os.path.join(current_dir, "test_subdir/test_include.yaml")
        reference_data = load_yaml_file(reference_file)
        include_data = load_yaml_file(include_file)
        self.assertEqual(reference_data, include_data["i"])  # type: ignore

    def test_loading_loop_handling(self):
        include_file = os.path.join(current_dir, "test_subdir/test_include_loop.yaml")
        include_data = load_yaml_file(include_file)
        reference_data = {
            "i": {
                "i": {"file": "test_include_loop.yaml"},
                "i2": {
                    "a": {
                        "float": 3.1415,
                        "list": [0, 1, 2],
                        "map": {"x": 0, "y": 1, "z": 2},
                        "number": 1,
                        "string": "Hello world!",
                    }
                },
            },
            "i2": {
                "a": {
                    "float": 3.1415,
                    "list": [0, 1, 2],
                    "map": {"x": 0, "y": 1, "z": 2},
                    "number": 1,
                    "string": "Hello world!",
                }
            },
        }
        self.assertEqual(reference_data, include_data)

    def test_loading_select_slash(self):
        import plucogen.handlers.yaml.tags

        reference_file = os.path.join(current_dir, "test_include.yaml")
        reference_data = load_yaml_file(reference_file)
        select_path = "a/number"
        include_data = load_yaml_string(
            """
            i: !include
                file: {}
                select: {}
            """.format(
                reference_file, select_path
            )
        )
        self.assertEqual(reference_data["a"]["number"], include_data["i"])  # type: ignore

    def test_loading_select_dot(self):
        import plucogen.handlers.yaml.tags

        reference_file = os.path.join(current_dir, "test_include.yaml")
        reference_data = load_yaml_file(reference_file)
        select_path = "a.number"
        include_data = load_yaml_string(
            """
            i: !include
                file: {}
                select: {}
            """.format(
                reference_file, select_path
            )
        )
        self.assertEqual(reference_data["a"]["number"], include_data["i"])  # type: ignore

    def test_loading_select_invalid(self):
        import plucogen.handlers.yaml.tags

        reference_file = os.path.join(current_dir, "test_include.yaml")
        select_path = "a/non_existing"
        with self.assertRaises(KeyError):
            load_yaml_string(
                """
                i: !include
                    file: {}
                    select: {}
                """.format(
                    reference_file, select_path
                )
            )

    def test_schema_validation(self):
        from jsonschema.exceptions import ValidationError

        reference_file = os.path.join(current_dir, "test_include.yaml")
        with self.assertRaises(ValidationError):
            load_yaml_string(
                """
                    i: !include
                      filee: {}
                    """.format(
                    reference_file
                )
            )

    def test_required_file_not_found(self):
        reference_file = os.path.join(current_dir, "DOES_NOT_EXIST.yaml")
        with self.assertRaises(FileNotFoundError):
            load_yaml_string(
                """
                    i: !include
                      file: {}
                    """.format(
                    reference_file
                )
            )

    def test_optional_file_not_found(self):
        reference_file = os.path.join(current_dir, "DOES_NOT_EXIST.yaml")
        load_yaml_string(
            """
                i: !include
                  file: {}
                  required: false
                """.format(
                reference_file
            )
        )


class TestTagTemplate(TestCase):
    def test_construction(self):
        from plucogen.handlers.yaml.tags import Template

        self.assertIsInstance(Template(), Template)

    def test_scalar_parsing(self):
        data = load_yaml_string(
            """
                a: 1
                b: !template "{{ 'ok'.upper() }}"
            """
        )
        reference = {"a": 1, "b": "OK"}
        self.assertEqual(data, reference)

    def test_file_parsing(self):
        from datetime import date

        test_values = {
            "boolean": ("true", True),
            "int": ("1", 1),
            "float": ("1.0", 1.0),
            #            'null': ('null', None),
            "date": ("1970-01-01", date(1970, 1, 1)),
            "list": ("[1, 2]", [1, 2]),
            "dict": ('{"a": 1}', {"a": 1}),
            "str": ('"test"', "test"),
        }
        for k, value_tuple in test_values.items():
            with self.subTest(msg="test_file_parsing_%s" % k, value_tuple=value_tuple):
                data = load_yaml_string(
                    """ 
                      input: {s}
                      template: !template
                        file: test_file_template.jinja.yaml
                  """.format(
                        s=value_tuple[0]
                    ),
                    {"search_paths": [current_dir]},
                )
                reference = load_yaml_string(
                    """
                      input: {s}
                      template:
                        output: {s}
                  """.format(
                        s=value_tuple[0]
                    )
                )
                self.assertEqual(data, reference)
                self.assertTrue(
                    data["template"]["output"] == value_tuple[1],  # type: ignore
                    "Generated type does not match python type!",
                )


# TODO test complex template

# TODO test usage of data and metadata
