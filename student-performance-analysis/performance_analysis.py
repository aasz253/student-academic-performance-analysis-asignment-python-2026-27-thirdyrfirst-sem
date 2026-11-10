"""Performance Analysis module.

Calculates individual student performance metrics and class-level statistics.

Provides functions for:
- Individual: total marks, average, grade, passed/failed units
- Class: overall stats, pass/fail percentages, grade distribution
"""

from data_manager import get_students, get_units, get_marks
from grading import get_grade


def calculate_student_performance(reg_no):
    """Calculate comprehensive performance metrics for a student.

    Args:
        reg_no: Student registration number.

    Returns:
        dict with keys:
            - total_marks: sum of all unit marks
            - average_marks: overall average
            - overall_grade: final grade
            - units_passed: count of units with grade D or above
            - units_failed: count of units with grade E
            - performance_classification: classification text
    """
    marks_data = get_marks()
    units = get_units()

    if reg_no not in marks_data or not marks_data[reg_no]:
        return {
            "total_marks": 0,
            "average_marks": 0,
            "overall_grade": "N/A",
            "units_passed": 0,
            "units_failed": 0,
            "performance_classification": "No marks recorded",
        }

    student_marks = marks_data[reg_no]
    total = 0
    count = 0
    passed = 0
    failed = 0

    for unit_code, entry in student_marks.items():
        # Only process numeric marks (not _grade/_remarks keys)
        if isinstance(entry, (int, float)):
            total += entry
            count += 1
        elif isinstance(entry, dict) and "marks" in entry:
            # Handle older format if needed
            marks_val = entry.get("marks", 0)
            total += marks_val
            count += 1

    if count == 0:
        return {
            "total_marks": 0,
            "average_marks": 0,
            "overall_grade": "N/A",
            "units_passed": 0,
            "units_failed": 0,
            "performance_classification": "No marks recorded",
        }

    average = total / count
    grade_info = get_grade(average)

    # Count passed/failed units based on individual unit grades
    for unit_code, entry in student_marks.items():
        if isinstance(entry, dict) and "grade" in entry:
            if entry["grade"] in ("A", "B", "C", "D"):
                passed += 1
            elif entry["grade"] == "E":
                failed += 1
        elif isinstance(entry, (int, float)):
            # No grade recorded yet - assume pass if >= 40
            if entry >= 40:
                passed += 1
            else:
                failed += 1

    # Determine academic performance classification
    if average >= 70:
        classification = "First Class"
    elif average >= 60:
        classification = "Second Class Upper"
    elif average >= 50:
        classification = "Second Class Lower"
    elif average >= 40:
        classification = "Third Class"
    else:
        classification = "Fail"

    return {
        "total_marks": round(total, 2),
        "average_marks": round(average, 2),
        "overall_grade": grade_info["grade"],
        "units_passed": passed,
        "units_failed": failed,
        "performance_classification": classification,
    }


def calculate_class_statistics():
    """Calculate overall class performance statistics.

    Returns:
        dict with class-level metrics:
            - total_students: count of registered students
            - class_average: overall average marks
            - highest_performing: reg_no and average of top student
            - lowest_performing: reg_no and average of bottom student
            - students_passed: count with overall average >= 40
            - students_failed: count with overall average < 40
            - pass_percentage: percentage of students who passed
            - grade_distribution: dict of grade -> count
    """
    students = get_students()
    marks_data = get_marks()
    averages = {}

    # Calculate average for each student
    for reg_no, student in students.items():
        student_marks = marks_data.get(reg_no, {})
        marks_list = [v for v in student_marks.values()
                      if isinstance(v, (int, float))]
        if marks_list:
            averages[reg_no] = sum(marks_list) / len(marks_list)
        else:
            averages[reg_no] = 0.0

    if not averages:
        return {
            "total_students": len(students),
            "class_average": 0,
            "highest_performing": None,
            "lowest_performing": None,
            "students_passed": 0,
            "students_failed": 0,
            "pass_percentage": 0,
            "grade_distribution": {},
        }

    class_average = sum(averages.values()) / len(averages)
    highest_reg = max(averages, key=averages.get)
    lowest_reg = min(averages, key=averages.get)

    students_passed = sum(1 for avg in averages.values() if avg >= 40)
    students_failed = sum(1 for avg in averages.values() if avg < 40)
    pass_percentage = (students_passed / len(averages)) * 100 if averages else 0

    # Grade distribution based on overall averages
    grade_dist = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0}
    for avg in averages.values():
        grade_info = get_grade(avg)
        grade_dist[grade_info["grade"]] += 1

    # Find top and lowest performing students by name
    top_student = students.get(highest_reg, {})
    lowest_student = students.get(lowest_reg, {})

    return {
        "total_students": len(students),
        "class_average": round(class_average, 2),
        "highest_performing": {
            "registration": highest_reg,
            "name": top_student.get("name", "Unknown"),
            "average": round(averages[highest_reg], 2),
        },
        "lowest_performing": {
            "registration": lowest_reg,
            "name": lowest_student.get("name", "Unknown"),
            "average": round(averages[lowest_reg], 2),
        },
        "students_passed": students_passed,
        "students_failed": students_failed,
        "pass_percentage": round(pass_percentage, 2),
        "grade_distribution": grade_dist,
    }


def compare_units_performance():
    """Compare performance across all academic units.

    Returns:
        list of dicts, each containing unit performance metrics:
            - unit_code
            - unit_name
            - average_marks
            - pass_count
            - fail_count
            - pass_percentage
    """
    units = get_units()
    marks_data = get_marks()
    results = []

    for unit_code, unit_info in units.items():
        unit_marks = []
        passed = 0
        failed = 0

        for reg_no, entries in marks_data.items():
            if unit_code in entries:
                mark = entries[unit_code]
                if isinstance(mark, (int, float)):
                    unit_marks.append(mark)
                    if mark >= 40:
                        passed += 1
                    else:
                        failed += 1

        avg = round(sum(unit_marks) / len(unit_marks), 2) if unit_marks else 0
        pass_perc = round((passed / len(unit_marks)) * 100, 2) if unit_marks else 0

        results.append({
            "unit_code": unit_code,
            "unit_name": unit_info.get("unit_name", unit_code),
            "average_marks": avg,
            "pass_count": passed,
            "fail_count": failed,
            "pass_percentage": pass_perc,
        })

    # Sort by average marks descending
    results.sort(key=lambda x: x["average_marks"], reverse=True)
    return results


def _bar_chart(value, max_value, width=20, char="█"):
    """Generate an ASCII bar chart segment.

    Args:
        value: The value to display.
        max_value: The maximum value for scaling.
        width: Bar width in characters.
        char: Character to use for the bar.

    Returns:
        str: ASCII bar string.
    """
    if max_value == 0:
        return char[0] * 1
    filled = int(value / max_value * width)
    return char[0] * filled + " " * (width - filled)


def _grade_distribution_chart(grade_dist):
    """Generate an ASCII bar chart for grade distribution.

    Args:
        grade_dist: Dict of grade -> count (e.g., {"A": 5, "B": 3}).

    Returns:
        str: Formatted grade distribution chart.
    """
    grades = ["A", "B", "C", "D", "E"]
    max_count = max(grade_dist.values()) if grade_dist.values() else 0
    max_width = 30
    lines = []

    for grade in grades:
        count = grade_dist.get(grade, 0)
        bar = _bar_chart(count, max_count, max_width)
        lines.append(f"  {grade}: {bar} ({count})")

    return "\n".join(lines)


def _performance_trend_chart(students_data, max_width=40):
    """Generate an ASCII bar chart for student performance comparison.

    Args:
        students_data: List of dicts with 'name' and 'average_marks' keys.
        max_width: Maximum bar width in characters.

    Returns:
        str: Formatted performance comparison chart.
    """
    if not students_data:
        return "No data available"

    max_marks = max(s["average_marks"] for s in students_data)
    min_marks = min(s["average_marks"] for s in students_data) if students_data else 0
    range_width = max_marks - min_marks
    if range_width == 0:
        range_width = 1

    lines = []
    for student in students_data:
        normalized = (student["average_marks"] - min_marks) / range_width * max_width
        filled = int(normalized)
        bar = "█" * filled + " " * (max_width - filled)
        lines.append(f"  {student['name'][:15]:15}: {bar} {student['average_marks']:.1f}")

    return "\n".join(lines)