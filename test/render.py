import unittest
import os
from plucogen.consumers.yaml import load_yaml_file


current_dir = os.path.dirname(__file__)


class TestRender(unittest.TestCase):
    def test_render_function_api(self):
        from plucogen.generators.jinja.render import render

        text = "{{ a }}"
        data = {"a": "ok"}
        reference = "ok"
        result = render(data, text=text)
        self.assertEqual(result, reference)

    def test_render_jinja_references(self):
        from plucogen.generators.jinja.render import process_template, Environment
        from jinja2 import FileSystemLoader

        data_file = os.path.join(current_dir, "test_generation.yaml")
        reference_file = os.path.join(current_dir, "test_generation.reference.yaml")

        environment = Environment(
            loader=FileSystemLoader([current_dir]), autoescape=None
        )
        template = "{% include 'test_generation.jinja.yaml' %}"
        data = load_yaml_file(data_file)
        result_string = process_template(
            template=template, environment=environment, data=data  # type: ignore
        )
        with open(reference_file, "r") as reference_descriptor:
            self.assertEqual(result_string, reference_descriptor.read())
            return
