"""Data Manager module for handling JSON file operations.

Handles loading, saving, and creating data files for students, units, and marks.
Uses the json module from Python's standard library.
"""

import json
from pathlib import Path


BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"

STUDENTS_FILE = DATA_DIR / "students.json"
UNITS_FILE = DATA_DIR / "units.json"
MARKS_FILE = DATA_DIR / "marks.json"


def _convert_path(filepath):
    """Convert filepath to Path if it's a string."""
    if isinstance(filepath, str):
        return Path(filepath)
    return filepath


def ensure_data_dirs():
    """Create data directory and default files if they don't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    students_path = _convert_path(STUDENTS_FILE)
    units_path = _convert_path(UNITS_FILE)
    marks_path = _convert_path(MARKS_FILE)

    if not students_path.exists():
        students_path.write_text("{}")

    if not units_path.exists():
        units_path.write_text("{}")

    if not marks_path.exists():
        marks_path.write_text("{")


def load_json(filepath):
    """Load and return JSON data from a file.

    Args:
        filepath: Path or string path to the JSON file.

    Returns:
        dict or empty dict if file is empty/corrupted.
    """
    try:
        filepath = _convert_path(filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def save_json(filepath, data):
    """Save data to a JSON file.

    Args:
        filepath: Path or string path to the JSON file.
        data: Data to save (dict).
    """
    try:
        filepath = _convert_path(filepath)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except OSError as e:
        print(f"Error saving file: {e}")


def get_students():
    """Load students record from JSON file."""
    ensure_data_dirs()
    return load_json(STUDENTS_FILE)


def save_students(students):
    """Save students record to JSON file."""
    ensure_data_dirs()
    save_json(STUDENTS_FILE, students)


def get_units():
    """Load units record from JSON file."""
    ensure_data_dirs()
    return load_json(UNITS_FILE)


def save_units(units):
    """Save units record to JSON file."""
    ensure_data_dirs()
    save_json(UNITS_FILE, units)


def get_marks():
    """Load marks record from JSON file."""
    ensure_data_dirs()
    return load_json(MARKS_FILE)


def save_marks(marks):
    """Save marks record to JSON file."""
    ensure_data_dirs()
    save_json(MARKS_FILE, marks)