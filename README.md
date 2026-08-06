# Flask Login & Registration System

## Project Name

12-fsd-flask

## Requirements

- Python 3
- Flask
- Flask-SQLAlchemy
- Werkzeug

## Installation

Create a virtual environment:

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python3 app.py
```

Open your browser:

```
http://127.0.0.1:5000
```

---

## GET vs POST

- **GET** is used to request data or display pages.
- **POST** is used to send data securely to the server.
- Login and registration forms use **POST** because they send user credentials.

---

## Why Client-side Validation Is Not Security

Client-side validation improves user experience but can be bypassed easily.

Server-side validation is mandatory because the server must verify all submitted data before processing it.

---

## Why Password Hashing Is Required

Passwords should never be stored as plain text.

This project uses Werkzeug's password hashing to securely store passwords in the database.

If the database is compromised, hashed passwords are much harder to recover than plain text passwords.

---

## Session

A session keeps the user logged in after successful authentication.

In this application, the logged-in user's email is stored in the Flask session.

The session is cleared when the user logs out.

---

## Features

- User Registration
- User Login
- Password Hashing
- SQLite Database
- Protected Dashboard
- Logout
