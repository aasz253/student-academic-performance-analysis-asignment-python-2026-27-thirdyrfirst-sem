"""Report Generator module.

Generates readable text reports for individual student performance,
class performance, top students, failed students, and unit performance.
Saves reports as text files in the reports/ directory.

Also generates HTML reports compatible with Version 3 web interface.
"""

import os
from datetime import datetime
from data_manager import REPORTS_DIR

from performance_analysis import (
    calculate_class_statistics, 
    compare_units_performance, 
    _grade_distribution_chart,
    _performance_trend_chart,
)
from ranking import rank_students, get_top_students
from grading import get_grade


def _format_grade_distribution(grade_dist):
    """Format grade distribution as a readable string."""
    lines = []
    for grade in ["A", "B", "C", "D", "E"]:
        count = grade_dist.get(grade, 0)
        lines.append(f"  {grade}: {count} student(s)")
    return "\n".join(lines)


def generate_individual_report(reg_no, student_name=None):
    """Generate an individual student performance report.

    Args:
        reg_no: Student registration number.
        student_name: Optional student name (if None, fetched from data).

    Returns:
        str: Formatted report text.
    """
    students = get_students()
    performance = calculate_student_performance(reg_no)

    if performance is None:
        return f"Report for Student {reg_no}: No performance data available."

    if student_name is None:
        student_name = students.get(reg_no, {}).get("name", "Unknown Student")

    lines = []
    lines.append("=" * 60)
    lines.append(f"INDIVIDUAL STUDENT PERFORMANCE REPORT")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Student Name: {student_name}")
    lines.append(f"Registration Number: {reg_no}")
    lines.append(f"Date Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    lines.append("-" * 40)
    lines.append("ACADEMIC PERFORMANCE")
    lines.append("-" * 40)
    lines.append(f"Total Marks: {performance['total_marks']}")
    lines.append(f"Average Marks: {performance['average_marks']}")
    lines.append(f"Overall Grade: {performance['overall_grade']}")
    lines.append(f"Remarks: {performance['overall_grade']} - Excellent/Very Good/Good/Pass/Fail")
    lines.append(f"Units Passed: {performance['units_passed']}")
    lines.append(f"Units Failed: {performance['units_failed']}")
    lines.append(f"Performance Classification: {performance['performance_classification']}")
    lines.append("")

    lines.append("-" * 40)
    lines.append("DETAILED UNIT BREAKDOWN")
    lines.append("-" * 40)

    units = get_units()
    marks_data = get_marks()
    student_marks = marks_data.get(reg_no, {})

    for unit_code, unit_info in units.items():
        unit_name = unit_info.get("unit_name", unit_code)
        if unit_code in student_marks:
            mark = student_marks[unit_code]
            if isinstance(mark, dict):
                mark = mark.get("marks", mark.get("grade", "N/A"))
            grade = student_marks.get(f"{unit_code}_grade", "N/A")
            remarks = student_marks.get(f"{unit_code}_remarks", "")
            lines.append(f"  {unit_code} ({unit_name}): {mark} - Grade {grade}")
        else:
            lines.append(f"  {unit_code} ({unit_name}): Not entered")

    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)


def generate_class_report():
    """Generate overall class performance report.

    Returns:
        str: Formatted class report text.
    """
    stats = calculate_class_statistics()

    lines = []
    lines.append("=" * 60)
    lines.append("CLASS PERFORMANCE ANALYSIS REPORT")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Total Registered Students: {stats['total_students']}")
    lines.append(f"Class Average: {stats['class_average']}")
    lines.append("")

    lines.append("-" * 40)
    lines.append("PERFORMANCE SUMMARY")
    lines.append("-" * 40)
    lines.append(f"Highest-Performing Student: {stats['highest_performing']['name']}")
    lines.append(f"  Registration: {stats['highest_performing']['registration']}")
    lines.append(f"  Average: {stats['highest_performing']['average']}")
    lines.append("")
    lines.append(f"Lowest-Performing Student: {stats['lowest_performing']['name']}")
    lines.append(f"  Registration: {stats['lowest_performing']['registration']}")
    lines.append(f"  Average: {stats['lowest_performing']['average']}")
    lines.append("")
    lines.append(f"Students Who Passed: {stats['students_passed']}")
    lines.append(f"Students Who Failed: {stats['students_failed']}")
    lines.append(f"Class Pass Percentage: {stats['pass_percentage']}%")
    lines.append("")

    lines.append("-" * 40)
    lines.append("GRADE DISTRIBUTION")
    lines.append("-" * 40)
    lines.append(_format_grade_distribution(stats['grade_distribution']))
    lines.append("")

    lines.append("=" * 60)
    return "\n".join(lines)


def generate_top_students_report(n=10):
    """Generate a report of top-performing students.

    Args:
        n: Number of top students to include.

    Returns:
        str: Formatted top students report.
    """
    top = get_top_students(n)
    lines = []
    lines.append("=" * 60)
    lines.append(f"TOP {n} PERFORMING STUDENTS")
    lines.append("=" * 60)
    lines.append("")

    for entry in top:
        lines.append(f"Rank {entry['rank']}: {entry['name']}")
        lines.append(f"  Registration: {entry['registration_number']}")
        lines.append(f"  Average Marks: {entry['average_marks']}")
        lines.append(f"  Overall Grade: {entry['overall_grade']}")
        lines.append("")

    lines.append("=" * 60)
    return "\n".join(lines)


def generate_failed_students_report():
    """Generate a report of students who failed.

    Returns:
        str: Formatted failed students report.
    """
    students_needing = get_students_needing_improvement(passing_threshold=40)
    lines = []
    lines.append("=" * 60)
    lines.append("STUDENTS REQUIRING ACADEMIC IMPROVEMENT")
    lines.append("=" * 60)
    lines.append(f"Threshold: {'Average Marks >= 40 to Pass'}")
    lines.append("")

    if not students_needing:
        lines.append("No students below the passing threshold.")
    else:
        for entry in students_needing:
            lines.append(f"Rank {entry['rank']}: {entry['name']}")
            lines.append(f"  Registration: {entry['registration_number']}")
            lines.append(f"  Average Marks: {entry['average_marks']}")
            lines.append(f"  Overall Grade: {entry['overall_grade']}")
            lines.append("")

    lines.append("=" * 60)
    return "\n".join(lines)


def generate_unit_performance_report():
    """Generate a report comparing academic unit performance.

    Returns:
        str: Formatted unit performance report.
    """
    unit_comparisons = compare_units_performance()
    lines = []
    lines.append("=" * 60)
    lines.append("ACADEMIC UNIT PERFORMANCE COMPARISON")
    lines.append("=" * 60)
    lines.append("")

    for entry in unit_comparisons:
        lines.append(f"Unit: {entry['unit_code']} ({entry['unit_name']})")
        lines.append(f"  Average Marks: {entry['average_marks']}")
        lines.append(f"  Pass Count: {entry['pass_count']}")
        lines.append(f"  Fail Count: {entry['fail_count']}")
        lines.append(f"  Pass Percentage: {entry['pass_percentage']}%")
        lines.append("")

    lines.append("=" * 60)
    return "\n".join(lines)


def save_report(report_text, filename):
    """Save a report text to the reports directory.

    Args:
        report_text: The report content to save.
        filename: Name of the file (without .txt extension).

    Returns:
        str: Full path to the saved file, or None if failed.
    """
    try:
        ensure_data_dirs()  # ensures reports dir exists
        filepath = REPORTS_DIR / f"{filename}.txt"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report_text)
        return str(filepath)
    except OSError as e:
        print(f"Error saving report: {e}")
        return None


def _html_escape(text):
    """Escape HTML special characters."""
    return (
        str(text)
        .replace("&", "&")
        .replace("<", "<")
        .replace(">", ">")
        .replace('"', """)
    )


def generate_individual_html_report(reg_no, student_name=None):
    """Generate HTML report for individual student performance.

    Args:
        reg_no: Student registration number.
        student_name: Optional student name.

    Returns:
        str: HTML report string.
    """
    students = get_students()
    performance = calculate_student_performance(reg_no)

    if performance is None:
        return f"<p>Report for Student {reg_no}: No performance data available.</p>"

    if student_name is None:
        student_name = students.get(reg_no, {}).get("name", "Unknown Student")

    html = f"""
    <div class="report-card">
        <h2>Individual Student Performance Report</h2>
        <div class="report-header">
            <h3>{_html_escape(student_name)}</h3>
            <p>Registration: {_html_escape(reg_no)}</p>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        <div class="report-details">
            <p><strong>Total Marks:</strong> {performance['total_marks']}</p>
            <p><strong>Average Marks:</strong> {performance['average_marks']}</p>
            <p><strong>Overall Grade:</strong> {performance['overall_grade']}</p>
            <p><strong>Units Passed:</strong> {performance['units_passed']}</p>
            <p><strong>Units Failed:</strong> {performance['units_failed']}</p>
            <p><strong>Performance Classification:</strong> {performance['performance_classification']}</p>
        </div>
    </div>
    """
    return html


def generate_class_html_report():
    """Generate HTML report for class performance.

    Returns:
        str: HTML report string.
    """
    stats = calculate_class_statistics()

    grade_chart = _grade_distribution_chart(stats['grade_distribution'])

    html = f"""
    <div class="report-card">
        <h2>Class Performance Analysis Report</h2>
        <div class="report-header">
            <h3>Class Overview</h3>
        </div>
        <div class="report-details">
            <p><strong>Total Registered Students:</strong> {stats['total_students']}</p>
            <p><strong>Class Average:</strong> {stats['class_average']}</p>
            <p><strong>Highest-Performing Student:</strong> {_html_escape(stats['highest_performing']['name'])} ({_html_escape(stats['highest_performing']['registration'])})</p>
            <p><strong>Lowest-Performing Student:</strong> {_html_escape(stats['lowest_performing']['name'])} ({_html_escape(stats['lowest_performing']['registration'])})</p>
            <p><strong>Students Who Passed:</strong> {stats['students_passed']}</p>
            <p><strong>Students Who Failed:</strong> {stats['students_failed']}</p>
            <p><strong>Class Pass Percentage:</strong> {stats['pass_percentage']}%</p>
        </div>
        
        <div class="report-section">
            <h3>Grade Distribution</h3>
            {grade_chart}
        </div>
    </div>
    """
    return html


def generate_top_students_html_report(n=10):
    """Generate HTML report for top-performing students.

    Args:
        n: Number of top students to include.

    Returns:
        str: HTML report string.
    """
    top = get_top_students(n)

    html = "<div class='report-card'>"
    html += f"<h2>Top {n} Performing Students</h2>"
    html += "<div class='student-list'>"

    for entry in top:
        html += f"""
        <div class="student-item">
            <span>Rank {entry['rank']}</span>
            <span>{_html_escape(entry['name'])}</span>
            <span>{_html_escape(entry['registration_number'])}</span>
            <span>{entry['average_marks']}</span>
            <span>{_html_escape(entry['overall_grade'])}</span>
        </div>
        """

    html += "</div>"
    html += "</div>"
    return html


def generate_failed_students_html_report():
    """Generate HTML report for students requiring improvement.

    Returns:
        str: HTML report string.
    """
    students_needing = get_students_needing_improvement(passing_threshold=40)

    html = "<div class='report-card'>"
    html += f"<h2>Students Requiring Academic Improvement</h2>"
    html += f"<p>Threshold: Average Marks >= 40 to Pass</p>"
    html += "<div class='student-list'>"

    if not students_needing:
        html += "<p>No students below the passing threshold.</p>"
    else:
        for entry in students_needing:
            html += f"""
            <div class="student-item">
                <span>Rank {entry['rank']}</span>
                <span>{_html_escape(entry['name'])}</span>
                <span>{_html_escape(entry['registration_number'])}</span>
                <span>{entry['average_marks']}</span>
                <span>{_html_escape(entry['overall_grade'])}</span>
            </div>
            """

    html += "</div>"
    html += "</div>"
    return html


def generate_unit_performance_html_report():
    """Generate HTML report for academic unit performance comparison.

    Returns:
        str: HTML report string.
    """
    unit_comparisons = compare_units_performance()

    html = "<div class='report-card'>"
    html += f"<h2>Academic Unit Performance Comparison</h2>"
    html += "<div class='unit-list'>"

    for entry in unit_comparisons:
        html += f"""
        <div class="unit-item">
            <span>{_html_escape(entry['unit_code'])} ({_html_escape(entry['unit_name'])})</span>
            <div class="unit-stats">
                <span>Average: {entry['average_marks']}</span>
                <span>Pass: {entry['pass_count']}</span>
                <span>Fail: {entry['fail_count']}</span>
                <span>Pass %: {entry['pass_percentage']}%</span>
            </div>
        </div>
        """

    html += "</div>"
    html += "</div>"
    return html