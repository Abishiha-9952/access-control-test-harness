# Access-Control Test Harness

A Python-based security testing tool for testing **authentication and authorization controls** in web applications and APIs.

The harness is designed to identify access-control vulnerabilities by testing different users and roles against protected endpoints and verifying not only HTTP responses, but also returned data and unauthorized state changes.

---

## 1. Project Overview

Access control determines **who is allowed to access a resource or perform an operation** in an application.

Incorrect access-control implementation can allow:

* Unauthenticated users to access protected resources
* Normal users to access administrator functions
* One user to access another user's data
* Unauthorized users to modify or delete resources
* Sensitive information to be returned to users without permission

The **Access-Control Test Harness** automates these checks and provides test results that can be used to identify authorization problems.

The project also provides controlled target applications for reproducing and validating access-control vulnerabilities.

---

## 2. Project Objectives

The main objectives are:

* Test authentication and authorization controls.
* Test access based on user roles.
* Detect vertical privilege escalation.
* Detect horizontal privilege escalation.
* Test unauthenticated access to protected endpoints.
* Validate returned response data.
* Verify whether unauthorized modifications actually occur.
* Compare vulnerable and fixed application behavior.
* Generate security-testing reports.
* Provide reproducible evidence of access-control testing.

---

# 3. What Does the Harness Test?

The harness focuses on authorization boundaries.

## 3.1 Unauthenticated Access

The harness tests whether a user without authentication can access protected endpoints.

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

If protected information is returned without authentication, the test can identify an authorization issue.

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

The harness also verifies whether an unauthorized request actually changes application data.

For example:

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

This is important because checking only the HTTP status code does not always prove that an unauthorized operation was prevented.

---

# 4. Main Testing Approach

The testing process is:

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
10. Generate report
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
│
├── target2-app/
│   └── templates/
│
├── reports/
│
├── openapi.yaml
├── openapi_test.yaml
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

It helps identify API information such as:

* Endpoints
* HTTP methods
* API paths
* Request information

---

## `harness/openapi_test_generator.py`

This component prepares access-control test cases based on the API information and configured authorization requirements.

---

## `harness/__main__.py`

Provides the module entry point for running the harness where supported.

---

# 7. OpenAPI Files

The project contains OpenAPI specifications used during testing.

```text
openapi.yaml
openapi_test.yaml
```

These files describe API endpoints and information required for the testing process.

---

# 8. Role Matrices

The project uses role-matrix files to define expected authorization behavior.

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

The exact permissions depend on the target application's security requirements.

---

# 9. Target Applications

The repository contains controlled applications that are used as security-testing targets.

## Target 1

```text
target1-app/
```

Target 1 provides an environment for testing access-control behavior.

---

## Target 2

```text
target2-app/
```

Target 2 provides another controlled environment for testing authorization behavior.

It contains application templates under:

```text
target2-app/templates/
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

Install the required Python packages:

```bash
pip install -r requirements.txt
```

If a target application has its own requirements file, install those dependencies from the corresponding target application directory.

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

Use environment variables or local configuration for passwords, tokens, API keys, and other secrets.

---

# 12. Start a Target Application

Navigate to the target application.

For example:

```bash
cd target2-app
```

Install its requirements if required:

```bash
pip install -r requirements.txt
```

Start the application using its configured startup command.

For a Flask application, this may be:

```bash
python app.py
```

The exact host and port depend on the application's configuration.

After starting the application, verify that it is accessible before running the security tests.

---

# 13. Run the Test Harness

From the project root:

```bash
python harness/test_runner.py
```

If the project supports module execution:

```bash
python -m harness
```

The exact command-line options depend on the current test-runner configuration.

---

# 14. Authorization Test Cases

The harness can be used to test several authorization scenarios.

### Test 1 — Unauthenticated User

```text
User: Unauthenticated
Endpoint: Protected endpoint
Expected: Access denied
```

---

### Test 2 — Normal User → Admin Endpoint

```text
User: Normal User
Endpoint: Admin endpoint
Expected: Access denied
```

---

### Test 3 — User A → User B

```text
User: User A
Resource owner: User B
Expected: Access denied
```

---

### Test 4 — Unauthorized Modification

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

However, an HTTP status code alone is not considered sufficient evidence of correct authorization.

For example:

```text
403 Forbidden
```

is useful evidence, but the test should also consider whether protected data was exposed or whether an unauthorized state change occurred.

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
Authorization vulnerability identified.
```

This helps detect cases where the response status does not fully describe the security impact.

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

If the resource changes despite the authorization restriction, the test identifies a potential access-control vulnerability.

---

# 18. Vulnerable and Fixed Testing

A major purpose of the project is to demonstrate that the harness can **detect vulnerabilities**, rather than only demonstrating that an application was fixed.

The same test can be executed against:

* An intentionally vulnerable version
* A fixed version

---

## Vulnerable Version

Example:

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

Using the same test against both versions provides reproducible evidence that the harness is actually detecting the authorization issue.

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

If a normal user receives administrator-only information, the authorization control should be reported as vulnerable.

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

# 22. Reports

Generated security reports are stored in:

```text
reports/
```

The repository contains reports such as:

```text
live-website_access_control_report.pdf
website-target-1_access_control_report.pdf
website-target-2_access_control_report.pdf
```

The reports provide evidence of the authorization tests performed.

They can contain information such as:

* Tested endpoints
* User/role used
* Expected authorization behavior
* Actual behavior
* Test results
* Detected authorization issues
* Response validation
* State validation

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

For example:

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

# 24. Recommended Vulnerable vs Fixed Demonstration

For a complete project demonstration:

### Step 1

Start the intentionally vulnerable target.

### Step 2

Run the access-control test.

### Step 3

Save the test output.

### Step 4

Generate the security report.

### Step 5

Fix the authorization vulnerability.

### Step 6

Run the exact same test again.

### Step 7

Verify:

```text
Vulnerable version → Vulnerability detected
Fixed version      → Test passes
```

### Step 8

Keep the reports and test output as evidence.

This demonstrates that the harness is capable of detecting the vulnerability.

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

```bash
git clone https://github.com/Abishiha-9952/access-control-test-harness.git

cd access-control-test-harness

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt
```

Start the required target application, configure the users/roles and target URL, then run:

```bash
python harness/test_runner.py
```

Review the generated results and reports under:

```text
reports/
```

---

# 27. Repository

GitHub:

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

