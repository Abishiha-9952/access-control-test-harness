from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

import jwt
from functools import wraps
from datetime import datetime, timedelta, timezone


app = Flask(__name__)

app.config["SECRET_KEY"] = "mysecretkey"
app.config["JWT_SECRET_KEY"] = "change-this-jwt-secret"
app.config["JWT_EXPIRATION_HOURS"] = 1
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ============================================================
# DATABASE MODEL
# ============================================================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="user", nullable=False)


# ============================================================
# JWT TOKEN GENERATION
# ============================================================

def generate_token(user):

    payload = {
        "user_id": user.id,
        "email": user.email,
        "role": user.role,
        "exp": datetime.now(timezone.utc) + timedelta(
            hours=app.config["JWT_EXPIRATION_HOURS"]
        )
    }

    return jwt.encode(
        payload,
        app.config["JWT_SECRET_KEY"],
        algorithm="HS256"
    )


# ============================================================
# JWT AUTHENTICATION DECORATOR
# ============================================================

def jwt_required(f):

    @wraps(f)
    def decorated(*args, **kwargs):

        token = request.headers.get("Authorization")

        if not token:
            return jsonify({
                "error": "Authorization token required"
            }), 401

        if not token.startswith("Bearer "):
            return jsonify({
                "error": "Invalid authorization format"
            }), 401

        token = token.split(" ", 1)[1]

        try:

            payload = jwt.decode(
                token,
                app.config["JWT_SECRET_KEY"],
                algorithms=["HS256"]
            )

            current_user = User.query.get(payload["user_id"])

            if not current_user:
                return jsonify({
                    "error": "User not found"
                }), 401

            request.current_user = current_user

        except jwt.ExpiredSignatureError:

            return jsonify({
                "error": "Token expired"
            }), 401

        except jwt.InvalidTokenError:

            return jsonify({
                "error": "Invalid token"
            }), 401

        return f(*args, **kwargs)

    return decorated


# ============================================================
# CREATE DATABASE
# ============================================================

with app.app_context():
    db.create_all()


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():
    return redirect(url_for("login"))


# ============================================================
# REGISTER
# ============================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]
        confirm = request.form["confirm"]

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


# ============================================================
# API 1 - JWT LOGIN
# ============================================================

@app.route("/api/login", methods=["POST"])
def api_login():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "JSON body required"
        }), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "error": "Email and password are required"
        }), 400

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(
        user.password_hash,
        password
    ):
        return jsonify({
            "error": "Invalid email or password"
        }), 401

    token = generate_token(user)

    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role
        }
    }), 200


# ============================================================
# API 2 - USER PROFILE
# ============================================================

@app.route("/api/profile", methods=["GET"])
@jwt_required
def api_profile():

    user = request.current_user

    return jsonify({
        "message": "Access granted",
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role
        }
    }), 200


# ============================================================
# API 3 - GET ALL USERS
# ADMIN ONLY
# ============================================================

@app.route("/api/users", methods=["GET"])
@jwt_required
def get_users():

    user = request.current_user

    if user.role != "admin":
        return jsonify({
            "error": "Admin access required"
        }), 403

    users = User.query.all()

    return jsonify({
        "users": [
            {
                "id": u.id,
                "email": u.email,
                "role": u.role
            }
            for u in users
        ]
    }), 200


# ============================================================
# API 4 - GET USER BY ID
# ============================================================

@app.route("/api/users/<int:user_id>", methods=["GET"])
@jwt_required
def get_user(user_id):

    user = request.current_user

    # User can access own profile.
    # Admin can access any profile.
    if user.role != "admin" and user.id != user_id:

        return jsonify({
            "error": "Access denied"
        }), 403

    target_user = User.query.get(user_id)

    if not target_user:

        return jsonify({
            "error": "User not found"
        }), 404

    return jsonify({
        "id": target_user.id,
        "email": target_user.email,
        "role": target_user.role
    }), 200


# ============================================================
# API 5 - CREATE USER
# ADMIN ONLY
# ============================================================

@app.route("/api/users", methods=["POST"])
@jwt_required
def create_user():

    user = request.current_user

    if user.role != "admin":

        return jsonify({
            "error": "Admin access required"
        }), 403

    data = request.get_json()

    if not data:

        return jsonify({
            "error": "JSON body required"
        }), 400

    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "user")

    if not email or not password:

        return jsonify({
            "error": "Email and password are required"
        }), 400

    if role not in ["user", "admin"]:

        return jsonify({
            "error": "Invalid role"
        }), 400

    existing_user = User.query.filter_by(
        email=email
    ).first()

    if existing_user:

        return jsonify({
            "error": "Email already exists"
        }), 409

    new_user = User(
        email=email,
        password_hash=generate_password_hash(password),
        role=role
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "User created successfully",
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "role": new_user.role
        }
    }), 201


# ============================================================
# API 6 - UPDATE USER
# ============================================================

@app.route("/api/users/<int:user_id>", methods=["PUT"])
@jwt_required
def update_user(user_id):

    user = request.current_user

    if user.role != "admin" and user.id != user_id:

        return jsonify({
            "error": "Access denied"
        }), 403

    target_user = User.query.get(user_id)

    if not target_user:

        return jsonify({
            "error": "User not found"
        }), 404

    data = request.get_json()

    if not data:

        return jsonify({
            "error": "JSON body required"
        }), 400

    if "email" in data:
        target_user.email = data["email"]

    if "password" in data:

        target_user.password_hash = generate_password_hash(
            data["password"]
        )

    db.session.commit()

    return jsonify({
        "message": "User updated successfully",
        "user": {
            "id": target_user.id,
            "email": target_user.email,
            "role": target_user.role
        }
    }), 200


# ============================================================
# API 7 - DELETE USER
# ADMIN ONLY
# ============================================================

@app.route("/api/users/<int:user_id>", methods=["DELETE"])
@jwt_required
def delete_user(user_id):

    user = request.current_user

    if user.role != "admin":

        return jsonify({
            "error": "Admin access required"
        }), 403

    target_user = User.query.get(user_id)

    if not target_user:

        return jsonify({
            "error": "User not found"
        }), 404

    if target_user.id == user.id:

        return jsonify({
            "error": "Admin cannot delete itself"
        }), 403

    db.session.delete(target_user)
    db.session.commit()

    return jsonify({
        "message": "User deleted successfully"
    }), 200


# ============================================================
# API 8 - CHANGE USER ROLE
# ADMIN ONLY
# ============================================================

@app.route("/api/users/<int:user_id>/role", methods=["PUT"])
@jwt_required
def change_user_role(user_id):

    user = request.current_user

    if user.role != "admin":

        return jsonify({
            "error": "Admin access required"
        }), 403

    target_user = User.query.get(user_id)

    if not target_user:

        return jsonify({
            "error": "User not found"
        }), 404

    data = request.get_json()

    if not data or "role" not in data:

        return jsonify({
            "error": "Role is required"
        }), 400

    if data["role"] not in ["user", "admin"]:

        return jsonify({
            "error": "Invalid role"
        }), 400

    target_user.role = data["role"]

    db.session.commit()

    return jsonify({
        "message": "Role updated successfully",
        "user": {
            "id": target_user.id,
            "email": target_user.email,
            "role": target_user.role
        }
    }), 200


# ============================================================
# API 9 - RESOURCES
# ============================================================

@app.route("/api/resources", methods=["GET"])
@jwt_required
def get_resources():

    user = request.current_user

    resources = [
        {
            "id": 1,
            "name": "User Profile",
            "access": "user"
        },
        {
            "id": 2,
            "name": "User Management",
            "access": "admin"
        },
        {
            "id": 3,
            "name": "Admin Dashboard",
            "access": "admin"
        }
    ]

    accessible_resources = []

    for resource in resources:

        if resource["access"] == "user":

            accessible_resources.append(resource)

        elif (
            resource["access"] == "admin"
            and user.role == "admin"
        ):

            accessible_resources.append(resource)

    return jsonify({
        "user_role": user.role,
        "resources": accessible_resources
    }), 200


# ============================================================
# API 10 - ADMIN DASHBOARD
# ============================================================

@app.route("/api/admin/dashboard", methods=["GET"])
@jwt_required
def admin_dashboard():

    user = request.current_user

    if user.role != "admin":

        return jsonify({
            "error": "Admin access required"
        }), 403

    total_users = User.query.count()

    total_admins = User.query.filter_by(
        role="admin"
    ).count()

    return jsonify({
        "message": "Admin dashboard access granted",
        "statistics": {
            "total_users": total_users,
            "total_admins": total_admins
        }
    }), 200


# ============================================================
# WEB LOGIN
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(
            email=email
        ).first()

        if user and check_password_hash(
            user.password_hash,
            password
        ):

            session["user_id"] = user.id

            return redirect(url_for("dashboard"))

        flash("Invalid email or password")

    return render_template("login.html")


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])

    return render_template(
        "dashboard.html",
        user=user
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.pop("user_id", None)

    return redirect(url_for("login"))


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
