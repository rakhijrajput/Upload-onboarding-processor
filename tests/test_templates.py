import unittest

from onboarding.templates import render_template, validate_template


class TemplateTests(unittest.TestCase):
    def test_render(self):
        self.assertEqual(render_template("Hi {{ name }}", {"name": "Tara"}), "Hi Tara")

    def test_unknown_placeholder(self):
        with self.assertRaisesRegex(ValueError, "Unknown template"):
            validate_template("Hi {{ full_name }}", {"name"})


if __name__ == "__main__":
    unittest.main()
