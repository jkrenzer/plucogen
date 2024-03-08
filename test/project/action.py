from test.base.test_case import TestCase

test_context_dict_1 = {"variables": {"function": "str"}}
test_action_dict_1 = {
    "name": "Test Action",
    "module": "plucogen.v0.action.python",
    "parameters": {
        "call": "builtins:{{ variables.function }}",
        "args": ["Path: {{ path }}"],
        "kwargs": {},
        "validate": False,
    },
}


class TestAction(TestCase):
    def test_python_simple_action(self):
        from plucogen.api.v0.project.action.api import Action

        action = Action(**test_action_dict_1)
        self.assertIsInstance(action, Action)
        print(test_context_dict_1)
        result = action.execute(test_context_dict_1)
        self.assertTrue(result)
        self.assertEqual(
            test_context_dict_1["variables"]["function"],
            action.evaluate_templates("{{ variables.function }}", test_context_dict_1),
        )

    def test_python_simple_action_cli(self):
        from plucogen.cli import app
        from typer.testing import CliRunner
        from ast import literal_eval

        runner = CliRunner()
        test_int = 123
        result = runner.invoke(
            app,
            [
                "action",
                "run",
                "--parameter",
                "validate",
                "False",
                "--parameter",
                "call",
                '"builtins:int"',
                "--parameter",
                "args",
                f"[{test_int},]",
                "plucogen.v0.action.python",
            ],
        )
        self.assertEqual(0, result.exit_code)
        self.assertEqual(str(test_int), result.stdout)
