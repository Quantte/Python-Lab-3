import string
import unittest
from unittest.mock import patch

try:
    import variant_10
except ModuleNotFoundError:
    variant_10 = None


class GenerateKeyTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(variant_10, "variant_10.py is not implemented yet")

    @patch("variant_10.random.choices", side_effect=[["A", "B"], ["C", "D"]])
    @patch("variant_10.random.sample", side_effect=[["6", "5", "4"], ["3", "2", "1"]])
    def test_uses_last_three_digits_in_first_block_and_first_three_in_second(
        self, mock_sample, mock_choices
    ):
        self.assertEqual(variant_10.generate_key("123456"), "654AB-321CD 0975")

    @patch("variant_10.random.choices", side_effect=[["A", "A"], ["B", "B"]])
    @patch("variant_10.random.sample", side_effect=[["0", "0", "1"], ["0", "0", "0"]])
    def test_preserves_leading_zeros(self, mock_sample, mock_choices):
        self.assertEqual(variant_10.generate_key("000001"), "001AA-000BB 0001")

    @patch("variant_10.random.choices", side_effect=[["X", "Y"], ["Z", "Q"]])
    @patch("variant_10.random.sample", side_effect=[["9", "9", "9"], ["9", "9", "9"]])
    def test_formats_largest_sum_as_four_digits(self, mock_sample, mock_choices):
        self.assertEqual(variant_10.generate_key("999999"), "999XY-999ZQ 1998")

    def test_generated_key_has_expected_structure(self):
        key = variant_10.generate_key("726911")
        self.assertEqual(key.count("-"), 1)
        first, second_with_total = key.split("-")
        second, total = second_with_total.split(" ")

        self.assertEqual(len(first), 5)
        self.assertEqual(len(second), 5)
        self.assertEqual(len(total), 4)
        self.assertCountEqual(first[:3], "911")
        self.assertCountEqual(second[:3], "726")
        self.assertTrue(all(letter in string.ascii_uppercase for letter in first[3:]))
        self.assertTrue(all(letter in string.ascii_uppercase for letter in second[3:]))
        self.assertEqual(int(total), int(first[:3]) + int(second[:3]))

    def test_rejects_invalid_input(self):
        invalid_values = [
            "",
            "12345",
            "1234567",
            "12345A",
            "123 56",
            "١٢٣٤٥٦",
        ]

        for value in invalid_values:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    variant_10.generate_key(value)


if __name__ == "__main__":
    unittest.main()
