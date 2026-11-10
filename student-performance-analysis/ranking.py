"""Student Ranking module.

Ranks students according to their average marks and identifies
top performers and students needing academic improvement.

Handles students with equal average marks using secondary sort by name.
"""

from data_manager import get_students, get_marks
from performance_analysis import calculate_student_performance


def rank_students():
    """Rank all students by their average marks.

    Returns:
        list of dicts, each containing:
            - registration_number
            - name
            - average_marks
            - overall_grade
            - rank (1-indexed)
    """
    students = get_students()
    marks_data = get_marks()
    rankings = []

    for reg_no, student in students.items():
        performance = calculate_student_performance(reg_no)
        if performance is None:
            avg = 0
            grade = "N/A"
        else:
            avg = performance["average_marks"]
            grade = performance["overall_grade"]

        rankings.append({
            "registration_number": reg_no,
            "name": student.get("name", "Unknown"),
            "average_marks": avg,
            "overall_grade": grade,
        })

    # Sort by average marks descending, then by name ascending for ties
    rankings.sort(key=lambda x: (-x["average_marks"], x["name"].lower()))

    # Assign ranks
    for i, entry in enumerate(rankings):
        entry["rank"] = i + 1

    return rankings


def get_top_students(n=10):
    """Get the top N students by average marks.

    Args:
        n: Number of top students to return.

    Returns:
        list of dicts ranked by average marks.
    """
    rankings = rank_students()
    return rankings[:n]


def get_students_needing_improvement(passing_threshold=40):
    """Identify students who need academic improvement.

    Args:
        passing_threshold: Minimum average to be considered passing.

    Returns:
        list of dicts with student info and average marks,
        sorted by average (lowest first).
    """
    rankings = rank_students()
    needing = [entry for entry in rankings
               if entry["average_marks"] < passing_threshold]
    return needing