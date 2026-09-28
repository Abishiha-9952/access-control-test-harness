import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent

if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from app import app, db, User


USERS = [
    {
        "email": "usera@example.com",
        "password": "password123",
        "role": "user",
    },
    {
        "email": "userb@example.com",
        "password": "password123",
        "role": "user",
    },
    {
        "email": "admin@example.com",
        "password": "admin123",
        "role": "admin",
    },
]


def main():
    with app.app_context():
        db.create_all()

        for item in USERS:
            user = User.query.filter_by(
                email=item["email"]
            ).first()

            if user is None:
                from werkzeug.security import generate_password_hash

                user = User(
                    email=item["email"],
                    password_hash=generate_password_hash(
                        item["password"]
                    ),
                    role=item["role"],
                )

                db.session.add(user)

            else:
                user.role = item["role"]

        db.session.commit()

        print("=== Target 3 test users ready ===")

        for item in USERS:
            user = User.query.filter_by(
                email=item["email"]
            ).first()

            print(
                f"{user.id}: "
                f"{user.email} "
                f"role={user.role}"
            )


if __name__ == "__main__":
    main()
