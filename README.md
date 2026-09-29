# Access-Control Test Harness

A Python-based security testing tool for testing **authentication and authorization controls** in web applications and APIs.

The Access-Control Test Harness is designed to identify access-control vulnerabilities by testing different users and roles against protected endpoints. It validates not only HTTP responses, but also returned data and unauthorized changes to application state.

The project includes controlled target applications that can be used to reproduce and validate access-control vulnerabilities in a local testing environment.

---

## 1. Project Overview

Access control determines **who is allowed to access a resource or perform an operation** in an application.

Incorrect access-control implementation can allow:

* Unauthenticated users to access protected resources
* Normal users to access administrator functions
* One user to access another user's data
* Unauthorized users to modify another user's resources
* Sensitive information to be returned to users without permission

The **Access-Control Test Harness** automates authorization testing and provides evidence that can be used to identify and validate access-control issues.

---

## 2. Project Objectives

The main objectives of this project are:

* Test authentication and authorization controls
* Test access based on user roles
* Detect vertical privilege escalation
* Detect horizontal privilege escalation
* Test unauthenticated access to protected endpoints
* Validate returned response data
* Verify whether unauthorized modifications actually occur
* Compare vulnerable and fixed application behavior
* Generate security-testing reports
* Provide reproducible evidence of authorization testing

---

# 3. What Does the Harness Test?

The harness focuses on testing authorization boundaries between users, roles, and resources.

## 3.1 Unauthenticated Access

The harness tests whether an unauthenticated user can access protected endpoints.

Example:

```text
Unauthenticated User
        |
        v
Protected Endpoint
        |
        v
Access should be denied
```

If protected information is returned without authentication, the test can identify a potential authorization issue.

---

## 3.2 Normal User Accessing Admin Functions

The harness tests whether an ordinary user can access administrator-only functionality.

Example:

```text
Normal User
     |
     v
Admin Endpoint
     |
     v
Access should be denied
```

This helps identify **vertical privilege escalation**.

---

## 3.3 Cross-User Resource Access

The harness tests whether one authenticated user can access another user's resources.

Example:

```text
User A
  |
  | Request User B's resource
  v
Protected Resource
  |
  v
Access should be denied
```

This helps identify **horizontal privilege escalation and IDOR-style authorization issues**.

---

## 3.4 Unauthorized Modifications

The harness can also verify whether an unauthorized request actually changes application data.

Example:

```text
User A
   |
   | Modify User B's resource
   v
Authorization Check
   |
   +---- Blocked
   |       |
   |       v
   |   State unchanged
   |
   +---- Allowed
           |
           v
    Potential vulnerability
```

This is important because an HTTP status code alone does not always prove that an unauthorized operation was prevented.

---

# 4. Main Testing Approach

The general testing workflow is:

```text
1. Start target application
          |
          v
2. Configure target
          |
          v
3. Define users and roles
          |
          v
4. Define expected permissions
          |
          v
5. Execute authorization tests
          |
          v
6. Check HTTP response
          |
          v
7. Check returned data
          |
          v
8. Check application state
          |
          v
9. Compare expected vs actual behavior
          |
          v
10. Generate security report
```

---

# 5. Project Structure

```text
access-control-test-harness/
│
├── harness/
│   ├── __main__.py
│   ├── openapi_parser.py
│   ├── openapi_test_generator.py
│   └── test_runner.py
│
├── target1-app/
│   ├── app.py
│   └── openapi.yaml
│
├── target2-app/
│   ├── static/
│   ├── templates/
│   └── app.py
│
├── reports/
│   ├── live-website_access_control_report.html
│   ├── live-website_access_control_report.pdf
│   ├── website-target-1_access_control_report.html
│   ├── website-target-1_access_control_report.pdf
│   ├── website-target-2_access_control_report.html
│   └── website-target-2_access_control_report.pdf
│
├── openapi.yaml
├── role_matrix.yaml
├── role_matrix_target1.yaml
├── role_matrix_target2.yaml
├── README.md
└── .gitignore
```

---

# 6. Important Files

## `harness/test_runner.py`

This is the main test execution component.

It performs the configured access-control tests against the target application.

The tests can validate:

* Authentication requirements
* User roles
* Endpoint authorization
* HTTP responses
* Response content
* Protected data
* Unauthorized state changes

---

## `harness/openapi_parser.py`

This component works with OpenAPI/API definitions used by the testing process.

It handles API information such as:

* Endpoints
* HTTP methods
* API paths
* Request information

---

## `harness/openapi_test_generator.py`

This component prepares access-control test cases using the API information and configured authorization requirements.

---

## `harness/__main__.py`

Provides the module entry point for running the harness where supported.

---

# 7. OpenAPI File

The project contains an OpenAPI specification used during testing:

```text
openapi.yaml
```

The OpenAPI specification describes the API endpoints used by the access-control testing harness.

It provides information such as:

* API paths
* HTTP methods
* Parameters
* Authentication requirements
* API operations

The OpenAPI specification is used by the testing process to understand the target API and prepare appropriate access-control test cases.

---

# 8. Role Matrices

The project uses role-matrix files to define expected authorization behavior:

```text
role_matrix.yaml
role_matrix_target1.yaml
role_matrix_target2.yaml
```

A role matrix describes which operations different users or roles should be allowed or denied.

Example:

| User Type       | Normal Resource     | Own Resource | Admin Resource |
| --------------- | ------------------- | ------------ | -------------- |
| Unauthenticated | Deny                | Deny         | Deny           |
| Normal User     | According to policy | Allow        | Deny           |
| Admin           | According to policy | Allow        | Allow          |

The exact permissions depend on the security requirements of the target application.

---

# 9. Target Applications

The repository contains controlled applications used as security-testing targets.

## Target 1

```text
target1-app/
```

Target 1 provides an environment for testing access-control behavior.

It contains:

```text
target1-app/
├── app.py
└── openapi.yaml
```

---

## Target 2

```text
target2-app/
```

Target 2 provides another controlled environment for testing authorization behavior.

It contains:

```text
target2-app/
├── static/
├── templates/
└── app.py
```

The target applications are intended for local and controlled security testing.

---

# 10. Installation

## Step 1 — Clone the Repository

```bash
git clone https://github.com/Abishiha-9952/access-control-test-harness.git
```

Enter the project directory:

```bash
cd access-control-test-harness
```

---

## Step 2 — Create a Virtual Environment

On Linux/Kali:

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

On Windows:

```powershell
python -m venv venv
venv\Scripts\activate
```

---

## Step 3 — Install Dependencies

The project does not include a `requirements.txt` file.

Use the Python environment and packages already required by the project and target applications.

---

# 11. Configure the Target

Before running the harness, make sure the target application is running.

The testing configuration may include:

```text
Target URL
User credentials
User roles
API endpoints
Authorization policy
Role matrix
```

Sensitive credentials should not be committed to GitHub.

Use environment variables or local configuration for:

* Passwords
* Authentication tokens
* API keys
* Other secrets

---

# 12. Start a Target Application

Navigate to the required target application.

For example:

```bash
cd target2-app
```

For a Flask application, the application may be started using:

```bash
python app.py
```

The exact host and port depend on the application's configuration.

Verify that the target application is accessible before running the security tests.

If Nginx is part of the local testing environment, start it before performing the tests:

```bash
sudo systemctl start nginx
```

Verify the Nginx service:

```bash
sudo systemctl status nginx
```

A typical local testing sequence is:

```text
Start Nginx
     |
     v
Start target application
     |
     v
Verify target application
     |
     v
Run access-control tests
```

---

# 13. Run the Test Harness

From the project root:

```bash
python harness/test_runner.py
```

If module execution is supported by the current project configuration, the harness can also be run using:

```bash
python -m harness
```

The available command-line options depend on the current test-runner implementation.

---

# 14. Authorization Test Cases

The harness can be used to test several authorization scenarios.

## Test 1 — Unauthenticated User

```text
User: Unauthenticated
Endpoint: Protected endpoint
Expected: Access denied
```

---

## Test 2 — Normal User → Admin Endpoint

```text
User: Normal User
Endpoint: Admin endpoint
Expected: Access denied
```

---

## Test 3 — User A → User B

```text
User: User A
Resource owner: User B
Expected: Access denied
```

---

## Test 4 — Unauthorized Modification

```text
User: User A
Target resource: User B
Operation: Modify

Expected:
- Request denied
- Resource remains unchanged
```

---

# 15. HTTP Response Validation

The harness checks HTTP responses as part of authorization testing.

Possible responses include:

```text
200 OK
201 Created
401 Unauthorized
403 Forbidden
404 Not Found
```

However, an HTTP status code alone is not sufficient evidence of correct authorization.

For example:

```text
403 Forbidden
```

is useful evidence, but testing should also consider:

* Whether protected data was exposed
* Whether the requested operation actually occurred
* Whether application state changed

---

# 16. Response Data Validation

The harness can verify the actual content returned by the application.

Example:

```text
User A requests User B's private resource.

Expected:
User B's information is not returned.

Observed:
User B's private information is returned.

Result:
Potential authorization vulnerability identified.
```

This helps identify cases where the response status does not fully describe the security impact.

---

# 17. State Validation

For operations that modify application data, the harness can validate application state.

Example:

```text
Before request:
User B's resource = Original value

User A sends unauthorized modification

After request:
User B's resource = ?
```

Expected secure result:

```text
Authorization denied
+
Resource remains unchanged
```

If the resource changes despite the authorization restriction, the test can identify a potential access-control vulnerability.

---

# 18. Vulnerable and Fixed Testing

A major purpose of this project is to demonstrate that the harness can **detect vulnerabilities**, rather than only demonstrating that an application was fixed.

The same test can be executed against:

* An intentionally vulnerable version
* A fixed version

---

## Vulnerable Version

```text
Test
 |
 v
Vulnerable Application
 |
 v
Unauthorized operation succeeds
 |
 v
Test identifies vulnerability
```

Expected result:

```text
FAIL / VULNERABILITY DETECTED
```

---

## Fixed Version

```text
Test
 |
 v
Fixed Application
 |
 v
Unauthorized operation blocked
 |
 v
State remains unchanged
 |
 v
Test passes
```

Expected result:

```text
PASS
```

Running the same test against both versions provides reproducible evidence that the harness is detecting the authorization issue.

---

# 19. Example Admin Authorization Test

Suppose the application contains:

```text
GET /admin/stats
```

Expected authorization policy:

| Role            | Expected Access |
| --------------- | --------------- |
| Unauthenticated | Deny            |
| Normal User     | Deny            |
| Admin           | Allow           |

The harness tests:

```text
Unauthenticated → /admin/stats
Normal User     → /admin/stats
Admin           → /admin/stats
```

Expected:

```text
Unauthenticated → Denied
Normal User     → Denied
Admin           → Allowed
```

If a normal user receives administrator-only information, the test can identify a potential authorization vulnerability.

---

# 20. Example Cross-User Test

Suppose:

```text
User A → /users/A/orders
User B → /users/B/orders
```

The harness tests whether User A can access User B's orders.

Expected:

```text
User A → User A's orders = Allowed
User A → User B's orders = Denied
```

The test should also verify that User B's protected data is not returned.

---

# 21. Example State-Change Test

For a modification endpoint:

```text
PUT /users/B/profile
```

the test can perform:

```text
1. Record User B's original profile.
2. Authenticate as User A.
3. Attempt to modify User B's profile.
4. Record the HTTP response.
5. Retrieve User B's profile.
6. Compare the state before and after.
```

Expected secure behavior:

```text
Request denied
+
User B's profile unchanged
```

---

# 22. Security Testing Reports

Generated security-testing reports are included in the `reports/` directory.

The reports provide evidence of the authorization tests performed by the harness, including tested endpoints, user roles, expected behavior, actual behavior, and test results.

Available reports include:

* `live-website_access_control_report.pdf` — Access-control testing report for the live test target.
* `website-target-1_access_control_report.pdf` — Access-control testing report for Target 1.
* `website-target-2_access_control_report.pdf` — Access-control testing report for Target 2.

HTML versions of the reports are also provided:

* `live-website_access_control_report.html`
* `website-target-1_access_control_report.html`
* `website-target-2_access_control_report.html`

These reports are included as project evidence and are intended to support reproducibility and mentor/project review.

---

# 23. Recommended Testing Evidence

For each completed security-testing task, maintain:

```text
1. Test case
2. Expected result
3. Actual result
4. Test output
5. Generated report
6. Relevant commit
```

Example:

```text
Test:
Normal user attempts to access admin statistics.

Expected:
Access denied.

Actual:
Access denied and no administrator data returned.

Evidence:
reports/website-target-2_access_control_report.pdf
```

---

# 24. Vulnerable vs Fixed Demonstration

For a complete project demonstration:

### Step 1

Start the intentionally vulnerable target.

### Step 2

If Nginx is used by the local testing environment, start Nginx:

```bash
sudo systemctl start nginx
```

### Step 3

Run the access-control test.

### Step 4

Save the test output.

### Step 5

Generate the security report.

### Step 6

Fix the authorization vulnerability.

### Step 7

Run the exact same test again.

### Step 8

Compare the results:

```text
Vulnerable version → Vulnerability detected
Fixed version      → Test passes
```

### Step 9

Keep the reports and test output as evidence.

This demonstrates that the harness can detect an authorization vulnerability and verify the behavior after remediation.

---

# 25. Security Considerations

This project is intended for:

* Educational security testing
* Local security labs
* Controlled applications
* Authorized testing
* Development and testing environments

Only test systems that you own or have explicit permission to test.

Do not use the harness against third-party applications without authorization.

---

# 26. Quick Start

Clone the repository:

```bash
git clone https://github.com/Abishiha-9952/access-control-test-harness.git
```

Enter the project:

```bash
cd access-control-test-harness
```

Create and activate the virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Start Nginx if it is required by the local testing environment:

```bash
sudo systemctl start nginx
```

Verify Nginx:

```bash
sudo systemctl status nginx
```

Start the required target application.

For example:

```bash
cd target2-app
python app.py
```

Return to the project root and run the harness:

```bash
cd ..
python harness/test_runner.py
```

If supported:

```bash
python -m harness
```

Review the generated results and security reports under:

```text
reports/
```

---

# 27. Repository

GitHub repository:

https://github.com/Abishiha-9952/access-control-test-harness

---

# 28. Project Goal

The goal of the **Access-Control Test Harness** is to provide a reproducible method for testing application authorization.

The project demonstrates access-control testing through:

* Role-based authorization testing
* Unauthenticated access testing
* Cross-user access testing
* Admin privilege testing
* Response-data validation
* Unauthorized state-change validation
* Vulnerable-versus-fixed testing
* Generated security reports

The key objective is to demonstrate that the harness can **identify unauthorized access and verify whether security controls correctly prevent unauthorized actions**.
