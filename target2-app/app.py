import os
import sqlite3
import jwt
import datetime
from functools import wraps
from flask import Flask, render_template, request, jsonify, g, redirect, url_for

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Replace with secure key in production
DATABASE = 'database.db'

# --- Database Helper Functions ---

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        
        # Schema definition
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT,
                name TEXT NOT NULL,
                price REAL NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending',
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        # --- Seed Default Test Credentials ---
        test_users = [
            (1, 'alice_user', 'password123', 'user'),
            (2, 'bob_user', 'password123', 'user'),
            (3, 'sam_support', 'password123', 'support'),
            (4, 'mary_manager', 'password123', 'manager'),
            (5, 'admin_root', 'password123', 'admin')
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO users (id, username, password, role)
            VALUES (?, ?, ?, ?)
        ''', test_users)
        
        db.commit()

# --- Authentication Decorator ---

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
            
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = query_db('SELECT id, username, role FROM users WHERE id = ?', (data['user_id'],), one=True)
            if not current_user:
                return jsonify({'message': 'User not found'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
            
        return f(current_user, *args, **kwargs)
    return decorated

# --- Frontend Page Routes (HTML Renderers) ---

@app.route("/")
def index_page():
    return render_template("index.html")

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/dashboard")
def dashboard_page():
    return render_template("dashboard.html")

@app.route("/products")
def products_page():
    return render_template("products.html")

@app.route("/orders")
def orders_page():
    return render_template("orders.html")

@app.route("/profile")
def profile_page():
    return render_template("profile.html")

@app.route("/admin/users")
def admin_users_page():
    return render_template("admin_users.html")

@app.route("/admin/stats")
def admin_stats_page():
    return render_template("admin_stats.html")

# --- Backend API Endpoints ---

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()
    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"message": "Missing username or password"}), 400

    user = query_db("SELECT * FROM users WHERE username = ?", (data["username"],), one=True)
    
    if user and user["password"] == data["password"]:
        token = jwt.encode({
            "user_id": user["id"],
            "role": user["role"],
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({
            "token": token,
            "user": {
                "id": user["id"],
                "username": user["username"],
                "role": user["role"]
            }
        }), 200

    return jsonify({"message": "Invalid credentials"}), 401

@app.route("/api/me", methods=["GET"])
@token_required
def api_me(current_user):
    return jsonify({
        "user": {
            "id": current_user["id"],
            "username": current_user["username"],
            "role": current_user["role"]
        }
    }), 200

# --- Profile API Endpoint ---
@app.route("/api/profile", methods=["GET"])
@token_required
def api_profile(current_user):
    return jsonify({
        "id": current_user["id"],
        "username": current_user["username"],
        "role": current_user["role"]
    }), 200

@app.route("/api/products", methods=["GET"])
def api_get_products():
    products = query_db("SELECT * FROM products")
    return jsonify([dict(product) for product in products]), 200

@app.route("/api/orders", methods=["GET"])
@token_required
def api_get_orders(current_user):
    if current_user["role"] == "admin":
        orders = query_db("""
            SELECT orders.id, users.username, products.name as product_name, orders.quantity, orders.status 
            FROM orders 
            JOIN users ON orders.user_id = users.id 
            JOIN products ON orders.product_id = products.id
        """)
    else:
        orders = query_db("""
            SELECT orders.id, products.name as product_name, orders.quantity, orders.status 
            FROM orders 
            JOIN products ON orders.product_id = products.id 
            WHERE orders.user_id = ?
        """, (current_user["id"],))
        
    return jsonify([dict(order) for order in orders]), 200

@app.route("/api/admin/users", methods=["GET"])
@token_required
def api_admin_users(current_user):
    users = query_db("SELECT id, username, role FROM users")
    return jsonify([dict(u) for u in users]), 200

@app.route("/api/admin/stats", methods=["GET"])
@token_required
def api_admin_stats(current_user):
    user_count = query_db("SELECT COUNT(*) as count FROM users", one=True)["count"]
    order_count = query_db("SELECT COUNT(*) as count FROM orders", one=True)["count"]
    product_count = query_db("SELECT COUNT(*) as count FROM products", one=True)["count"]
    
    return jsonify({
        "total_users": user_count,
        "total_orders": order_count,
        "total_products": product_count
    }), 200

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
