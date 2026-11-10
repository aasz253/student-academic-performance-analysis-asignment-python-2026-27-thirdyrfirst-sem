"""Student Manager module.

Handles student registration, search, update, and deletion operations.
Maintains students record in JSON format with unique registration numbers.

Each student record contains:
- registration_number: unique identifier
- name: student full name
- courses: list of enrolled course codes
- academic_year: string like "2024/2025"
"""

import uuid
from datetime import datetime

from data_manager import get_students, save_students, get_units, save_units


def generate_registration_number():
    """Generate a unique registration number.

    Format: REG-YYYYMMDD-XXXX where XXXX is a unique sequence.
    Returns string registration number.
    """
    date_part = datetime.now().strftime("%Y%m%d")
    # Use a short UUID fragment for uniqueness
    unique_part = uuid.uuid4().hex[:4].upper()
    return f"REG-{date_part}-{unique_part}"


def register_student(name, academic_year="2024/2025"):
    """Register a new student.

    Args:
        name: Student full name.
        academic_year: Academic year string.

    Returns:
        dict: Complete student record.
    """
    if not name or not name.strip():
        raise ValueError("Student name cannot be empty.")

    students = get_students()

    # Check if student with same name already exists (simple check)
    for reg_no, record in students.items():
        if record["name"].lower() == name.lower():
            raise ValueError(f"A student with name {name} already exists "
                             f"(reg no: {reg_no}).")

    reg_no = generate_registration_number()
    student = {
        "registration_number": reg_no,
        "name": name.strip(),
        "academic_year": academic_year,
        "courses": [],
        "date_registered": datetime.now().isoformat()
    }

    students[reg_no] = student
    save_students(students)
    return student


def view_all_students():
    """Return all registered students.

    Returns:
        dict: Mapping of registration numbers to student records.
    """
    return get_students()


def search_student(query):
    """Search for students by registration number or name.

    Args:
        query: String to search for (reg no or name part).

    Returns:
        dict: Matching student records.
    """
    students = get_students()
    query_lower = query.lower()
    results = {}

    for reg_no, record in students.items():
        if query_lower in reg_no.lower() or query_lower in record["name"].lower():
            results[reg_no] = record

    return results


def update_student(reg_no, name=None, academic_year=None):
    """Update student information.

    Args:
        reg_no: Registration number of student to update.
        name: New name (optional).
        academic_year: New academic year (optional).

    Returns:
        dict: Updated student record, or None if not found.
    """
    students = get_students()

    if reg_no not in students:
        return None

    if name is not None:
        if not name.strip():
            raise ValueError("Student name cannot be empty.")
        students[reg_no]["name"] = name.strip()

    if academic_year is not None:
        students[reg_no]["academic_year"] = academic_year

    save_students(students)
    return students[reg_no]


def delete_student(reg_no):
    """Delete a student record.

    Args:
        reg_no: Registration number of student to delete.

    Returns:
        dict: Deleted student record, or None if not found.
    """
    students = get_students()

    if reg_no not in students:
        return None

    deleted = students.pop(reg_no)
    save_students(students)
    return deleted


def assign_student_course(reg_no, course_code):
    """Assign a course to a student.

    Args:
        reg_no: Registration number.
        course_code: Course code string.

    Returns:
        dict: Updated student record, or None if student not found.
    """
    students = get_students()

    if reg_no not in students:
        return None

    if course_code not in students[reg_no]["courses"]:
        students[reg_no]["courses"].append(course_code)

    save_students(students)
    return students[reg_no]