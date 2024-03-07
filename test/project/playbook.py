import plucogen
from plucogen.api.v0.resource import PathTemplate, Path
from test.base import TestCase

from .action import test_action_dict_1, test_context_dict_1

class TestPlaybook(TestCase):
    def test_simple_init(self):
        from plucogen.api.v0.project import Playbook

        playbook_dict = {
            "name": "Test Playbook",
            "actions": [
                test_action_dict_1
            ]
        }
        playbook = Playbook(**playbook_dict)
        self.assertIsInstance(playbook, Playbook)
        results = playbook.execute(test_context_dict_1)
        self.assertTrue(results[0])


