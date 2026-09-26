# JWT Token Generation Handover

## API Version

Version: 1.0.0

## Authentication

The API uses JSON Web Tokens (JWT) for authentication.

JWT algorithm:

HS256

Token expiration:

1 hour

## Generate a JWT

Run:

    python generate_token.py

Enter the required user information:

    User ID
    Email
    Role

Supported roles:

    user
    admin

The script generates a JWT token that can be used with protected API endpoints.

## Using the JWT

Add the token to the Authorization header:

    Authorization: Bearer <JWT_TOKEN>

Example:

    curl http://127.0.0.1:5000/api/profile \
    -H "Authorization: Bearer <JWT_TOKEN>"

## Test Users

Normal user:

    ID: 1
    Email: user1@gmail.com
    Role: user

Admin:

    ID: 2
    Email: admin@test.com
    Role: admin

## Access Control

Normal users:

- Can access their own profile
- Cannot access other users' profiles
- Cannot access the admin dashboard
- Cannot change user roles

Administrators:

- Can access user management
- Can access the admin dashboard
- Can manage user roles

## API v1.0 Freeze

The current API behavior is frozen as version 1.0.0.

Changes to existing endpoints should not be made without team approval.

## Security Notes

- Do not share JWT tokens publicly.
- Do not commit production secrets to GitHub.
- JWT tokens expire after 1 hour.
- Use HTTPS when deploying outside the local development environment.
- The current secret is for development/testing only.
