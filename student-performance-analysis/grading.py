"""Grading module.

Implements the automatic grading system as specified:
- Marks range 70-100: Grade A, Excellent
- Marks range 60-69: Grade B, Very Good
- Marks range 50-59: Grade C, Good
- Marks range 40-49: Grade D, Pass
- Marks range 0-39: Grade E, Fail

The grading function is designed to be reusable and independent of terminal I/O.
"""


def get_grade(marks):
    """Determine grade and remarks based on marks.

    Args:
        marks: Numeric marks (0-100).

    Returns:
        dict with keys 'grade' and 'remarks'.

    Raises:
        ValueError: If marks are not in valid range 0-100.
    """
    if not isinstance(marks, (int, float)):
        raise ValueError("Marks must be a numeric value.")
    if marks < 0 or marks > 100:
        raise ValueError("Marks must be between 0 and 100.")

    if marks >= 70:
        return {"grade": "A", "remarks": "Excellent"}
    elif marks >= 60:
        return {"grade": "B", "remarks": "Very Good"}
    elif marks >= 50:
        return {"grade": "C", "remarks": "Good"}
    elif marks >= 40:
        return {"grade": "D", "remarks": "Pass"}
    else:
        return {"grade": "E", "remarks": "Fail"}