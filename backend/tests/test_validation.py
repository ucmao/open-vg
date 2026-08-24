import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "app" / "utils" / "validation.py"
SPEC = importlib.util.spec_from_file_location("validation_under_test", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load validation module from {MODULE_PATH}")
validation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validation)

is_english_only = validation.is_english_only
validate_reason_english = validation.validate_reason_english


class EnglishValidationTests(unittest.TestCase):
    def test_empty_text_is_valid(self):
        self.assertTrue(is_english_only(""))
        self.assertTrue(is_english_only("   "))

    def test_printable_ascii_is_valid(self):
        self.assertTrue(is_english_only("Manual adjustment: order #123, refund $9.99."))

    def test_newlines_are_valid(self):
        self.assertTrue(is_english_only("First line\nSecond line"))

    def test_cjk_text_is_rejected(self):
        self.assertFalse(is_english_only("\u624b\u52a8\u8c03\u6574"))

    def test_emoji_is_rejected(self):
        self.assertFalse(is_english_only("Approved ✅"))

    def test_cyrillic_is_rejected(self):
        self.assertFalse(is_english_only("Одобрено"))


class ReasonValidationTests(unittest.TestCase):
    def test_none_and_blank_reasons_are_optional(self):
        self.assertEqual(validate_reason_english(None), (True, None))
        self.assertEqual(validate_reason_english("  "), (True, None))

    def test_ascii_reason_is_accepted(self):
        self.assertEqual(validate_reason_english("Customer support refund #42"), (True, None))

    def test_non_ascii_reason_returns_explanation(self):
        valid, message = validate_reason_english("\u9000\u6b3e")
        self.assertFalse(valid)
        self.assertIsNotNone(message)
        self.assertIn("English", message or "")


if __name__ == "__main__":
    unittest.main()
