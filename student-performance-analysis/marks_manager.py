"""Marks Manager module.

Handles entering, updating, and validating marks for students in academic units.
Validates that marks are between 0 and 100.

Each marks record structure:
- student_registration_number: mapping of unit_code -> marks
"""

from data_manager import get_marks, save_marks, get_students, get_units
from grading import get_grade


def enter_marks(reg_no, unit_code, marks):
        """Enter marks for a student in a specific unit.

        Args:
                reg_no: Student registration number.
                unit_code: Unit code string.
                marks: Numeric marks (0-100).

        Returns:
                dict: Updated marks record, or None if student/unit not found.

        Raises:
                ValueError: If marks are not in valid range.
        """
        try:
                marks_float = float(marks)
        except (ValueError, TypeError):
                raise ValueError("Marks must be a numeric value.")

        if marks_float < 0 or marks_float > 100:
                raise ValueError("Marks must be between 0 and 100.")

        students = get_students()
        if reg_no not in students:
                raise ValueError(f"Student with registration number {reg_no} not found.")

        units = get_units()
        if unit_code not in units:
                raise ValueError(f"Unit with code {unit_code} not found.")

        marks_data = get_marks()

        if reg_no not in marks_data:
                marks_data[reg_no] = {}

        marks_data[reg_no][unit_code] = marks_float

        grade_info = get_grade(marks_float)
        marks_data[reg_no][f"{unit_code}_grade"] = grade_info["grade"]
        marks_data[reg_no][f"{unit_code}_remarks"] = grade_info["remarks"]

        save_marks(marks_data)
        return marks_data[reg_no]


def update_marks(reg_no, unit_code, new_marks):
        """Update previously entered marks for a student.

        Args:
                reg_no: Student registration number.
                unit_code: Unit code string.
                new_marks: New numeric marks (0-100).

        Returns:
                dict: Updated marks entry, or None if not found.

        Raises:
                ValueError: If new marks are not in valid range.
        """
        try:
                new_marks_float = float(new_marks)
        except (ValueError, TypeError):
                raise ValueError("Marks must be a numeric value.")

        if new_marks_float < 0 or new_marks_float > 100:
                raise ValueError("Marks must be between 0 and 100.")

        marks_data = get_marks()

        if reg_no not in marks_data or unit_code not in marks_data[reg_no]:
                return None

        marks_data[reg_no][unit_code] = new_marks_float

        grade_info = get_grade(new_marks_float)
        marks_data[reg_no][f"{unit_code}_grade"] = grade_info["grade"]
        marks_data[reg_no][f"{unit_code}_remarks"] = grade_info["remarks"]

        save_marks(marks_data)
        return marks_data[reg_no]


def view_marks_by_student(reg_no):
        """View all marks for a specific student.

        Args:
                reg_no: Student registration number.

        Returns:
                dict: Marks entries for the student, or None if not found.
        """
        marks_data = get_marks()
        if reg_no not in marks_data:
                return None
        return marks_data[reg_no]


def view_marks_by_unit(unit_code):
        """View all marks for a specific unit across all students.

        Args:
                unit_code: Unit code string.

        Returns:
                dict: Mapping of reg_no -> marks, or None if unit not found.
        """
        marks_data = get_marks()
        results = {}

        for reg_no, entries in marks_data.items():
                if unit_code in entries:
                        results[reg_no] = entries[unit_code]

        return results if results else None


def calculate_class_averages():
        """Calculate average marks for all students.

        Returns:
                dict: Mapping of reg_no -> average marks.
        """
        marks_data = get_marks()
        students = get_students()
        averages = {}

        for reg_no, entries in marks_data.items():
                marks_list = [v for k, v in entries.items() if isinstance(v, (int, float))]
                if marks_list:
                        averages[reg_no] = sum(marks_list) / len(marks_list)
                else:
                        averages[reg_no] = 0.0

        return averages