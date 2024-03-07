from test.base.test_case import TestCase

test_context_dict_1 = {"variables": {"function": "str"}}
test_action_dict_1 = {
    "name": "Test Action",
    "module": "plucogen.v0.action.python",
    "parameters": {
        "call": "builtins:{{ variables.function }}",
        "args": ["Path: {{ path }}"],
        "kwargs": {},
        "validate": False
    },
}

class TestAction(TestCase):

    def test_python_simple_action(self):
        from plucogen.api.v0.project.action import Action

        action = Action(**test_action_dict_1)
        self.assertIsInstance(action, Action)
        print(test_context_dict_1)
        result = action.execute(test_context_dict_1)
        self.assertTrue(result)
        self.assertEqual(test_context_dict_1['function'], action.evaluate_templates("{{ function }}", test_context_dict_1))
