import jwt
import datetime
from app import JWT_SECRET_KEY


JWT_EXPIRATION_HOURS = 1


def generate_token(user_id, email, role):
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(hours=JWT_EXPIRATION_HOURS)
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm="HS256"
    )


if __name__ == "__main__":

    print("JWT Token Generator")
    print("-------------------")

    user_id = int(input("User ID: "))
    email = input("Email: ")
    role = input("Role (user/admin): ")

    if role not in ["user", "admin"]:
        print("Invalid role. Use user or admin.")
        exit()

    token = generate_token(
        user_id,
        email,
        role
    )

    print("\nGenerated JWT:")
    print(token)
