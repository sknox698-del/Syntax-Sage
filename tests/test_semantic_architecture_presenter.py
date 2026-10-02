import unittest

from app.semantic_architecture_presenter import (
    format_verified_semantic_architecture,
)


class TestSemanticArchitecturePresenter(unittest.TestCase):

    def setUp(self):
        self.facts = {
            "modules": [
                {
                    "path": "app/language_router.py",
                    "depends_on": [],
                    "used_by": ["app/main.py"],
                },
                {
                    "path": "app/unknown_module.py",
                    "depends_on": [],
                    "used_by": [],
                },
            ]
        }

    def test_presents_verified_module_role(self):
        answer = format_verified_semantic_architecture(
            self.facts
        )

        self.assertIn(
            "Module: app/language_router.py",
            answer,
        )

        self.assertIn(
            (
                "Verified responsibility: Identifies supported "
                "programming languages from filename extensions "
                "using a fixed extension map."
            ),
            answer,
        )

    def test_unknown_module_does_not_get_invented_role(self):
        answer = format_verified_semantic_architecture(
            self.facts
        )

        self.assertIn(
            "Module: app/unknown_module.py",
            answer,
        )

        self.assertIn(
            "Verified responsibility: Not established.",
            answer,
        )

    def test_runtime_inference_boundary_is_present(self):
        answer = format_verified_semantic_architecture(
            self.facts
        )

        self.assertIn(
            (
                "Static dependency relationships do not prove "
                "runtime execution order or call flow."
            ),
            answer,
        )


if __name__ == "__main__":
    unittest.main()