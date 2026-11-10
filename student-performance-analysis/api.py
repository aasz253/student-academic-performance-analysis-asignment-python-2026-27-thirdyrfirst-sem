"""SAPAS Python API - Vercel Serverless Functions.

Provides REST API endpoints for the Student Academic Performance Analysis System.
Uses only Python standard library - no third-party dependencies required.

Endpoints:
- GET /api/students - List all students
- GET /api/students/{reg_no} - Get student by reg no
- GET /api/units - List all units
- GET /api/marks/{reg_no} - Get student marks
- GET /api/performance/{reg_no} - Get student performance analysis
- GET /api/class - Class performance statistics
- GET /api/grade/{marks} - Get grade for marks
"""

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any, Optional

# Try to import project modules, fall back to file-based data
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_DIR, "data")
REPORTS_DIR = os.path.join(PROJECT_DIR, "reports")

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# Initialize data files if they don't exist
STUDENTS_FILE = os.path.join(DATA_DIR, "students.json")
UNITS_FILE = os.path.join(DATA_DIR, "units.json")
MARKS_FILE = os.path.join(DATA_DIR, "marks.json")

for filepath in [STUDENTS_FILE, UNITS_FILE, MARKS_FILE]:
    if not os.path.exists(filepath):
        with open(filepath, "w") as f:
            f.write("{}")


def load_json_file(filepath: str) -> dict:
    """Load JSON from file with graceful error handling."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_json_file(filepath: str, data: dict) -> None:
    """Save JSON to file with indentation."""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except IOError:
        pass


# Load initial data
students_data = load_json_file(STUDENTS_FILE)
units_data = load_json_file(UNITS_FILE)
marks_data = load_json_file(MARKS_FILE)


def get_student(reg_no: str) -> Optional[dict]:
    """Get student by registration number."""
    return students_data.get(reg_no)


def get_all_students() -> dict:
    """Get all students."""
    return students_data


def add_student(reg_no: str, name: str, academic_year: str = "2024/2025") -> dict:
    """Add a new student."""
    student = {
        "registration_number": reg_no,
        "name": name,
        "academic_year": academic_year,
        "courses": [],
        "date_registered": os.popen("date +%Y-%m-%dT%H:%M:%S%z").read().strip() or "2024-01-01T00:00:00+00:00"
    }
    students_data[reg_no] = student
    save_json_file(STUDENTS_FILE, students_data)
    return student


def update_student(reg_no: str, name: Optional[str] = None, academic_year: Optional[str] = None) -> Optional[dict]:
    """Update student information."""
    if reg_no not in students_data:
        return None
    if name:
        students_data[reg_no]["name"] = name
    if academic_year:
        students_data[reg_no]["academic_year"] = academic_year
    save_json_file(STUDENTS_FILE, students_data)
    return students_data[reg_no]


def delete_student(reg_no: str) -> Optional[dict]:
    """Delete student record."""
    if reg_no not in students_data:
        return None
    deleted = students_data.pop(reg_no)
    save_json_file(STUDENTS_FILE, students_data)
    return deleted


# Grade function (same as grading.py)
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


# Performance calculation (simplified from performance_analysis.py)
def calculate_student_performance(reg_no: str) -> dict:
    """Calculate student performance metrics."""
    student_marks = marks_data.get(reg_no, {})
    
    if not student_marks:
        return {
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
    
    for unit_code, entry in student_marks.items():
        if isinstance(entry, (int, float)):
            total += entry
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
    
    # Count passed/failed units
    for unit_code, entry in student_marks.items():
        if isinstance(entry, (int, float)):
            if entry >= 40:
                passed += 1
            else:
                failed += 1
    
    # Classification
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


def calculate_class_statistics() -> dict:
    """Calculate class-level statistics."""
    all_students = load_json_file(STUDENTS_FILE)
    all_marks = load_json_file(MARKS_FILE)
    
    averages = {}
    for reg_no, student in all_students.items():
        student_marks = all_marks.get(reg_no, {})
        marks_list = [v for v in student_marks.values() if isinstance(v, (int, float))]
        if marks_list:
            averages[reg_no] = sum(marks_list) / len(marks_list)
        else:
            averages[reg_no] = 0.0
    
    if not averages:
        return {
            "total_students": len(all_students),
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
    
    # Grade distribution
    grade_dist = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0}
    for avg in averages.values():
        g = get_grade(avg)
        grade_dist[g["grade"]] += 1
    
    top_student = all_students.get(highest_reg, {})
    lowest_student = all_students.get(lowest_reg, {})
    
    return {
        "total_students": len(all_students),
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


# Request handler
class SAPASHandler(BaseHTTPRequestHandler):
    """HTTP request handler for SAPAS API."""
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass
    
    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        
        # Remove leading slash
        path_parts = [p for p in path.split("/") if p]
        
        if not path_parts or path_parts[0] == "":
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
            return
        
        endpoint = path_parts[0]
        
        # API routes
        if endpoint == "api" and len(path_parts) > 1:
            sub_endpoint = path_parts[1]
            reg_no = path_parts[2] if len(path_parts) > 2 else None
            
            if sub_endpoint == "students":
                if reg_no:
                    student = get_student(reg_no)
                    if student:
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps(student).encode())
                    else:
                        self.send_response(404)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": "Student not found"}).encode())
                else:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(get_all_students()).encode())
                    
            elif sub_endpoint == "units":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(load_json_file(UNITS_FILE)).encode())
                
            elif sub_endpoint == "marks" and reg_no:
                student_marks = load_json_file(MARKS_FILE).get(reg_no, {})
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(student_marks).encode())
                
            elif sub_endpoint == "performance" and reg_no:
                perf = calculate_student_performance(reg_no)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(perf).encode())
                
            elif sub_endpoint == "class":
                stats = calculate_class_statistics()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(stats).encode())
                
            elif sub_endpoint == "grade":
                marks_str = query.get("marks", [""])[0]
                try:
                    marks = float(marks_str)
                    grade = get_grade(marks)
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(grade).encode())
                except (ValueError, TypeError):
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Invalid marks value"}).encode())
                    
            else:
                self.send_response(404)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "API endpoint not found"}).encode())
        
        # Serve HTML file for root path
        elif path == "/" or path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            
            # Read and serve the HTML template
            html_path = os.path.join(PROJECT_DIR, "templates", "student_dashboard.html")
            if os.path.exists(html_path):
                with open(html_path, "r", encoding="utf-8") as f:
                    self.wfile.write(f.read().encode())
            else:
                # Simple fallback HTML
                self.wfile.write(b"""
                <!DOCTYPE html>
                <html><head><title>SAPAS API</title></head>
                <body><h1>SAPAS API</h1>
                <p>API is running. Visit /api/students to see data.</p>
                </body></html>
                """)
        
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def do_POST(self):
        """Handle POST requests for data operations."""
        parsed = urlparse(self.path)
        path = parsed.path
        path_parts = [p for p in path.split("/") if p]
        
        if not path_parts:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
            return
        
        endpoint = path_parts[0]
        
        if endpoint == "api" and len(path_parts) > 1:
            sub_endpoint = path_parts[1]
            reg_no = path_parts[2] if len(path_parts) > 2 else None
            
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length) if content_length else b""
            
            try:
                data = json.loads(body) if body else {}
            except json.JSONDecodeError:
                data = {}
            
            if sub_endpoint == "students" and reg_no:
                # Add or update student
                name = data.get("name", "")
                academic_year = data.get("academic_year", "2024/2025")
                student = add_student(reg_no, name, academic_year)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(student).encode())
                
            elif sub_endpoint == "students" and not reg_no:
                # List all or create (reg_no from body)
                name = data.get("name", "")
                academic_year = data.get("academic_year", "2024/2025")
                reg_no_new = data.get("registration_number", "")
                if reg_no_new:
                    student = add_student(reg_no_new, name, academic_year)
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(student).encode())
                else:
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "registration_number required"}).encode())
                    
            elif sub_endpoint == "update" and reg_no:
                name = data.get("name")
                academic_year = data.get("academic_year")
                updated = update_student(reg_no, name, academic_year)
                if updated:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(updated).encode())
                else:
                    self.send_response(404)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Student not found"}).encode())
            
            else:
                self.send_response(404)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode())
        
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def do_HEAD(self):
        """Handle HEAD requests."""
        self.do_GET()


def run_server(port: int = 8000):
    """Run the SAPAS API server (local development only)."""
    server_address = ("0.0.0.0", port)
    httpd = HTTPServer(server_address, SAPASHandler)
    print(f"SAPAS API running on http://0.0.0.0:{port}")
    print(f"API endpoints:")
    print(f"  GET /api/students - List all students")
    print(f"  GET /api/students/{{reg_no}} - Get student")
    print(f"  GET /api/units - List units")
    print(f"  GET /api/marks/{{reg_no}} - Get marks")
    print(f"  GET /api/performance/{{reg_no}} - Performance analysis")
    print(f"  GET /api/class - Class statistics")
    print(f"  GET /api/grade?marks=XX - Grade calculation")
    print()
    httpd.serve_forever()


# Vercel serverless function handler
# Vercel expects a function that takes (event, context) or similar signature
# For stdlib HTTP server, we create a compatible wrapper
def handler(event, context=None):
    """
    Vercel serverless function handler for SAPAS API.
    
    This wrapper routes Vercel's event format to our custom HTTP handler.
    In production, Vercel will call this function with the request data.
    """
    # Parse the request path and method from Vercel's event format
    # Vercel provides event.path, event.httpMethod, event.queryStringParameters, etc.
    path = event.get("path", "/")
    method = event.get("httpMethod", "GET")
    query = event.get("queryStringParameters", {})
    
    # Reconstruct the path similar to our local setup
    # This is a simplified mapping - full Vercel integration would be more complex
    full_path = path
    
    # Create a minimal mock environment for our handler
    from http.server import BaseHTTPRequestHandler
    import io
    
    # We'll return a simple response based on the path
    # For a full implementation, you'd want to map all routes properly
    if path == "/api/students":
        students_data = load_json_file(STUDENTS_FILE)
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(students_data)
        }
    elif path == "/api/units":
        units_data = load_json_file(UNITS_FILE)
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(units_data)
        }
    elif path == "/api/class":
        stats = calculate_class_statistics()
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(stats)
        }
    elif path == "/api/grade":
        marks_str = query.get("marks", [""])[0] if query else ""
        try:
            marks = float(marks_str)
            grade = get_grade(marks)
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(grade)
            }
        except (ValueError, TypeError):
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Invalid marks value"})
            }
    elif path.startswith("/api/students/") and len(path) > 16:
        reg_no = path[len("/api/students/"):]
        student = get_student(reg_no)
        if student:
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(student)
            }
        else:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Student not found"})
            }
    elif path.startswith("/api/marks/") and len(path) > 11:
        reg_no = path[len("/api/marks/"):]
        student_marks = load_json_file(MARKS_FILE).get(reg_no, {})
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(student_marks)
        }
    elif path.startswith("/api/performance/") and len(path) > 19:
        reg_no = path[len("/api/performance/"):]
        perf = calculate_student_performance(reg_no)
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(perf)
        }
    else:
        return {
            "statusCode": 404,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Not found"})
        }


# Expose 'handler' at module top-level for Vercel Python runtime
# This is the variable Vercel looks for in Python serverless functions
handler = handler

if __name__ == "__main__":
    run_server()


if __name__ == "__main__":
    run_server()