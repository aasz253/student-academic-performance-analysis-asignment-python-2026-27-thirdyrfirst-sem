"""Test cases for grading module.

Tests the get_grade function with various marks values.
"""

import unittest
from grading import get_grade


class TestGrading(unittest.TestCase):
    """Test cases for grade calculation."""

    def test_mark_100_grade_A(self):
        """Marks 100 should give Grade A."""
        result = get_grade(100)
        self.assertEqual(result["grade"], "A")
        self.assertEqual(result["remarks"], "Excellent")

    def test_mark_70_grade_A(self):
        """Marks 70 should give Grade A (boundary)."""
        result = get_grade(70)
        self.assertEqual(result["grade"], "A")
        self.assertEqual(result["remarks"], "Excellent")

    def test_mark_69_grade_B(self):
        """Marks 69 should give Grade B."""
        result = get_grade(69)
        self.assertEqual(result["grade"], "B")
        self.assertEqual(result["remarks"], "Very Good")

    def test_mark_60_grade_B(self):
        """Marks 60 should give Grade B (boundary)."""
        result = get_grade(60)
        self.assertEqual(result["grade"], "B")
        self.assertEqual(result["remarks"], "Very Good")

    def test_mark_59_grade_C(self):
        """Marks 59 should give Grade C."""
        result = get_grade(59)
        self.assertEqual(result["grade"], "C")
        self.assertEqual(result["remarks"], "Good")

    def test_mark_50_grade_C(self):
        """Marks 50 should give Grade C (boundary)."""
        result = get_grade(50)
        self.assertEqual(result["grade"], "C")
        self.assertEqual(result["remarks"], "Good")

    def test_mark_49_grade_D(self):
        """Marks 49 should give Grade D."""
        result = get_grade(49)
        self.assertEqual(result["grade"], "D")
        self.assertEqual(result["remarks"], "Pass")

    def test_mark_40_grade_D(self):
        """Marks 40 should give Grade D (boundary)."""
        result = get_grade(40)
        self.assertEqual(result["grade"], "D")
        self.assertEqual(result["remarks"], "Pass")

    def test_mark_39_grade_E(self):
        """Marks 39 should give Grade E."""
        result = get_grade(39)
        self.assertEqual(result["grade"], "E")
        self.assertEqual(result["remarks"], "Fail")

    def test_mark_0_grade_E(self):
        """Marks 0 should give Grade E."""
        result = get_grade(0)
        self.assertEqual(result["grade"], "E")
        self.assertEqual(result["remarks"], "Fail")

    def test_mark_invalid_101(self):
        """Marks 101 should raise ValueError."""
        with self.assertRaises(ValueError):
            get_grade(101)

    def test_mark_invalid_minus1(self):
        """Marks -1 should raise ValueError."""
        with self.assertRaises(ValueError):
            get_grade(-1)

    def test_mark_invalid_string(self):
        """Marks 'abc' should raise ValueError."""
        with self.assertRaises(ValueError):
            get_grade("abc")


if __name__ == "__main__":
    unittest.main()