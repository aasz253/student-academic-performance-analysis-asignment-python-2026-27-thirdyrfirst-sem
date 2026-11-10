# Student Academic Performance Analysis System (SAPAS)

## Project Description

Student Academic Performance Analysis System (SAPAS) is a Python-based command-line application designed for educational institutions to manage student academic records, process examination marks, calculate grades, and analyze academic performance at individual and class levels.

This project was developed as an academic project for an Introduction to Python course, demonstrating practical understanding of fundamental Python programming concepts.

## Problem Statement

Educational institutions need an efficient system to manage student records, track academic performance across multiple subjects, calculate grades automatically, and generate analytical reports. Manual management of academic records is time-consuming, error-prone, and lacks centralized data storage for analysis.

## Version History

### Version 1 - Command Line Interface (Current)
- CLI menu-driven interface
- JSON data persistence
- All core functionality implemented
- Tested with 23 unit tests
- No third-party dependencies

### Version 2 - Web Backend (Planned)
- FastAPI backend exposing Python functions through REST APIs
- JSON API responses for student records and analytical results
- Enable HTML front-end to communicate with Python backend

### Version 3 - Web Interface (Current Development)
- HTML for page structure
- CSS for interface design
- JavaScript for interactive data presentation
- Charts using Chart.js for performance visualization
- Dashboards for academic performance overview
- Report generation in HTML format

## Version 3 - Web Interface Features

### HTML Structure
- Student dashboard with statistics cards
- Grade distribution charts using Chart.js
- Unit performance comparison charts
- Navigation between different sections (Students, Units, Marks, Reports)

### CSS Styling
- Responsive design working on mobile and desktop
- Color scheme consistent with the project branding
- Card-based layout for reports and statistics
- Hover effects and smooth transitions

### JavaScript Interactivity
- Chart.js integration for dynamic charts
- AJAX-style data loading from Python backend
- Section navigation without full page reloads
- Real-time statistics updates

### Chart Integration
- Grade distribution bar charts
- Unit performance comparison bar charts
- Student performance ranking charts
- All charts generated from Python backend data

### Report Generation
- HTML format reports for individual students
- HTML format class performance reports
- HTML format top students lists
- HTML format unit performance comparisons
- Reports can be printed or saved

### API Compatibility
The Version 3 web interface communicates with the existing Python backend through:
- Reusable functions from `grading.py`, `data_manager.py`, `performance_analysis.py`, etc.
- JSON data structures suitable for API responses
- No code duplication - web interface uses the same backend modules

### Future Enhancements (Version 4+)
- User authentication and role-based access
- Integration with existing school information systems
- Advanced statistical analysis and trend prediction
- Multi-semester support
- Export reports to PDF/Excel format

## Features

### Student Management
- Register new students with unique registration numbers
- View all registered students
- Search students by registration number or name
- Update student information
- Delete student records

### Academic Unit Management
- Add academic units/subjects (e.g., Mathematics, Physics)
- Assign units to students
- Prevent duplicate unit registrations
- View all registered units

### Marks Management
- Enter marks for individual students in each unit
- Validate marks are between 0 and 100
- Update previously entered marks
- Record marks for multiple academic units

### Automatic Grading System
- Grade A: 70-100 (Excellent)
- Grade B: 60-69 (Very Good)
- Grade C: 50-59 (Good)
- Grade D: 40-49 (Pass)
- Grade E: 0-39 (Fail)

### Performance Analysis
- Individual student: total marks, average, grade, passed/failed units
- Class: overall average, highest/lowest performers, pass/fail percentages
- Unit comparison: performance across all academic units
- Student ranking by average marks

### Report Generation
- Individual student performance reports
- Class performance analysis reports
- Top-performing students reports
- Students requiring improvement reports
- Academic unit performance comparison reports
- Reports saved as text files in reports/ directory

## Technologies Used

- **Python 3.x**: Core programming language
- **Standard Library Modules**:
  - `json`: Data persistence and storage
  - `os` and `pathlib`: File and directory management
  - `datetime`: Timestamp generation for records
  - `statistics`: Statistical calculations
  - `collections`: Grade distribution and counting
  - `unittest`: Testing framework
- **No third-party dependencies** (Version 1)

## Python Concepts Demonstrated

1. **Modular Programming**: Code separated into logical modules (student_manager, unit_manager, marks_manager, grading, performance_analysis, ranking, report_generator, data_manager)
2. **Functions**: Reusable functions with clear inputs and outputs
3. **Error Handling**: Try-except blocks for graceful error recovery
4. **Input Validation**: Checking user inputs and data integrity
5. **Data Structures**: Dictionaries, lists, and tuples for data organization
6. **Object-Oriented Concepts**: While not using classes extensively, the code demonstrates structured programming
7. **File I/O**: Reading and writing JSON files for data persistence
8. **Unit Testing**: Using unittest to verify correctness of functions
9. **Control Flow**: Conditional statements and loops for decision making
10. **String Formatting**: f-strings and format methods for readable output

## Project Directory Structure

```
student-performance-analysis/
│
├── main.py                          # Main CLI application entry point
├── data_manager.py                  # JSON file operations
├── grading.py                       # Automatic grading system
├── student_manager.py               # Student registration & management
├── unit_manager.py                  # Academic unit management
├── marks_manager.py                 # Marks entry & validation
├── performance_analysis.py          # Individual & class analysis
├── ranking.py                       # Student ranking & improvement
├── report_generator.py              # Report generation
│
├── data/                          # Data persistence directory
│   ├── students.json
│   ├── units.json
│   └── marks.json
│
├── reports/                       # Generated reports directory
│
├── tests/                       # Unit test directory
│   ├── test_grading.py
│   ├── test_students.py
│   └── test_analysis.py
│
├── screenshots/                   # Screenshots directory
│
├── requirements.txt              # Project dependencies
├── .gitignore                     # Git ignore file
└── README.md                      # This file
```

## Installation Instructions

1. Ensure Python 3.x is installed on your system
2. Clone or download this repository
3. No additional packages need to be installed - this project uses Python's standard library only
4. Navigate to the project directory
5. Run the application: `python3 main.py`

## How to Run the Application

```bash
cd student-performance-analysis
python3 main.py
```

The application will display a professional terminal menu:

```
 STUDENT ACADEMIC PERFORMANCE ANALYSIS 

1. Student Management
2. Academic Unit Management
3. Enter and Manage Marks
4. Individual Performance Analysis
5. Class Performance Analysis
6. Student Rankings
7. Academic Reports
8. System Information
9. Exit

Select an option:
```

Navigate the menu using number keys (1-9). The system automatically creates data files on first run.

## Sample Outputs

### Entering Student Records
```
 STUDENT MANAGEMENT 

1. Register New Student
2. View All Students
...

Select an option: 1
Enter student name: Alice Smith
Enter academic year (e.g., 2024/2025): 2024/2025

Student registered successfully!
Registration Number: REG-20241101-89F4
Name: Alice Smith
Academic Year: 2024/2025
```

### Entering Marks
```
 ENTER AND MANAGE MARKS 

1. Enter Marks for Student
2. View Student Marks
...

Select an option: 1
Enter student registration number: REG-20241101-89F4
Enter unit code: MTH101
Enter marks (0-100): 85

Marks entered successfully!
Student: REG-20241101-89F4
Unit: MTH101
Marks: 85
Grade: A
```

### Class Performance Report
```
 CLASS PERFORMANCE ANALYSIS REPORT 

============================================================
CLASS PERFORMANCE ANALYSIS REPORT
============================================================

Total Registered Students: 3
Class Average: 58.33

Highest-Performing Student: Alice Smith
  Registration: REG-20241101-89F4
  Average: 85.00

Lowest-Performing Student: Carol White
  Registration: REG-20241101-D641
  Average: 23.33

Students Who Passed: 1
Students Who Failed: 2
Class Pass Percentage: 33.33%

GRADE DISTRIBUTION
  A: 1 student
  B: 1 student
  C: 0 students
  D: 0 students
  E: 1 student
```

## Testing

All core functionality is tested using Python's built-in `unittest` framework. Tests cover:

- Grade calculations for all mark ranges
- Invalid marks handling (below 0, above 100, non-numeric)
- Student registration and duplicate prevention
- Student search, update, and deletion
- Average calculations and performance metrics
- Student rankings
- Pass/fail percentages
- Empty dataset handling

To run tests:
```bash
python3 -m unittest discover -s tests
```

All 23 tests pass successfully.

## Future Improvements

### Version 2 - Web Backend
- Introduce FastAPI to expose existing Python functions through REST APIs
- Enable HTML front-end to communicate with Python backend
- Support JSON API responses for student records and analytical results

### Version 3 - Web Interface
- Build HTML pages for student management interface
- Add CSS for interface design and styling
- Implement JavaScript for interactive data presentation
- Create charts and graphical academic dashboards
- Add visualization of grade distributions and performance trends

### Additional Features
- Export reports in multiple formats (PDF, Excel)
- Support for different academic years and semesters
- User authentication and role-based access
- Integration with existing school information systems
- Advanced statistical analysis and trend prediction

## Author Information

**Project**: Student Academic Performance Analysis System (SAPAS)
**Course**: Introduction to Python
**Level**: Academic Project - Version 1 (Command-Line Interface)
**Developer**: Python Software Engineer

This project demonstrates fundamental Python programming concepts including modular programming, file I/O, data validation, error handling, and algorithm implementation. The architecture is designed to support future web interface development in Version 2 and Version 3.