"""Unit Manager module.

Handles academic unit/subject management including adding units,
assigning units to students, and preventing duplicate registrations.

Each unit record contains:
- unit_code: unique identifier (e.g., "MTH101")
- unit_name: full name of the subject
- assigned_students: list of registration numbers enrolled in the unit
"""

from data_manager import get_units, save_units, get_students


def add_unit(unit_code, unit_name):
    """Add a new academic unit.

    Args:
        unit_code: Unique unit code (e.g., "PHY101").
        unit_name: Full name of the unit.

    Returns:
        dict: Created unit record, or None if unit code already exists.

    Raises:
        ValueError: If unit code or name is empty.
    """
    if not unit_code or not unit_name:
        raise ValueError("Unit code and unit name must not be empty.")

    units = get_units()

    # Check for duplicate unit code (case-insensitive)
    for existing_code in units:
        if existing_code.lower() == unit_code.lower():
            print(f"Warning: Unit code '{unit_code}' already exists.")
            return None

    unit = {
        "unit_code": unit_code.strip().upper(),
        "unit_name": unit_name.strip(),
        "assigned_students": []
    }

    units[unit["unit_code"]] = unit
    save_units(units)
    return unit


def view_all_units():
    """Return all registered units.

    Returns:
        dict: Mapping of unit codes to unit records.
    """
    return get_units()


def search_unit(query):
    """Search for units by code or name.

    Args:
        query: String to search for (unit code or name part).

    Returns:
        dict: Matching unit records.
    """
    units = get_units()
    query_lower = query.lower()
    results = {}

    for code, record in units.items():
        if query_lower in code.lower() or query_lower in record["unit_name"].lower():
            results[code] = record

    return results


def assign_unit_to_student(unit_code, reg_no):
    """Assign a student to a unit.

    Args:
        unit_code: Unit code string.
        reg_no: Student registration number.

    Returns:
        dict: Updated unit record, or None if unit/student not found.
    """
    units = get_units()
    students = get_students()

    if unit_code not in units:
        return None

    if reg_no not in students:
        return None

    if reg_no not in units[unit_code]["assigned_students"]:
        units[unit_code]["assigned_students"].append(reg_no)

    save_units(units)

    # Also add unit to student's courses
    student = students[reg_no]
    if unit_code not in student["courses"]:
        student["courses"].append(unit_code)
        save_students(students)

    return units[unit_code]


def unassign_unit_from_student(unit_code, reg_no):
    """Remove a student from a unit.

    Args:
        unit_code: Unit code string.
        reg_no: Student registration number.

    Returns:
        dict: Updated unit record, or None if not found.
    """
    units = get_units()

    if unit_code not in units:
        return None

    if reg_no in units[unit_code]["assigned_students"]:
        units[unit_code]["assigned_students"].remove(reg_no)

    save_units(units)
    return units[unit_code]