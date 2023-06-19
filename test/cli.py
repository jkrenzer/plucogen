import unittest
import os

current_dir = os.path.dirname(__file__)


class TestCLI(unittest.TestCase):
    def test_cli_file_generation(self):
        import plucogen

        data_file = os.path.join(current_dir, "test_generation.yaml")
        template_file = os.path.join(current_dir, "test_generation.jinja.yaml")
        reference_file = os.path.join(current_dir, "test_generation.reference.yaml")
        result_file = "/tmp/test_generation.result.yaml"
        cli_args = [
            "--log-level",
            "debug",
            "generate",
            "jinja",
            "-d",
            data_file,
            "-o",
            result_file,
            template_file,
        ]
        return_code = plucogen.cli.main(cli_args)
        self.assertEqual(return_code, 0)
        with open(result_file, "r") as result_descriptor, open(
            reference_file, "r"
        ) as reference_descriptor:
            self.assertEqual(result_descriptor.read(), reference_descriptor.read())
            return
        self.fail("Unable to compare result and reference files!")
