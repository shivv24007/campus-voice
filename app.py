from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///complaints.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# =========================
# DATABASE MODEL
# =========================
class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    message = db.Column(db.Text)
    status = db.Column(db.String(50), default="Pending")
    admin_reply = db.Column(db.Text)   # NEW COLUMN

# Create database
with app.app_context():
    db.create_all()

# =========================
# STUDENT PAGE
# =========================
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name")
        message = request.form.get("message")

        new_complaint = Complaint(name=name, message=message)
        db.session.add(new_complaint)
        db.session.commit()

        return redirect("/")

    complaints = Complaint.query.all()
    return render_template("index.html", complaints=complaints)

# =========================
# ADMIN PANEL
# =========================
@app.route("/admin")
def admin():
    complaints = Complaint.query.all()
    return render_template("admin.html", complaints=complaints)

# =========================
# UPDATE STATUS
# =========================
@app.route("/update_status/<int:id>", methods=["POST"])
def update_status(id):
    complaint = Complaint.query.get(id)
    complaint.status = request.form.get("status")
    db.session.commit()
    return redirect("/admin")

# =========================
# ADMIN REPLY
# =========================
@app.route("/reply/<int:id>", methods=["POST"])
def reply(id):
    complaint = Complaint.query.get(id)
    complaint.admin_reply = request.form.get("reply")
    db.session.commit()
    return redirect("/admin")

if __name__ == "__main__":
    app.run(debug=True)
