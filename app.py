from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config["SECRET_KEY"] = "mysecretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# Database Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)


# Create Database
with app.app_context():
    db.create_all()


# Home Page
@app.route("/")
def home():
    return redirect(url_for("login"))


# Register
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]
        confirm = request.form["confirm"]

        # Validation
        if not email:
            flash("Email is required")
            return redirect(url_for("register"))

        if not password:
            flash("Password is required")
            return redirect(url_for("register"))

        if not confirm:
            flash("Confirm Password is required")
            return redirect(url_for("register"))

        if len(password) < 8:
            flash("Password must be at least 8 characters")
            return redirect(url_for("register"))

        if password != confirm:
            flash("Passwords do not match")
            return redirect(url_for("register"))

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email already exists")
            return redirect(url_for("register"))

        password_hash = generate_password_hash(password)

        new_user = User(
            email=email,
            password_hash=password_hash
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration Successful")
        return redirect(url_for("login"))

    return render_template("register.html")


# Login
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        if not email:
            flash("Email is required")
            return redirect(url_for("login"))

        if not password:
            flash("Password is required")
            return redirect(url_for("login"))

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            session["user"] = user.email
            return redirect(url_for("dashboard"))

        flash("Invalid Email or Password")

    return render_template("login.html")


# Dashboard
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        email=session["user"]
    )


# Logout
@app.route("/logout")
def logout():

    session.clear()

    flash("Logged out successfully")

    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
