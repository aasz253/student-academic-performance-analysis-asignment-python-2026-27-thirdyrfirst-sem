"""SAPAS Python API - Local HTTP Server & Vercel Serverless Function.

Provides REST API endpoints and static file serving for the
Student Academic Performance Analysis System.
Uses only Python standard library - no third-party dependencies required.

Compatible with:
- Vercel Serverless Functions (@vercel/python class handler)
- Local HTTP Server (python3 api.py)
- Event-based calls handler(event, context)
"""

import json
import os
import shutil
import tempfile
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote
from typing import Dict, Any, Optional

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DATA_DIR = os.path.join(PROJECT_DIR, "data")
REPORTS_DIR = os.path.join(PROJECT_DIR, "reports")
STATIC_DIR = os.path.join(PROJECT_DIR, "static")
TEMPLATES_DIR = os.path.join(PROJECT_DIR, "templates")

# Fallback to parent data directory if data is stored one level up
if not os.path.exists(os.path.join(BASE_DATA_DIR, "students.json")):
    parent_data = os.path.join(os.path.dirname(PROJECT_DIR), "data")
    if os.path.exists(os.path.join(parent_data, "students.json")):
        BASE_DATA_DIR = parent_data


def get_data_dir() -> str:
    """Return a writable data directory, copying seed data to /tmp if read-only (e.g. on Vercel)."""
    # Check if local directory is writable
    if os.path.exists(BASE_DATA_DIR) and os.access(BASE_DATA_DIR, os.W_OK):
        return BASE_DATA_DIR

    # When running in serverless environments (Vercel / AWS Lambda) filesystem is read-only
    tmp_data = os.path.join(tempfile.gettempdir(), "sapas_data")
    os.makedirs(tmp_data, exist_ok=True)

    for filename in ["students.json", "units.json", "marks.json"]:
        dst = os.path.join(tmp_data, filename)
        src = os.path.join(BASE_DATA_DIR, filename)
        if not os.path.exists(dst):
            if os.path.exists(src):
                try:
                    shutil.copy2(src, dst)
                except Exception:
                    pass
            else:
                try:
                    with open(dst, "w", encoding="utf-8") as f:
                        f.write("{}")
                except Exception:
                    pass
    return tmp_data


def get_file_path(filename: str) -> str:
    """Return the active path for a data file."""
    return os.path.join(get_data_dir(), filename)


def path_remainder(path: str, marker: str) -> str:
    """Return the decoded part of a path after marker (supports slashes in registration numbers)."""
    if marker in path:
        return unquote(path.split(marker, 1)[1]).strip("/")
    return ""


def load_json_file(filepath: str) -> dict:
    """Load JSON from file with graceful error handling."""
    # If the file doesn't exist in active directory, check BASE_DATA_DIR
    if not os.path.exists(filepath):
        base_fallback = os.path.join(BASE_DATA_DIR, os.path.basename(filepath))
        if os.path.exists(base_fallback):
            filepath = base_fallback

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return {}
            data = json.loads(content)
            return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, IOError):
        return {}


def save_json_file(filepath: str, data: dict) -> None:
    """Save JSON to file with indentation."""
    target_dir = os.path.dirname(filepath)
    os.makedirs(target_dir, exist_ok=True)
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except IOError:
        # If write fails (read-only filesystem), fallback to /tmp
        tmp_dir = os.path.join(tempfile.gettempdir(), "sapas_data")
        os.makedirs(tmp_dir, exist_ok=True)
        tmp_filepath = os.path.join(tmp_dir, os.path.basename(filepath))
        try:
            with open(tmp_filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except IOError:
            pass


def get_student(reg_no: str) -> Optional[dict]:
    """Get student by registration number."""
    return load_json_file(get_file_path("students.json")).get(reg_no)


def get_all_students() -> dict:
    """Get all students."""
    return load_json_file(get_file_path("students.json"))


def add_student(reg_no: str, name: str, academic_year: str = "2024/2025") -> dict:
    """Add a new student."""
    students_path = get_file_path("students.json")
    students = load_json_file(students_path)
    student = {
        "registration_number": reg_no,
        "name": name,
        "academic_year": academic_year,
        "courses": [],
        "date_registered": datetime.now().isoformat(),
    }
    students[reg_no] = student
    save_json_file(students_path, students)
    return student


def update_student(reg_no: str, name: Optional[str] = None, academic_year: Optional[str] = None) -> Optional[dict]:
    """Update student information."""
    students_path = get_file_path("students.json")
    students = load_json_file(students_path)
    if reg_no not in students:
        return None
    if name:
        students[reg_no]["name"] = name
    if academic_year:
        students[reg_no]["academic_year"] = academic_year
    save_json_file(students_path, students)
    return students[reg_no]


def delete_student(reg_no: str) -> Optional[dict]:
    """Delete student record."""
    students_path = get_file_path("students.json")
    students = load_json_file(students_path)
    if reg_no not in students:
        return None
    deleted = students.pop(reg_no)
    save_json_file(students_path, students)
    return deleted


def get_all_units() -> dict:
    """Get all registered units."""
    return load_json_file(get_file_path("units.json"))


def add_unit(unit_code: str, unit_name: str) -> dict:
    """Add a new academic unit."""
    units_path = get_file_path("units.json")
    units = load_json_file(units_path)
    unit = {"unit_code": unit_code, "unit_name": unit_name}
    units[unit_code] = unit
    save_json_file(units_path, units)
    return unit


def get_student_marks(reg_no: str) -> dict:
    """Get marks for a student."""
    return load_json_file(get_file_path("marks.json")).get(reg_no, {})


def get_all_marks() -> dict:
    """Get all marks records."""
    return load_json_file(get_file_path("marks.json"))


def record_marks(reg_no: str, unit_code: str, marks_val: float) -> dict:
    """Record or update marks for a student in a unit."""
    marks_path = get_file_path("marks.json")
    marks_data = load_json_file(marks_path)
    if reg_no not in marks_data:
        marks_data[reg_no] = {}
    marks_float = float(marks_val)
    marks_data[reg_no][unit_code] = marks_float
    grade_info = get_grade(marks_float)
    marks_data[reg_no][f"{unit_code}_grade"] = grade_info["grade"]
    marks_data[reg_no][f"{unit_code}_remarks"] = grade_info["remarks"]
    save_json_file(marks_path, marks_data)
    return marks_data[reg_no]


def get_grade(marks: float) -> dict:
    """Determine grade and remarks based on marks."""
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


def calculate_student_performance(reg_no: str) -> dict:
    """Calculate student performance metrics."""
    student_marks = get_student_marks(reg_no)

    if not student_marks:
        return {
            "registration_number": reg_no,
            "total_marks": 0,
            "average_marks": 0,
            "overall_grade": "N/A",
            "units_passed": 0,
            "units_failed": 0,
            "performance_classification": "No marks recorded",
        }

    total = 0
    count = 0
    passed = 0
    failed = 0

    for k, v in student_marks.items():
        if not k.endswith("_grade") and not k.endswith("_remarks") and isinstance(v, (int, float)):
            total += v
            count += 1
            if v >= 40:
                passed += 1
            else:
                failed += 1

    if count == 0:
        return {
            "registration_number": reg_no,
            "total_marks": 0,
            "average_marks": 0,
            "overall_grade": "N/A",
            "units_passed": 0,
            "units_failed": 0,
            "performance_classification": "No marks recorded",
        }

    average = total / count
    grade_info = get_grade(average)

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
        "registration_number": reg_no,
        "total_marks": round(total, 2),
        "average_marks": round(average, 2),
        "overall_grade": grade_info["grade"],
        "units_passed": passed,
        "units_failed": failed,
        "performance_classification": classification,
    }


def calculate_class_statistics() -> dict:
    """Calculate class-level statistics."""
    all_students = get_all_students()
    all_marks = get_all_marks()

    if not all_students:
        return {
            "total_students": 0,
            "class_average": 0,
            "highest_performing": None,
            "lowest_performing": None,
            "students_passed": 0,
            "students_failed": 0,
            "pass_percentage": 0,
            "grade_distribution": {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0},
        }

    averages = {}
    for reg_no in all_students:
        student_marks = all_marks.get(reg_no, {})
        marks_list = [v for k, v in student_marks.items()
                      if not k.endswith("_grade") and not k.endswith("_remarks") and isinstance(v, (int, float))]
        if marks_list:
            averages[reg_no] = sum(marks_list) / len(marks_list)
        else:
            averages[reg_no] = 0.0

    class_average = sum(averages.values()) / len(averages) if averages else 0
    highest_reg = max(averages, key=averages.get) if averages else None
    lowest_reg = min(averages, key=averages.get) if averages else None

    students_passed = sum(1 for avg in averages.values() if avg >= 40)
    students_failed = sum(1 for avg in averages.values() if avg < 40)
    pass_percentage = (students_passed / len(averages)) * 100 if averages else 0

    grade_dist = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0}
    for avg in averages.values():
        g = get_grade(avg)
        grade_dist[g["grade"]] += 1

    top_student = all_students.get(highest_reg, {}) if highest_reg else {}
    lowest_student = all_students.get(lowest_reg, {}) if lowest_reg else {}

    return {
        "total_students": len(all_students),
        "class_average": round(class_average, 2),
        "highest_performing": {
            "registration": highest_reg,
            "name": top_student.get("name", "Unknown"),
            "average": round(averages[highest_reg], 2) if highest_reg else 0,
        } if highest_reg else None,
        "lowest_performing": {
            "registration": lowest_reg,
            "name": lowest_student.get("name", "Unknown"),
            "average": round(averages[lowest_reg], 2) if lowest_reg else 0,
        } if lowest_reg else None,
        "students_passed": students_passed,
        "students_failed": students_failed,
        "pass_percentage": round(pass_percentage, 2),
        "grade_distribution": grade_dist,
    }


def get_student_summary(reg_no: str) -> Optional[dict]:
    """Compile comprehensive student summary including profile, performance, units breakdown, and class benchmarks."""
    student = get_student(reg_no)
    if not student:
        return None
    perf = calculate_student_performance(reg_no)
    marks_raw = get_student_marks(reg_no)
    all_units = get_all_units()

    units_list = []
    for k, v in marks_raw.items():
        if not k.endswith("_grade") and not k.endswith("_remarks") and isinstance(v, (int, float)):
            unit_info = all_units.get(k, {})
            units_list.append({
                "unit_code": k,
                "unit_name": unit_info.get("unit_name", k),
                "marks": v,
                "grade": marks_raw.get(f"{k}_grade", get_grade(v)["grade"]),
                "remarks": marks_raw.get(f"{k}_remarks", get_grade(v)["remarks"]),
                "status": "Passed" if v >= 40 else "Failed"
            })

    # Sort units by unit code
    units_list.sort(key=lambda u: u["unit_code"])
    class_stats = calculate_class_statistics()

    return {
        "student": student,
        "performance": perf,
        "units": units_list,
        "class_average": class_stats.get("class_average", 0),
        "total_class_students": class_stats.get("total_students", 0)
    }


def authenticate_student(identifier: str) -> Optional[dict]:
    """Authenticate a student by registration number or name."""
    ident = (identifier or "").strip().lower()
    if not ident:
        return None
    students = get_all_students()

    # 1. Exact registration match
    for reg_no, s in students.items():
        if reg_no.strip().lower() == ident:
            return s

    # 2. Match by student name
    for reg_no, s in students.items():
        if s.get("name", "").strip().lower() == ident:
            return s

    return None


def get_rankings() -> list:
    """Calculate and return students ranked by average marks."""
    all_students = get_all_students()
    rank_list = []
    for reg_no, info in all_students.items():
        perf = calculate_student_performance(reg_no)
        rank_list.append({
            "registration_number": reg_no,
            "name": info.get("name", ""),
            "average_marks": perf["average_marks"],
            "grade": perf["overall_grade"],
            "classification": perf["performance_classification"],
        })
    rank_list.sort(key=lambda s: s["average_marks"], reverse=True)
    for idx, item in enumerate(rank_list, start=1):
        item["rank"] = idx
    return rank_list


def handle_event(event: dict, context=None) -> dict:
    """Handle event-style calls for test suites or serverless wrappers."""
    path = event.get("path", "/")
    method = event.get("httpMethod", "GET")
    query = event.get("queryStringParameters") or {}
    body_raw = event.get("body") or "{}"

    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
    }

    try:
        body = json.loads(body_raw) if isinstance(body_raw, str) else body_raw
    except Exception:
        body = {}

    if method == "OPTIONS":
        return {"statusCode": 204, "headers": headers, "body": ""}

    # Strip trailing slash
    clean_path = path.rstrip("/") if len(path) > 1 else path

    if clean_path in ["/api/login", "/login"]:
        if method == "POST":
            ident = body.get("registration_number") or body.get("reg_no") or body.get("name") or ""
            student = authenticate_student(ident)
            if student:
                summary = get_student_summary(student["registration_number"])
                return {"statusCode": 200, "headers": headers, "body": json.dumps({"success": True, "student": student, "summary": summary})}
            return {"statusCode": 401, "headers": headers, "body": json.dumps({"success": False, "error": "Student registration number not found."})}
        return {"statusCode": 405, "headers": headers, "body": json.dumps({"error": "Method not allowed"})}

    elif clean_path in ["/api/student-summary", "/student-summary"]:
        reg_no = query.get("registration") or query.get("reg_no") or ""
        if isinstance(reg_no, list):
            reg_no = reg_no[0] if reg_no else ""
        summary = get_student_summary(unquote(str(reg_no)))
        if summary:
            return {"statusCode": 200, "headers": headers, "body": json.dumps(summary)}
        return {"statusCode": 404, "headers": headers, "body": json.dumps({"error": "Student summary not found"})}

    elif clean_path.startswith("/api/student-summary/") or clean_path.startswith("/student-summary/"):
        reg_no = path_remainder(clean_path, "student-summary/")
        summary = get_student_summary(reg_no)
        if summary:
            return {"statusCode": 200, "headers": headers, "body": json.dumps(summary)}
        return {"statusCode": 404, "headers": headers, "body": json.dumps({"error": "Student summary not found"})}

    elif clean_path in ["/api/students", "/students"]:
        if method == "POST":
            reg_no = body.get("registration_number", "")
            name = body.get("name", "")
            year = body.get("academic_year", "2024/2025")
            if not reg_no or not name:
                return {"statusCode": 400, "headers": headers, "body": json.dumps({"error": "registration_number and name required"})}
            student = add_student(reg_no, name, year)
            return {"statusCode": 200, "headers": headers, "body": json.dumps(student)}
        return {"statusCode": 200, "headers": headers, "body": json.dumps(get_all_students())}

    elif clean_path.startswith("/api/students/") or clean_path.startswith("/students/"):
        reg_no = path_remainder(clean_path, "students/")
        student = get_student(reg_no)
        if student:
            return {"statusCode": 200, "headers": headers, "body": json.dumps(student)}
        return {"statusCode": 404, "headers": headers, "body": json.dumps({"error": "Student not found"})}

    elif clean_path in ["/api/units", "/units"]:
        if method == "POST":
            code = body.get("unit_code", "")
            name = body.get("unit_name", "")
            if not code or not name:
                return {"statusCode": 400, "headers": headers, "body": json.dumps({"error": "unit_code and unit_name required"})}
            unit = add_unit(code, name)
            return {"statusCode": 200, "headers": headers, "body": json.dumps(unit)}
        return {"statusCode": 200, "headers": headers, "body": json.dumps(get_all_units())}

    elif clean_path in ["/api/marks", "/marks"]:
        if method == "POST":
            reg_no = body.get("registration_number", "")
            unit_code = body.get("unit_code", "")
            m_val = body.get("marks")
            if not reg_no or not unit_code or m_val is None:
                return {"statusCode": 400, "headers": headers, "body": json.dumps({"error": "Missing required fields"})}
            res = record_marks(reg_no, unit_code, float(m_val))
            return {"statusCode": 200, "headers": headers, "body": json.dumps(res)}
        reg = query.get("registration", [""])[0] if isinstance(query.get("registration"), list) else query.get("registration", "")
        if reg:
            return {"statusCode": 200, "headers": headers, "body": json.dumps(get_student_marks(reg))}
        return {"statusCode": 200, "headers": headers, "body": json.dumps(get_all_marks())}

    elif clean_path.startswith("/api/marks/") or clean_path.startswith("/marks/"):
        reg_no = path_remainder(clean_path, "marks/")
        return {"statusCode": 200, "headers": headers, "body": json.dumps(get_student_marks(reg_no))}

    elif clean_path.startswith("/api/performance/") or clean_path.startswith("/performance/"):
        reg_no = path_remainder(clean_path, "performance/")
        return {"statusCode": 200, "headers": headers, "body": json.dumps(calculate_student_performance(reg_no))}

    elif clean_path in ["/api/class", "/class"]:
        stats = calculate_class_statistics()
        return {"statusCode": 200, "headers": headers, "body": json.dumps(stats)}

    elif clean_path in ["/api/rankings", "/api/ranking", "/rankings"]:
        return {"statusCode": 200, "headers": headers, "body": json.dumps({"rankings": get_rankings()})}

    elif clean_path.startswith("/api/grade") or clean_path.startswith("/grade"):
        marks_param = query.get("marks", [""])[0] if isinstance(query.get("marks"), list) else query.get("marks", "")
        if not marks_param and clean_path.count("/") >= 2:
            marks_param = clean_path.split("/")[-1]
        try:
            m = float(marks_param)
            return {"statusCode": 200, "headers": headers, "body": json.dumps(get_grade(m))}
        except (ValueError, TypeError):
            return {"statusCode": 400, "headers": headers, "body": json.dumps({"error": "Invalid marks value"})}

    return {"statusCode": 404, "headers": headers, "body": json.dumps({"error": "Not found"})}


class HandlerMeta(type):
    """Metaclass allowing class `handler` to be invoked both as a BaseHTTPRequestHandler and as a function."""

    def __call__(cls, *args, **kwargs):
        # When called like a function handler(event, context)
        if len(args) >= 1 and isinstance(args[0], dict):
            return handle_event(args[0], args[1] if len(args) > 1 else None)
        return super().__call__(*args, **kwargs)


class handler(BaseHTTPRequestHandler, metaclass=HandlerMeta):
    """Vercel Serverless Function & Local HTTP Request Handler."""

    def log_message(self, format, *args):
        """Suppress default verbose logging."""
        pass

    def send_cors_headers(self):
        """Send standard CORS headers."""
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, HEAD")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def send_json(self, status_code: int, data: Any):
        """Send a JSON HTTP response."""
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def send_html(self, html_content: str, status_code: int = 200):
        """Send an HTML HTTP response."""
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(html_content.encode("utf-8"))

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(204)
        self.send_cors_headers()
        self.end_headers()

    def do_HEAD(self):
        """Handle HEAD requests."""
        self.do_GET()

    def do_GET(self):
        """Handle GET requests for static assets and API routes."""
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        # 1. Static file requests
        if path.startswith("/static/"):
            rel_path = path[len("/static/"):].lstrip("/")
            file_path = os.path.join(STATIC_DIR, rel_path)
            if os.path.isfile(file_path):
                content_type = "text/plain"
                if file_path.endswith(".css"):
                    content_type = "text/css; charset=utf-8"
                elif file_path.endswith(".js"):
                    content_type = "application/javascript; charset=utf-8"
                elif file_path.endswith(".json"):
                    content_type = "application/json; charset=utf-8"
                elif file_path.endswith(".png"):
                    content_type = "image/png"
                elif file_path.endswith(".svg"):
                    content_type = "image/svg+xml"

                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_cors_headers()
                self.end_headers()
                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())
                return
            else:
                self.send_json(404, {"error": "Static file not found"})
                return

        # Normalize API path (strip /api if present)
        api_path = path
        if api_path.startswith("/api/"):
            api_path = api_path[len("/api"):]

        path_parts = [p for p in api_path.split("/") if p]
        sub_endpoint = path_parts[0] if len(path_parts) > 0 else ""
        param = path_parts[1] if len(path_parts) > 1 else None

        if sub_endpoint in ["student-summary", "summary"]:
            reg_no = path_remainder(api_path, sub_endpoint + "/")
            if not reg_no and "registration" in query:
                reg_no = query["registration"][0]
            if not reg_no:
                self.send_json(400, {"error": "Registration number required"})
                return
            summary = get_student_summary(reg_no)
            if summary:
                self.send_json(200, summary)
            else:
                self.send_json(404, {"error": "Student summary not found"})
            return

        elif sub_endpoint == "students":
            reg_no = path_remainder(api_path, "students/")
            if reg_no:
                student = get_student(reg_no)
                if student:
                    self.send_json(200, student)
                else:
                    self.send_json(404, {"error": "Student not found"})
            else:
                self.send_json(200, get_all_students())
            return

        elif sub_endpoint == "units":
            if param:
                unit = get_all_units().get(param)
                if unit:
                    self.send_json(200, unit)
                else:
                    self.send_json(404, {"error": "Unit not found"})
            else:
                self.send_json(200, get_all_units())
            return

        elif sub_endpoint == "marks":
            reg_no = path_remainder(api_path, "marks/")
            if reg_no:
                self.send_json(200, get_student_marks(reg_no))
            elif "registration" in query:
                reg = query["registration"][0]
                self.send_json(200, get_student_marks(reg))
            else:
                self.send_json(200, get_all_marks())
            return

        elif sub_endpoint == "performance":
            reg_no = path_remainder(api_path, "performance/")
            if not reg_no:
                self.send_json(400, {"error": "Registration number required"})
                return
            perf = calculate_student_performance(reg_no)
            self.send_json(200, perf)
            return

        elif sub_endpoint == "class":
            stats = calculate_class_statistics()
            self.send_json(200, stats)
            return

        elif sub_endpoint in ["rankings", "ranking"]:
            self.send_json(200, {"rankings": get_rankings()})
            return

        elif sub_endpoint == "grade":
            marks_str = query.get("marks", [""])[0] if "marks" in query else (param or "")
            try:
                marks_val = float(marks_str)
                self.send_json(200, get_grade(marks_val))
            except (ValueError, TypeError):
                self.send_json(400, {"error": "Invalid marks value"})
            return

        # 3. HTML routes: root, index, and SPA views
        html_file = os.path.join(PROJECT_DIR, "index.html")
        if not os.path.isfile(html_file):
            html_file = os.path.join(TEMPLATES_DIR, "student_dashboard.html")

        if os.path.isfile(html_file):
            with open(html_file, "r", encoding="utf-8") as f:
                content = f.read()
            self.send_html(content)
            return

        self.send_html("""
        <!DOCTYPE html>
        <html><head><title>SAPAS API</title></head>
        <body style="font-family:sans-serif;padding:2rem;">
        <h1>Student Academic Performance Analysis System</h1>
        <p>API is active. Available endpoints:</p>
        <ul>
          <li><a href="/api/students">/api/students</a></li>
          <li><a href="/api/units">/api/units</a></li>
          <li><a href="/api/marks">/api/marks</a></li>
          <li><a href="/api/class">/api/class</a></li>
          <li><a href="/api/grade?marks=85">/api/grade?marks=85</a></li>
        </ul>
        </body></html>
        """)

    def do_POST(self):
        """Handle POST requests for creating/updating records."""
        parsed = urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(content_length) if content_length > 0 else b""
        try:
            body = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
        except json.JSONDecodeError:
            body = {}

        api_path = path
        if api_path.startswith("/api/"):
            api_path = api_path[len("/api"):]

        path_parts = [p for p in api_path.split("/") if p]
        sub_endpoint = path_parts[0] if len(path_parts) > 0 else ""
        param = path_parts[1] if len(path_parts) > 1 else None

        if sub_endpoint == "login":
            ident = body.get("registration_number") or body.get("reg_no") or body.get("name") or ""
            student = authenticate_student(ident)
            if student:
                summary = get_student_summary(student["registration_number"])
                self.send_json(200, {"success": True, "student": student, "summary": summary})
            else:
                self.send_json(401, {"success": False, "error": "Student registration number not found. Please try again."})
            return

        elif sub_endpoint == "students":
            reg_no = path_remainder(api_path, "students/") or body.get("registration_number", "")
            name = body.get("name", "")
            academic_year = body.get("academic_year", "2024/2025")
            if not reg_no or not name:
                self.send_json(400, {"error": "registration_number and name are required"})
                return
            student = add_student(reg_no, name, academic_year)
            self.send_json(200, student)
            return

        elif sub_endpoint == "units":
            unit_code = param or body.get("unit_code", "")
            unit_name = body.get("unit_name", "")
            if not unit_code or not unit_name:
                self.send_json(400, {"error": "unit_code and unit_name are required"})
                return
            unit = add_unit(unit_code, unit_name)
            self.send_json(200, unit)
            return

        elif sub_endpoint == "marks":
            reg_no = body.get("registration_number") or path_remainder(api_path, "marks/")
            unit_code = body.get("unit_code", "")
            marks_val = body.get("marks")
            if not reg_no or not unit_code or marks_val is None:
                self.send_json(400, {"error": "registration_number, unit_code, and marks required"})
                return
            try:
                res = record_marks(reg_no, unit_code, float(marks_val))
                self.send_json(200, res)
            except ValueError as e:
                self.send_json(400, {"error": str(e)})
            return

        self.send_json(404, {"error": "Endpoint not found"})


# Aliases for backwards compatibility and serverless runners
SAPASHandler = handler


def run_server(port: int = 8000):
    """Run the SAPAS API and web server locally."""
    server_address = ("0.0.0.0", port)
    HTTPServer.allow_reuse_address = True
    httpd = HTTPServer(server_address, handler)
    print(f"SAPAS API & Dashboard running on http://localhost:{port}")
    print("Available endpoints:")
    print(f"  Web Dashboard:  http://localhost:{port}/")
    print(f"  GET  /api/students - List students")
    print(f"  GET  /api/units    - List units")
    print(f"  GET  /api/marks    - List marks")
    print(f"  GET  /api/class    - Class statistics")
    print(f"  GET  /api/grade?marks=XX - Calculate grade")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()


if __name__ == "__main__":
    run_server()
