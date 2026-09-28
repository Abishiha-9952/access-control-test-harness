from flask import Flask, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import jwt
import datetime


app = Flask(__name__)

# --------------------------------------------------
# Configuration
# --------------------------------------------------

app.config["SECRET_KEY"] = "change-this-session-secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

JWT_SECRET_KEY = "change-this-jwt-secret"
JWT_EXPIRATION_HOURS = 1

db = SQLAlchemy(app)


# --------------------------------------------------
# Database Model
# --------------------------------------------------

class User(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        default="user",
        nullable=False
    )

    def to_dict(self):

        return {
            "id": self.id,
            "email": self.email,
            "role": self.role
        }


# --------------------------------------------------
# JWT Functions
# --------------------------------------------------

def generate_token(user):

    payload = {
        "user_id": user.id,
        "email": user.email,
        "role": user.role,
        "exp": (
            datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(
                hours=JWT_EXPIRATION_HOURS
            )
        )
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm="HS256"
    )


def jwt_required(f):

    @wraps(f)
    def decorated(*args, **kwargs):

        auth_header = request.headers.get(
            "Authorization"
        )

        if not auth_header:

            return jsonify({
                "error": "Authorization token required"
            }), 401

        try:

            parts = auth_header.split()

            if (
                len(parts) != 2
                or parts[0].lower() != "bearer"
            ):

                return jsonify({
                    "error": "Invalid authorization header"
                }), 401

            token = parts[1]

            payload = jwt.decode(
                token,
                JWT_SECRET_KEY,
                algorithms=["HS256"]
            )

            user = db.session.get(
                User,
                payload["user_id"]
            )

            if not user:

                return jsonify({
                    "error": "User not found"
                }), 401

            request.current_user = user

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


# --------------------------------------------------
# Initialize Database
# --------------------------------------------------

with app.app_context():

    db.create_all()


# --------------------------------------------------
# Home
# --------------------------------------------------

@app.route("/")
def home():

    return jsonify({
        "message": "Access Control Test Harness API",
        "status": "running"
    })


# --------------------------------------------------
# Register
# --------------------------------------------------

@app.route(
    "/register",
    methods=["POST"]
)
def register():

    data = request.get_json() or {}

    email = data.get("email")
    password = data.get("password")

    if not email or not password:

        return jsonify({
            "error": "Email and password are required"
        }), 400

    existing_user = User.query.filter_by(
        email=email
    ).first()

    if existing_user:

        return jsonify({
            "error": "User already exists"
        }), 409

    user = User(
        email=email,
        password_hash=generate_password_hash(password),
        role="user"
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "User registered successfully",
        "user": user.to_dict()
    }), 201


# --------------------------------------------------
# Login API
# --------------------------------------------------

@app.route(
    "/api/login",
    methods=["POST"]
)
def api_login():

    data = request.get_json() or {}

    email = data.get("email")
    password = data.get("password")

    if not email or not password:

        return jsonify({
            "error": "Email and password are required"
        }), 400

    user = User.query.filter_by(
        email=email
    ).first()

    if (
        not user
        or not check_password_hash(
            user.password_hash,
            password
        )
    ):

        return jsonify({
            "error": "Invalid email or password"
        }), 401

    token = generate_token(user)

    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": user.to_dict()
    })


# --------------------------------------------------
# Profile
# --------------------------------------------------

@app.route(
    "/api/profile",
    methods=["GET"]
)
@jwt_required
def profile():

    user = request.current_user

    return jsonify({
        "id": user.id,
        "email": user.email,
        "role": user.role
    })


# --------------------------------------------------
# Get All Users - ADMIN ONLY
# --------------------------------------------------

@app.route(
    "/api/users",
    methods=["GET"]
)
@jwt_required
def get_users():

    current_user = request.current_user

    if current_user.role != "admin":

        return jsonify({
            "error": "Admin access required"
        }), 403

    users = User.query.all()

    return jsonify([
        user.to_dict()
        for user in users
    ])


# --------------------------------------------------
# Get User By ID
# SECURE AGAINST HORIZONTAL IDOR
# --------------------------------------------------

@app.route(
    "/api/users/<int:user_id>",
    methods=["GET"]
)
@jwt_required
def get_user(user_id):

    # INTENTIONALLY VULNERABLE:
    # No ownership check is performed.
    # Any authenticated user can request any user ID.

    user = db.session.get(
        User,
        user_id
    )

    if not user:
        return jsonify({
            "error": "User not found"
        }), 404

    return jsonify(
        user.to_dict()
    )


# --------------------------------------------------
# Create User - ADMIN ONLY
# --------------------------------------------------

@app.route(
    "/api/users",
    methods=["POST"]
)
@jwt_required
def create_user():

    current_user = request.current_user

    if current_user.role != "admin":

        return jsonify({
            "error": "Admin access required"
        }), 403

    data = request.get_json() or {}

    email = data.get("email")
    password = data.get("password")
    role = data.get(
        "role",
        "user"
    )

    if not email or not password:

        return jsonify({
            "error": "Email and password are required"
        }), 400

    if role not in [
        "user",
        "admin"
    ]:

        return jsonify({
            "error": "Invalid role"
        }), 400

    existing_user = User.query.filter_by(
        email=email
    ).first()

    if existing_user:

        return jsonify({
            "error": "User already exists"
        }), 409

    user = User(
        email=email,
        password_hash=generate_password_hash(password),
        role=role
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "User created successfully",
        "user": user.to_dict()
    }), 201


# --------------------------------------------------
# Update User
# --------------------------------------------------

@app.route(
    "/api/users/<int:user_id>",
    methods=["PUT"]
)
@jwt_required
def update_user(user_id):

    current_user = request.current_user

    # User can update themselves.
    # Admin can update anyone.

    if (
        current_user.role != "admin"
        and current_user.id != user_id
    ):

        return jsonify({
            "error": "Access denied"
        }), 403

    user = db.session.get(
        User,
        user_id
    )

    if not user:

        return jsonify({
            "error": "User not found"
        }), 404

    data = request.get_json() or {}

    if "email" in data:

        user.email = data["email"]

    if "password" in data:

        user.password_hash = (
            generate_password_hash(
                data["password"]
            )
        )

    db.session.commit()

    return jsonify({
        "message": "User updated successfully",
        "user": user.to_dict()
    })


# --------------------------------------------------
# Delete User - ADMIN ONLY
# --------------------------------------------------

@app.route(
    "/api/users/<int:user_id>",
    methods=["DELETE"]
)
@jwt_required
def delete_user(user_id):

    current_user = request.current_user

    if current_user.role != "admin":

        return jsonify({
            "error": "Admin access required"
        }), 403

    if current_user.id == user_id:

        return jsonify({
            "error": "Admin cannot delete themselves"
        }), 400

    user = db.session.get(
        User,
        user_id
    )

    if not user:

        return jsonify({
            "error": "User not found"
        }), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({
        "message": "User deleted successfully"
    })


# --------------------------------------------------
# Change User Role
# ADMIN ONLY
# --------------------------------------------------

@app.route(
    "/api/users/<int:user_id>/role",
    methods=["PUT"]
)
@jwt_required
def change_role(user_id):

    current_user = request.current_user

    # SECURITY CONTROL:
    # Only administrators can change roles.

    if current_user.role != "admin":

        return jsonify({
            "error": "Admin access required"
        }), 403

    user = db.session.get(
        User,
        user_id
    )

    if not user:

        return jsonify({
            "error": "User not found"
        }), 404

    data = request.get_json() or {}

    new_role = data.get("role")

    if new_role not in [
        "user",
        "admin"
    ]:

        return jsonify({
            "error": "Invalid role"
        }), 400

    user.role = new_role
    db.session.commit()

    return jsonify({
        "message": "Role updated",
        "user": user.to_dict()
    })


# --------------------------------------------------
# Resources
# --------------------------------------------------

@app.route(
    "/api/resources",
    methods=["GET"]
)
@jwt_required
def resources():

    current_user = request.current_user

    resources = [
        {
            "name": "User Profile",
            "access": "user"
        }
    ]

    if current_user.role == "admin":

        resources.extend([
            {
                "name": "User Management",
                "access": "admin"
            },
            {
                "name": "Admin Dashboard",
                "access": "admin"
            }
        ])

    return jsonify({
        "user": current_user.email,
        "role": current_user.role,
        "resources": resources
    })


# --------------------------------------------------
# Admin Dashboard
# ADMIN ONLY
# --------------------------------------------------

@app.route(
    "/api/admin/dashboard",
    methods=["GET"]
)
@jwt_required
def admin_dashboard():

    current_user = request.current_user

    # SECURITY CONTROL:
    # Only administrators can access this endpoint.

    if current_user.role != "admin":

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
    })


# --------------------------------------------------
# Web Login
# --------------------------------------------------

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "GET":

        return """
        <h2>Login</h2>

        <form method="POST">

            <input
                name="email"
                type="email"
                placeholder="Email"
                required
            >

            <input
                name="password"
                type="password"
                placeholder="Password"
                required
            >

            <button type="submit">
                Login
            </button>

        </form>
        """

    email = request.form.get("email")
    password = request.form.get("password")

    user = User.query.filter_by(
        email=email
    ).first()

    if (
        not user
        or not check_password_hash(
            user.password_hash,
            password
        )
    ):

        return (
            "Invalid email or password",
            401
        )

    session["user_id"] = user.id
    session["email"] = user.email
    session["role"] = user.role

    return redirect(
        url_for("dashboard")
    )


# --------------------------------------------------
# Dashboard
# --------------------------------------------------

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    return f"""
    <h2>Dashboard</h2>

    <p>
        Welcome, {session["email"]}
    </p>

    <p>
        Role: {session["role"]}
    </p>

    <a href="/logout">
        Logout
    </a>
    """


# --------------------------------------------------
# Logout
# --------------------------------------------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# --------------------------------------------------
# Run Application
# --------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5002,
        debug=True
    )