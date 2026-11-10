"""Test cases for student manager module.

Tests student registration, search, update, and deletion.
"""

import unittest
import json
import os
import tempfile
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from student_manager import (
    register_student,
    view_all_students,
    search_student,
    update_student,
    delete_student,
    generate_registration_number,
)


class TestStudentManager(unittest.TestCase):
    """Test cases for student operations."""

    def setUp(self):
        """Set up test environment with temporary data."""
        self.original_students_file = "data/students.json"

    def test_generate_registration_number(self):
        """Test that registration numbers are generated correctly."""
        reg_no = generate_registration_number()
        self.assertTrue(reg_no.startswith("REG-"))
        # Check format: REG-YYYYMMDD-XXXX (at least 4+4+4=12 chars)
        parts = reg_no.split("-")
        self.assertEqual(len(parts), 3)
        self.assertEqual(parts[0], "REG")

    def test_register_new_student(self):
        """Test registering a new student."""
        # Save original file and backup
        import data_manager
        original_path = data_manager.STUDENTS_FILE
        test_path = os.path.join(tempfile.gettempdir(), "test_sapas_students.json")
        data_manager.STUDENTS_FILE = test_path
        data_manager.ensure_data_dirs()

        try:
            student = register_student("John Doe", "2024/2025")
            self.assertEqual(student["name"], "John Doe")
            self.assertEqual(student["academic_year"], "2024/2025")
            self.assertIn("registration_number", student)

            # Verify data was saved
            with open(test_path, "r") as f:
                data = json.load(f)
            self.assertIn(student["registration_number"], data)
        finally:
            # Restore and clean up
            data_manager.STUDENTS_FILE = original_path
            if os.path.exists(test_path):
                os.remove(test_path)

    def test_register_student_duplicate_name(self):
        """Test that registering duplicate name raises ValueError."""
        import data_manager
        original_path = data_manager.STUDENTS_FILE
        test_path = os.path.join(tempfile.gettempdir(), "test_sapas_students2.json")
        data_manager.STUDENTS_FILE = test_path
        data_manager.ensure_data_dirs()

        try:
            register_student("Jane Smith", "2024/2025")
            with self.assertRaises(ValueError):
                register_student("Jane Smith", "2024/2025")
        finally:
            data_manager.STUDENTS_FILE = original_path
            if os.path.exists(test_path):
                os.remove(test_path)

    def test_search_student_by_registration(self):
        """Test searching student by registration number."""
        import data_manager
        original_path = data_manager.STUDENTS_FILE
        test_path = os.path.join(tempfile.gettempdir(), "test_sapas_students3.json")
        data_manager.STUDENTS_FILE = test_path
        data_manager.ensure_data_dirs()

        try:
            register_student("Alice Johnson", "2024/2025")
            results = search_student("Alice Johnson")
            self.assertEqual(len(results), 1)
            reg_no = list(results.keys())[0]
            # Search by partial reg no
            results2 = search_student(reg_no[:8])
            self.assertEqual(len(results2), 1)
        finally:
            data_manager.STUDENTS_FILE = original_path
            if os.path.exists(test_path):
                os.remove(test_path)

    def test_update_student(self):
        """Test updating student information."""
        import data_manager
        original_path = data_manager.STUDENTS_FILE
        test_path = os.path.join(tempfile.gettempdir(), "test_sapas_students4.json")
        data_manager.STUDENTS_FILE = test_path
        data_manager.ensure_data_dirs()

        try:
            student = register_student("Bob Wilson", "2024/2025")
            reg_no = student["registration_number"]

            # Update name
            updated = update_student(reg_no, name="Robert Wilson")
            self.assertIsNotNone(updated)
            self.assertEqual(updated["name"], "Robert Wilson")

            # Update year
            updated = update_student(reg_no, academic_year="2025/2026")
            self.assertIsNotNone(updated)
            self.assertEqual(updated["academic_year"], "2025/2026")
        finally:
            data_manager.STUDENTS_FILE = original_path
            if os.path.exists(test_path):
                os.remove(test_path)

    def test_delete_student(self):
        """Test deleting student record."""
        import data_manager
        original_path = data_manager.STUDENTS_FILE
        test_path = os.path.join(tempfile.gettempdir(), "test_sapas_students5.json")
        data_manager.STUDENTS_FILE = test_path
        data_manager.ensure_data_dirs()

        try:
            student = register_student("Carol White", "2024/2025")
            reg_no = student["registration_number"]

            # Delete
            result = delete_student(reg_no)
            self.assertIsNotNone(result)
            self.assertEqual(result["name"], "Carol White")

            # Verify deleted
            remaining = view_all_students()
            self.assertNotIn(reg_no, remaining)
        finally:
            data_manager.STUDENTS_FILE = original_path
            if os.path.exists(test_path):
                os.remove(test_path)


if __name__ == "__main__":
    unittest.main()