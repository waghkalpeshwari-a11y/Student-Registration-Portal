from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import re

app = Flask(__name__)

# ---------------- DATABASE ----------------

def get_connection():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row
    return conn


def create_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            mobile TEXT NOT NULL,
            dob TEXT NOT NULL,
            gender TEXT NOT NULL,
            course TEXT NOT NULL,
            address TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


create_table()

# ---------------- HOME PAGE ----------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- REGISTER ----------------

@app.route("/register", methods=["POST"])
def register():

    name = request.form["name"]
    email = request.form["email"]
    mobile = request.form["mobile"]
    dob = request.form["dob"]
    gender = request.form["gender"]
    course = request.form["course"]
    address = request.form["address"]

    # Empty Validation
    if not all([name, email, mobile, dob, gender, course, address]):
        return "All fields are required!"

    # Email Validation
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(email_pattern, email):
        return "Invalid Email Address"

    # Mobile Validation
    if not mobile.isdigit() or len(mobile) != 10:
        return "Mobile number must contain exactly 10 digits"

    conn = get_connection()
    cursor = conn.cursor()

    # Duplicate Email Check
    cursor.execute("SELECT * FROM students WHERE email=?", (email,))
    existing = cursor.fetchone()

    if existing:
        conn.close()
        return "Email already registered!"

    cursor.execute("""
        INSERT INTO students
        (name,email,mobile,dob,gender,course,address)
        VALUES(?,?,?,?,?,?,?)
    """, (name, email, mobile, dob, gender, course, address))

    conn.commit()
    conn.close()

    return redirect(url_for("students"))


# ---------------- STUDENT LIST ----------------

@app.route("/students")
def students():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    data = cursor.fetchall()

    conn.close()

    return render_template("students.html", students=data)


# ---------------- VIEW STUDENT ----------------

@app.route("/student/<int:id>")
def student(id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students WHERE id=?", (id,))
    data = cursor.fetchone()

    conn.close()

    return render_template("student.html", student=data)


# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)