import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path(__file__).parent
DB_PATH = PROJECT_DIR / "database" / "student_performance.db"
DATA_DIR = PROJECT_DIR / "database"

ensure_db_dir = DATA_DIR.mkdir(parents=True, exist_ok=True)
ensure_db = not DB_PATH.exists()

if ensure_db:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("create table students (registration_number text primary key, name text, academic_year text, date_registered text)")
    c.execute("create table units (unit_code text primary key, unit_name text)")
    c.execute("create table enrollments (registration_number text, unit_code text, primary key (registration_number, unit_code), foreign key (registration_number) references students (registration_number), foreign key (unit_code) references units (unit_code))")
    c.execute("create table marks (registration_number text, unit_code text, marks integer, primary key (registration_number, unit_code), foreign key (registration_number) references students (registration_number), foreign key (unit_code) references units (unit_code))")
    c.execute("create table academic_records (record_id integer primary key autoincrement, registration_number text, semester text, year text, date_created text, foreign key (registration_number) references students (registration_number))")
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def execute_query(query, params=()):
    conn = get_db()
    c = conn.cursor()
    c.execute(query, params)
    result = c.fetchall()
    conn.commit()
    conn.close()
    return result

def register_student(registration_number, name, academic_year):
    conn = get_db()
    c = conn.cursor()
    date_registered = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("insert or ignore into students (registration_number, name, academic_year, date_registered) values (?,?,?,?)", (registration_number, name, academic_year, date_registered))
    conn.commit()
    conn.close()

def get_all_students():
    return execute_query("select * from students")

def get_student(registration_number):
    return execute_query("select * from students where registration_number=?", (registration_number,))

def add_unit(unit_code, unit_name):
    conn = get_db()
    c = conn.cursor()
    c.execute("insert or ignore into units (unit_code, unit_name) values (?,?)", (unit_code, unit_name))
    conn.commit()
    conn.close()

def get_all_units():
    return execute_query("select * from units")

def enroll_student(unit_code, registration_number):
    conn = get_db()
    c = conn.cursor()
    c.execute("insert or ignore into enrollments (registration_number, unit_code) values (?,?)", (registration_number, unit_code))
    conn.commit()
    conn.close()

def record_marks(registration_number, unit_code, marks):
    conn = get_db()
    c = conn.cursor()
    c.execute("insert or ignore into marks (registration_number, unit_code, marks) values (?,?,?)", (registration_number, unit_code, marks))
    conn.commit()
    conn.close()

def get_student_marks(registration_number):
    return execute_query("select * from marks where registration_number=?", (registration_number,))

def calculate_grade(marks):
    if marks >= 70:
        return "A"
    elif marks >= 60:
        return "B"
    elif marks >= 50:
        return "C"
    elif marks >= 40:
        return "D"
    else:
        return "E"

def calculate_student_average(registration_number):
    marks = get_student_marks(registration_number)
    if not marks:
        return 0
    total = sum(row[2] for row in marks)
    return total / len(marks)

def get_all_results():
    students = get_all_students()
    all_marks = execute_query("select * from marks")
    results = []
    for student in students:
        reg = student["registration_number"]
        avg = calculate_student_average(reg)
        grade = calculate_grade(avg)
        marks = get_student_marks(reg)
        r = {"registration": reg, "name": student["name"], "average": round(avg, 2), "grade": grade, "marks": marks}
        results.append(r)
    return results

def handler(event, context=None):
    path = event.get("path", "/")
    method = event.get("httpMethod", "GET")
    query_params = event.get("queryStringParameters", {})

    students_list = [{"registration": s["registration_number"], "name": s["name"], "year": s["academic_year"]} for s in get_all_students()]
    if path == "/api/students" and method == "GET":
        return {"statusCode": 200, "body": json.dumps({"students": students_list})}

    if path == "/api/students" and method == "POST":
        body = json.loads(event.get("body", "{}"))
        reg = body.get("registration_number", "")
        name = body.get("name", "")
        year = body.get("academic_year", "2024/2025")
        register_student(reg, name, year)
        return {"statusCode": 200, "body": json.dumps({"status": "registered"})}

    if path.startswith("/api/students/") and method == "GET":
        reg = path.split("/")[-1]
        s = get_student(reg)
        if s:
            r = {"registration": s[0]["registration_number"], "name": s[0]["name"], "year": s[0]["academic_year"]}
            return {"statusCode": 200, "body": json.dumps(r)}
        return {"statusCode": 404, "body": json.dumps({"error": "not found"})}

    if path == "/api/units" and method == "GET":
        units_list = [{"code": u["unit_code"], "name": u["unit_name"]} for u in get_all_units()]
        return {"statusCode": 200, "body": json.dumps({"units": units_list})}

    if path == "/api/marks" and method == "GET":
        reg = query_params.get("registration", [""])[0]
        m = get_student_marks(reg) if reg else []
        item_list = [{"unit": row[1], "marks": row[2]} for row in m]
        return {"statusCode": 200, "body": json.dumps({"marks": item_list})}

    if path == "/api/class/average" and method == "GET":
        results = get_all_results()
        if results:
            avg = round(sum(r["average"] for r in results) / len(results), 2)
            return {"statusCode": 200, "body": json.dumps({"average": avg, "count": len(results)})}
        return {"statusCode": 200, "body": json.dumps({"average": 0, "count": 0})}

    if path == "/api/grade" and method == "GET":
        marks_str = query_params.get("marks", [""])[0]
        try:
            m = int(marks_str)
            return {"statusCode": 200, "body": json.dumps({"grade": calculate_grade(m)})}
        except:
            return {"statusCode": 400, "body": json.dumps({"error": "invalid marks"})}

    return {"statusCode": 404, "body": json.dumps({"error": "not found"})}

if __name__ == "__main__":
    print("SAPAS CLI ready - use python3 main.py for command-line interface")