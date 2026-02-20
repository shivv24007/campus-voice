from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DATABASE ----------------

def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Students Table
    c.execute('''CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    email TEXT,
                    password TEXT
                )''')

    # Complaints Table
    c.execute('''CREATE TABLE IF NOT EXISTS complaints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER,
                    complaint TEXT,
                    status TEXT DEFAULT 'Pending'
                )''')

    conn.commit()
    conn.close()

init_db()

# ---------------- ROUTES ----------------

@app.route("/")
def home():
    return render_template("index.html")

# -------- Student Register --------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("INSERT INTO students (name,email,password) VALUES (?,?,?)",
                  (name, email, password))
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

# -------- Student Login --------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT * FROM students WHERE email=? AND password=?",
                  (email, password))
        user = c.fetchone()
        conn.close()

        if user:
            session["student_id"] = user[0]
            return redirect("/dashboard")
        else:
            return "Invalid Credentials"

    return render_template("login.html")

# -------- Student Dashboard --------

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "student_id" not in session:
        return redirect("/login")

    student_id = session["student_id"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    if request.method == "POST":
        complaint = request.form["complaint"]
        c.execute("INSERT INTO complaints (student_id, complaint) VALUES (?,?)",
                  (student_id, complaint))
        conn.commit()

    c.execute("SELECT * FROM complaints WHERE student_id=?",
              (student_id,))
    complaints = c.fetchall()

    conn.close()

    return render_template("dashboard.html", complaints=complaints)

# -------- Admin Login --------

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Hardcoded admin
        if username == "admin" and password == "admin123":
            session["admin"] = True
            return redirect("/admin_dashboard")
        else:
            return "Invalid Admin Credentials"

    return render_template("admin_login.html")

# -------- Admin Dashboard --------

@app.route("/admin_dashboard", methods=["GET", "POST"])
def admin_dashboard():
    if "admin" not in session:
        return redirect("/admin")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    if request.method == "POST":
        complaint_id = request.form["complaint_id"]
        status = request.form["status"]
        c.execute("UPDATE complaints SET status=? WHERE id=?",
                  (status, complaint_id))
        conn.commit()

    c.execute("""SELECT complaints.id, students.name, complaints.complaint, complaints.status
                 FROM complaints
                 JOIN students ON complaints.student_id = students.id""")
    all_complaints = c.fetchall()

    conn.close()

    return render_template("admin_dashboard.html", complaints=all_complaints)

# -------- Logout --------

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
