"""Test cases for performance analysis module.

Tests individual and class performance calculations.
"""

import unittest
import json
import os
import tempfile
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from performance_analysis import (
    calculate_student_performance,
    calculate_class_statistics,
    compare_units_performance,
)
from data_manager import get_students, get_units, get_marks


class TestPerformanceAnalysis(unittest.TestCase):
    """Test cases for performance calculations."""

    def setUp(self):
        """Set up test data before each test."""
        # Save original file paths
        self.original_students_file = "data/students.json"
        self.original_units_file = "data/units.json"
        self.original_marks_file = "data/marks.json"

        # Use temporary files
        import data_manager

        self.test_students = os.path.join(tempfile.gettempdir(), "test_students_sapas.json")
        self.test_units = os.path.join(tempfile.gettempdir(), "test_units_sapas.json")
        self.test_marks = os.path.join(tempfile.gettempdir(), "test_marks_sapas.json")

        data_manager.STUDENTS_FILE = self.test_students
        data_manager.UNITS_FILE = self.test_units
        data_manager.MARKS_FILE = self.test_marks

        # Initialize empty files
        data_manager.ensure_data_dirs()

        # Register test students
        from student_manager import register_student
        self.student1 = register_student("Alice Smith", "2024/2025")
        self.student2 = register_student("Bob Jones", "2024/2025")
        self.student3 = register_student("Carol Brown", "2024/2025")

        # Add test units
        from unit_manager import add_unit
        add_unit("MTH101", "Mathematics I")
        add_unit("PHY101", "Physics I")

    def tearDown(self):
        """Restore original file paths after each test."""
        import data_manager

        data_manager.STUDENTS_FILE = self.original_students_file
        data_manager.UNITS_FILE = self.original_units_file
        data_manager.MARKS_FILE = self.original_marks_file

        # Clean up temporary files
        for f in [self.test_students, self.test_units, self.test_marks]:
            if os.path.exists(f):
                os.remove(f)

    def test_calculate_student_performance_with_marks(self):
        """Test calculating student performance with entered marks."""
        from marks_manager import enter_marks
        enter_marks(self.student1["registration_number"], "MTH101", 85)
        enter_marks(self.student1["registration_number"], "PHY101", 78)

        performance = calculate_student_performance(self.student1["registration_number"])
        self.assertIsNotNone(performance)
        self.assertEqual(performance["total_marks"], 163)
        self.assertEqual(performance["average_marks"], 81.5)
        self.assertEqual(performance["overall_grade"], "A")
        self.assertEqual(performance["units_passed"], 2)
        self.assertEqual(performance["units_failed"], 0)

    def test_calculate_student_performance_no_marks(self):
        """Test calculating performance for student with no marks."""
        performance = calculate_student_performance(self.student3["registration_number"])
        self.assertIsNotNone(performance)
        self.assertEqual(performance["average_marks"], 0)
        self.assertEqual(performance["units_passed"], 0)
        self.assertEqual(performance["units_failed"], 0)

    def test_calculate_class_statistics(self):
        """Test class statistics calculation."""
        from marks_manager import enter_marks
        enter_marks(self.student1["registration_number"], "MTH101", 85)
        enter_marks(self.student1["registration_number"], "PHY101", 78)
        enter_marks(self.student2["registration_number"], "MTH101", 55)
        enter_marks(self.student2["registration_number"], "PHY101", 42)
        enter_marks(self.student3["registration_number"], "MTH101", 30)

        stats = calculate_class_statistics()
        self.assertEqual(stats["total_students"], 3)
        self.assertGreater(stats["class_average"], 0)
        self.assertIsNotNone(stats["highest_performing"])
        self.assertIsNotNone(stats["lowest_performing"])
        self.assertEqual(stats["students_passed"], 2)  # Alice and Bob passed
        self.assertEqual(stats["students_failed"], 1)  # Carol failed
        self.assertGreater(stats["pass_percentage"], 0)

    def test_compare_units_performance(self):
        """Test unit performance comparison."""
        from marks_manager import enter_marks
        enter_marks(self.student1["registration_number"], "MTH101", 85)
        enter_marks(self.student1["registration_number"], "PHY101", 78)
        enter_marks(self.student2["registration_number"], "MTH101", 55)
        enter_marks(self.student3["registration_number"], "MTH101", 30)

        comparison = compare_units_performance()
        self.assertGreater(len(comparison), 0)
        # Math should have higher average than Physics due to marks
        mth_avg = comparison[0]["average_marks"]  # First should be highest
        self.assertGreater(mth_avg, 0)


if __name__ == "__main__":
    unittest.main()