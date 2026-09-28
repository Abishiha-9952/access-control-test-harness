# Access Control Test Harness
## Intentional Vulnerability Testing

### Vulnerability 1: Horizontal IDOR

**Endpoint:**
GET /api/users/<user_id>

**Description:**
A normal authenticated user can access another user's information by changing the user ID in the URL.

**Test:**
User 1 requested:

GET /api/users/2

**Actual Result:**
User 2's information was returned.

**Expected Secure Result:**
The server should return HTTP 403 Forbidden with an access denied message.

**Impact:**
A user may access information belonging to another user.

---

### Vulnerability 2: Vertical Privilege Escalation

**Endpoint:**
GET /api/admin/dashboard

**Description:**
The endpoint checks whether the user is authenticated but does not verify that the user has the admin role.

**Test:**
A normal user requested:

GET /api/admin/dashboard

**Actual Result:**
The admin dashboard and statistics were returned.

**Expected Secure Result:**
A normal user should receive HTTP 403 Forbidden.

**Impact:**
A low-privileged user can access administrator functionality.

---

### Vulnerability 3: Unauthorized Role Modification

**Endpoint:**
PUT /api/users/<user_id>/role

**Description:**
The endpoint allows a normal authenticated user to modify another user's role because it does not verify that the requester is an administrator.

**Test:**
User 1 changed User 2's role using:

PUT /api/users/2/role

Request body:

{
    "role": "admin"
}

**Actual Result:**
The role was updated successfully.

**Expected Secure Result:**
Only an administrator should be able to change user roles.

**Impact:**
A normal user could potentially give accounts elevated privileges.

---

## Security Concepts Demonstrated

1. Horizontal access control failure / IDOR
2. Vertical privilege escalation
3. Missing authorization on sensitive operations

## Testing Method

The vulnerabilities were tested locally using curl against the Flask API.

The application uses JWT authentication for API requests.
