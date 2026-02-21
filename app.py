from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "secretkey"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------- MODELS ----------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))

class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100))
    complaint_text = db.Column(db.String(500))
    status = db.Column(db.String(50), default="Pending")


# ---------------- ROUTES ----------------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        new_user = User(name=name,email=email,password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email,password=password).first()

        if user:
            session['user'] = user.name
            return redirect("/dashboard")

    return render_template("login.html")


@app.route("/dashboard", methods=["GET","POST"])
def dashboard():
    if 'user' not in session:
        return redirect("/login")

    if request.method == "POST":
        complaint = request.form['complaint']

        new_complaint = Complaint(
            student_name=session['user'],
            complaint_text=complaint
        )

        db.session.add(new_complaint)
        db.session.commit()

    complaints = Complaint.query.all()

    return render_template("dashboard.html",complaints=complaints)


@app.route("/logout")
def logout():
    session.pop('user',None)
    return redirect("/")


# ---------------- RUN ----------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
