from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from plan import plan_problems


class PlanTests(unittest.TestCase):
    def setUp(self):
        self.plan = {"format": "produto", "brief": {"objective": "conversao", "audience": "salões",
                     "problem_or_desire": "organizar agenda", "benefit": "centralizar horários",
                     "desired_action": "pedir demonstração", "offer": "app", "cta_destination": "link fornecido",
                     "missing_inputs": []}, "hook_candidates": [{"visual": "demonstração"} for _ in range(5)],
                     "hook": "Veja a agenda em uso", "tool_plan": [{"tool": "FFmpeg", "status": "planejado"}],
                     "research": {"sources": []}}

    def test_consistent_plan(self):
        self.assertEqual(plan_problems(self.plan), ([], []))

    def test_empty_manifest_is_not_a_plan(self):
        errors, _ = plan_problems({})
        self.assertGreater(len(errors), 3)

    def test_invalid_manifest_types_are_reported(self):
        for value in ([], {"brief": ["unexpected"]}, {"brief": {"missing_inputs": "not a list"}}):
            with self.subTest(value=value):
                self.assertTrue(plan_problems(value)[0])

    def test_missing_inputs_can_be_declared_without_fabrication(self):
        self.plan["brief"]["cta_destination"] = ""
        self.plan["brief"]["missing_inputs"] = ["cta_destination"]
        self.assertEqual(plan_problems(self.plan), ([], ["cta_destination"]))

    def test_undeclared_missing_destination_is_an_error(self):
        self.plan["brief"]["cta_destination"] = ""
        self.assertTrue(any("cta_destination" in x for x in plan_problems(self.plan)[0]))

    def test_incomplete_hooks_and_invalid_tool_status_are_errors(self):
        self.plan["hook_candidates"] = []
        self.plan["tool_plan"][0]["status"] = "testado-sem-evidência"
        errors, _ = plan_problems(self.plan)
        self.assertTrue(any("hook_candidates" in x for x in errors))
        self.assertTrue(any("tool_plan" in x for x in errors))


if __name__ == "__main__":
    unittest.main()
