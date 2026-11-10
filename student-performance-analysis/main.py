"""Main module - Command Line Interface for Student Academic Performance Analysis System.

Provides a professional terminal menu-driven interface for managing
student records, academic units, marks, and performance analysis.

All business logic is kept separate in dedicated modules;
this file handles user I/O only.
"""

import sys
import os
import json
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

try:
    from api import handler
except ImportError:
    handler = None

from data_manager import ensure_data_dirs

from student_manager import (
    register_student,
    view_all_students,
    search_student,
    update_student,
    delete_student,
    assign_student_course,
)
from unit_manager import add_unit, view_all_units, search_unit, assign_unit_to_student
from marks_manager import enter_marks, view_marks_by_student, view_marks_by_unit, calculate_class_averages
from grading import get_grade
from performance_analysis import calculate_student_performance, calculate_class_statistics, compare_units_performance
from ranking import rank_students, get_top_students, get_students_needing_improvement
from report_generator import (
    generate_individual_report,
    generate_class_report,
    generate_top_students_report,
    generate_failed_students_report,
    generate_unit_performance_report,
    save_report,
)


def clear_screen():
    """Clear the terminal screen."""
    print("\n" * 50)


def display_header():
    """Display the application header."""
    print("=" * 60)
    print(" STUDENT ACADEMIC PERFORMANCE ANALYSIS ")
    print("=" * 60)
    print()


def display_main_menu():
    """Display the main menu options."""
    print("1. Student Management")
    print("2. Academic Unit Management")
    print("3. Enter and Manage Marks")
    print("4. Individual Performance Analysis")
    print("5. Class Performance Analysis")
    print("6. Student Rankings")
    print("7. Academic Reports")
    print("8. System Information")
    print("9. Exit")
    print()


def student_management_submenu():
    """Submenu for student management operations."""
    while True:
        clear_screen()
        display_header()
        print(" STUDENT MANAGEMENT ")
        print("-" * 40)
        print("1. Register New Student")
        print("2. View All Students")
        print("3. Search Student")
        print("4. Update Student Information")
        print("5. Delete Student Record")
        print("6. Assign Course to Student")
        print("7. Back to Main Menu")
        print()

        choice = input("Select an option: ").strip()

        if choice == "1":
            name = input("Enter student name: ").strip()
            year = input("Enter academic year (e.g., 2024/2025): ").strip() or "2024/2025"
            try:
                student = register_student(name, year)
                print(f"\nStudent registered successfully!")
                print(f"Registration Number: {student['registration_number']}")
                print(f"Name: {student['name']}")
            except ValueError as e:
                print(f"\nError: {e}")
            input("\nPress Enter to continue...")

        elif choice == "2":
            students = view_all_students()
            clear_screen()
            display_header()
            print(" ALL REGISTERED STUDENTS ")
            print("-" * 40)
            if not students:
                print("No students registered yet.")
            else:
                for reg_no, record in students.items():
                    print(f"  {reg_no}: {record['name']} (Year: {record.get('academic_year', 'N/A')})")
            input("\nPress Enter to continue...")

        elif choice == "3":
            query = input("Enter registration number or name to search: ").strip()
            results = search_student(query)
            clear_screen()
            display_header()
            print(f" SEARCH RESULTS for '{query}' ")
            print("-" * 40)
            if not results:
                print("No matching students found.")
            else:
                for reg_no, record in results.items():
                    print(f"  {reg_no}: {record['name']} (Year: {record.get('academic_year', 'N/A')})")
            input("\nPress Enter to continue...")

        elif choice == "4":
            reg_no = input("Enter registration number to update: ").strip()
            name = input("Enter new name (leave blank to keep unchanged): ").strip()
            year = input("Enter new academic year (leave blank to keep unchanged): ").strip()
            try:
                updated = update_student(reg_no, name if name else None, year if year else None)
                if updated is None:
                    print(f"\nStudent with registration number {reg_no} not found.")
                else:
                    print(f"\nStudent updated successfully!")
                    print(f"Name: {updated['name']}")
                    print(f"Year: {updated.get('academic_year', 'N/A')}")
            except ValueError as e:
                print(f"\nError: {e}")
            input("\nPress Enter to continue...")

        elif choice == "5":
            reg_no = input("Enter registration number to delete: ").strip()
            confirm = input(f"Are you sure you want to delete {reg_no}? (y/n): ").strip().lower()
            if confirm == "y":
                deleted = delete_student(reg_no)
                if deleted is None:
                    print(f"\nStudent with registration number {reg_no} not found.")
                else:
                    print(f"\nStudent record deleted successfully!")
                    print(f"Deleted: {deleted['name']}")
            input("\nPress Enter to continue...")

        elif choice == "6":
            reg_no = input("Enter student registration number: ").strip()
            course = input("Enter course code: ").strip()
            try:
                updated = assign_student_course(reg_no, course)
                if updated is None:
                    print(f"\nStudent with registration number {reg_no} not found.")
                else:
                    print(f"\nCourse {course} assigned to student {updated['name']}.")
            except ValueError as e:
                print(f"\nError: {e}")
            input("\nPress Enter to continue...")

        elif choice == "7":
            break

        else:
            print("\nInvalid option. Please try again.")
            input("Press Enter to continue...")


def unit_management_submenu():
    """Submenu for academic unit management operations."""
    while True:
        clear_screen()
        display_header()
        print(" ACADEMIC UNIT MANAGEMENT ")
        print("-" * 40)
        print("1. Add New Unit")
        print("2. View All Units")
        print("3. Search Unit")
        print("4. Assign Unit to Student")
        print("5. Back to Main Menu")
        print()

        choice = input("Select an option: ").strip()

        if choice == "1":
            code = input("Enter unit code (e.g., MTH101): ").strip().upper()
            name = input("Enter unit name: ").strip()
            try:
                unit = add_unit(code, name)
                if unit is None:
                    print(f"\nUnit code '{code}' already exists. No duplicate allowed.")
                else:
                    print(f"\nUnit added successfully!")
                    print(f"Code: {unit['unit_code']}")
                    print(f"Name: {unit['unit_name']}")
            except ValueError as e:
                print(f"\nError: {e}")
            input("\nPress Enter to continue...")

        elif choice == "2":
            units = view_all_units()
            clear_screen()
            display_header()
            print(" ALL REGISTERED UNITS ")
            print("-" * 40)
            if not units:
                print("No units registered yet.")
            else:
                for code, record in units.items():
                    students_count = len(record.get("assigned_students", []))
                    print(f"  {code}: {record['unit_name']} (Enrolled: {students_count})")
            input("\nPress Enter to continue...")

        elif choice == "3":
            query = input("Enter unit code or name to search: ").strip()
            results = search_unit(query)
            clear_screen()
            display_header()
            print(f" SEARCH RESULTS for '{query}' ")
            print("-" * 40)
            if not results:
                print("No matching units found.")
            else:
                for code, record in results.items():
                    students_count = len(record.get("assigned_students", []))
                    print(f"  {code}: {record['unit_name']} (Enrolled: {students_count})")
            input("\nPress Enter to continue...")

        elif choice == "4":
            code = input("Enter unit code: ").strip().upper()
            reg_no = input("Enter student registration number: ").strip()
            try:
                assigned = assign_unit_to_student(code, reg_no)
                if assigned is None:
                    print(f"\nUnit '{code}' or student {reg_no} not found.")
                else:
                    print(f"\nStudent {reg_no} assigned to unit {code}.")
            except ValueError as e:
                print(f"\nError: {e}")
            input("\nPress Enter to continue...")

        elif choice == "5":
            break

        else:
            print("\nInvalid option. Please try again.")
            input("Press Enter to continue...")


def marks_management_submenu():
    """Submenu for marks entry and management."""
    while True:
        clear_screen()
        display_header()
        print(" ENTER AND MANAGE MARKS ")
        print("-" * 40)
        print("1. Enter Marks for Student")
        print("2. View Student Marks")
        print("3. View Marks by Unit")
        print("4. Class Average Marks")
        print("5. Back to Main Menu")
        print()

        choice = input("Select an option: ").strip()

        if choice == "1":
            reg_no = input("Enter student registration number: ").strip()
            code = input("Enter unit code: ").strip().upper()
            marks_input = input("Enter marks (0-100): ").strip()
            try:
                entered = enter_marks(reg_no, code, marks_input)
                print(f"\nMarks entered successfully!")
                print(f"Student: {reg_no}")
                print(f"Unit: {code}")
                print(f"Marks: {entered.get(code, 'N/A')}")
                print(f"Grade: {entered.get(f'{code}_grade', 'N/A')}")
            except ValueError as e:
                print(f"\nError: {e}")
            input("\nPress Enter to continue...")

        elif choice == "2":
            reg_no = input("Enter student registration number: ").strip()
            marks = view_marks_by_student(reg_no)
            clear_screen()
            display_header()
            print(f" MARKS FOR STUDENT {reg_no} ")
            print("-" * 40)
            if marks is None:
                print("No marks found for this student.")
            else:
                for key, value in marks.items():
                    if key.endswith("_grade") or key.endswith("_remarks"):
                        continue
                    unit_key = key.replace("_marks", "") if "_marks" in key else key
                    print(f"  {unit_key}: {value}")
            input("\nPress Enter to continue...")

        elif choice == "3":
            code = input("Enter unit code: ").strip().upper()
            marks = view_marks_by_unit(code)
            clear_screen()
            display_header()
            print(f" MARKS FOR UNIT {code} ")
            print("-" * 40)
            if marks is None:
                print("No marks found for this unit.")
            else:
                for reg_no, mark in marks.items():
                    student = get_students().get(reg_no, {}).get("name", reg_no)
                    print(f"  {reg_no} ({student}): {mark}")
            input("\nPress Enter to continue...")

        elif choice == "4":
            averages = calculate_class_averages()
            clear_screen()
            display_header()
            print(" CLASS AVERAGE MARKS ")
            print("-" * 40)
            if not averages:
                print("No marks entered yet.")
            else:
                for reg_no, avg in sorted(averages.items(), key=lambda x: -x[1])[:10]:
                    student = get_students().get(reg_no, {}).get("name", reg_no)
                    print(f"  {reg_no} ({student}): {avg:.2f}")
            input("\nPress Enter to continue...")

        elif choice == "5":
            break

        else:
            print("\nInvalid option. Please try again.")
            input("Press Enter to continue...")


def individual_analysis_submenu():
    """Submenu for individual performance analysis."""
    while True:
        clear_screen()
        display_header()
        print(" INDIVIDUAL PERFORMANCE ANALYSIS ")
        print("-" * 40)
        print("1. Student Performance Report")
        print("2. Back to Main Menu")
        print()

        choice = input("Select an option: ").strip()

        if choice == "1":
            reg_no = input("Enter student registration number: ").strip()
            student = get_students().get(reg_no, {})
            name = student.get("name", "Unknown")
            report = generate_individual_report(reg_no, name)
            clear_screen()
            display_header()
            print(report)
            print()
            # Offer to save report
            save = input("Save this report? (y/n): ").strip().lower()
            if save == "y":
                filename = input("Enter filename (without .txt): ").strip()
                saved = save_report(report, filename)
                if saved:
                    print(f"Report saved to: {saved}")
            input("\nPress Enter to continue...")

        elif choice == "2":
            break

        else:
            print("\nInvalid option. Please try again.")
            input("Press Enter to continue...")


def class_analysis_submenu():
    """Submenu for class performance analysis."""
    while True:
        clear_screen()
        display_header()
        print(" CLASS PERFORMANCE ANALYSIS ")
        print("-" * 40)
        print("1. Generate Class Report")
        print("2. Back to Main Menu")
        print()

        choice = input("Select an option: ").strip()

        if choice == "1":
            report = generate_class_report()
            clear_screen()
            display_header()
            print(report)
            print()
            save = input("Save this report? (y/n): ").strip().lower()
            if save == "y":
                filename = input("Enter filename (without .txt): ").strip()
                saved = save_report(report, filename)
                if saved:
                    print(f"Report saved to: {saved}")
            input("\nPress Enter to continue...")

        elif choice == "2":
            break

        else:
            print("\nInvalid option. Please try again.")
            input("Press Enter to continue...")


def rankings_submenu():
    """Submenu for student rankings."""
    while True:
        clear_screen()
        display_header()
        print(" STUDENT RANKINGS ")
        print("-" * 40)
        print("1. Show Top 10 Students")
        print("2. Students Needing Improvement")
        print("3. Back to Main Menu")
        print()

        choice = input("Select an option: ").strip()

        if choice == "1":
            top = get_top_students(10)
            clear_screen()
            display_header()
            print(" TOP 10 STUDENTS ")
            print("-" * 40)
            if not top:
                print("No students ranked yet.")
            else:
                for entry in top:
                    print(f"  Rank {entry['rank']}: {entry['name']}")
                    print(f"    Registration: {entry['registration_number']}")
                    print(f"    Average: {entry['average_marks']}")
                    print(f"    Grade: {entry['overall_grade']}")
                    print()
            input("Press Enter to continue...")

        elif choice == "2":
            needing = get_students_needing_improvement()
            clear_screen()
            display_header()
            print(" STUDENTS NEEDING IMPROVEMENT ")
            print("-" * 40)
            if not needing:
                print("All students are passing (average >= 40).")
            else:
                for entry in needing:
                    print(f"  Rank {entry['rank']}: {entry['name']}")
                    print(f"    Registration: {entry['registration_number']}")
                    print(f"    Average: {entry['average_marks']}")
                    print(f"    Grade: {entry['overall_grade']}")
                    print()
            input("Press Enter to continue...")

        elif choice == "3":
            break

        else:
            print("\nInvalid option. Please try again.")
            input("Press Enter to continue...")


def reports_submenu():
    """Submenu for academic reports."""
    while True:
        clear_screen()
        display_header()
        print(" ACADEMIC REPORTS ")
        print("-" * 40)
        print("1. Individual Student Report")
        print("2. Class Performance Report")
        print("3. Top Students Report")
        print("4. Students Requiring Improvement Report")
        print("5. Unit Performance Comparison Report")
        print("6. Back to Main Menu")
        print()

        choice = input("Select an option: ").strip()

        if choice == "1":
            reg_no = input("Enter student registration number: ").strip()
            student = get_students().get(reg_no, {})
            name = student.get("name", "Unknown")
            report = generate_individual_report(reg_no, name)
            clear_screen()
            display_header()
            print(report)
            print()
            save = input("Save this report? (y/n): ").strip().lower()
            if save == "y":
                filename = input("Enter filename (without .txt): ").strip()
                saved = save_report(report, filename)
                if saved:
                    print(f"Report saved to: {saved}")
            input("\nPress Enter to continue...")

        elif choice == "2":
            report = generate_class_report()
            clear_screen()
            display_header()
            print(report)
            print()
            save = input("Save this report? (y/n): ").strip().lower()
            if save == "y":
                filename = input("Enter filename (without .txt): ").strip()
                saved = save_report(report, filename)
                if saved:
                    print(f"Report saved to: {saved}")
            input("\nPress Enter to continue...")

        elif choice == "3":
            try:
                n = input("How many top students? (default 10): ").strip()
                n = int(n) if n else 10
            except ValueError:
                n = 10
            report = generate_top_students_report(n)
            clear_screen()
            display_header()
            print(report)
            print()
            save = input("Save this report? (y/n): ").strip().lower()
            if save == "y":
                filename = input("Enter filename (without .txt): ").strip()
                saved = save_report(report, filename)
                if saved:
                    print(f"Report saved to: {saved}")
            input("\nPress Enter to continue...")

        elif choice == "4":
            report = generate_failed_students_report()
            clear_screen()
            display_header()
            print(report)
            print()
            save = input("Save this report? (y/n): ").strip().lower()
            if save == "y":
                filename = input("Enter filename (without .txt): ").strip()
                saved = save_report(report, filename)
                if saved:
                    print(f"Report saved to: {saved}")
            input("\nPress Enter to continue...")

        elif choice == "5":
            report = generate_unit_performance_report()
            clear_screen()
            display_header()
            print(report)
            print()
            save = input("Save this report? (y/n): ").strip().lower()
            if save == "y":
                filename = input("Enter filename (without .txt): ").strip()
                saved = save_report(report, filename)
                if saved:
                    print(f"Report saved to: {saved}")
            input("\nPress Enter to continue...")

        elif choice == "6":
            break

        else:
            print("\nInvalid option. Please try again.")
            input("Press Enter to continue...")


def system_info_submenu():
    """Display system information."""
    clear_screen()
    display_header()
    print(" SYSTEM INFORMATION ")
    print("-" * 40)
    print(" Student Academic Performance Analysis System (SAPAS)")
    print(" Version 1.0 - Command Line Interface")
    print()
    print(" Data Persistence: JSON files")
    print(" Storage Location: data/ directory")
    print(" Report Location: reports/ directory")
    print()
    print(" Modules:")
    print("  - student_manager.py  Student registration & management")
    print("  - unit_manager.py     Academic unit management")
    print("  - marks_manager.py    Marks entry & validation")
    print("  - grading.py          Automatic grading system")
    print("  - performance_analysis.py Student & class analysis")
    print("  - ranking.py          Student ranking & improvement")
    print("  - report_generator.py Report generation")
    print("  - data_manager.py     Data file management")
    print()
    print(" Main Menu Options: 1-9")
    print()
    input("\nPress Enter to continue...")


def main():
    """Main application entry point.

    Initializes data directories and runs the CLI menu loop.
    """
    ensure_data_dirs()

    while True:
        display_header()
        display_main_menu()
        choice = input("Select an option: ").strip()

        if choice == "1":
            student_management_submenu()
        elif choice == "2":
            unit_management_submenu()
        elif choice == "3":
            marks_management_submenu()
        elif choice == "4":
            individual_analysis_submenu()
        elif choice == "5":
            class_analysis_submenu()
        elif choice == "6":
            rankings_submenu()
        elif choice == "7":
            reports_submenu()
        elif choice == "8":
            system_info_submenu()
        elif choice == "9":
            print("\nThank you for using Student Academic Performance Analysis System.")
            print("Goodbye!")
            sys.exit(0)
        else:
            print("\nInvalid option. Please select 1-9.")
            input("Press Enter to continue...")


if __name__ == "__main__":
    main()