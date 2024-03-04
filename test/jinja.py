import unittest
import os

from plucogen.handlers.yaml import load_yaml_file
from .base import TestCase

current_dir = os.path.dirname(__file__)


class TestJinjaExtensions(TestCase):
    def test_jinja_ext_metadata(self):
        from jinja2 import Environment, FileSystemLoader

        data_file = os.path.join(current_dir, "test_generation.yaml")
        template_file = "test_generation.jinja.yaml"
        reference_file = os.path.join(current_dir, "test_generation.reference.yaml")

        environment = Environment(
            loader=FileSystemLoader([current_dir]),
            autoescape=False,
            extensions=["plucogen.generators.jinja.extensions.YAMLMetadata"],
        )
        template = environment.get_template(template_file)
        data = load_yaml_file(data_file)
        result_string = template.render(data)
        with open(reference_file, "r") as reference_descriptor:
            self.assertEqual(result_string, reference_descriptor.read())
            return
