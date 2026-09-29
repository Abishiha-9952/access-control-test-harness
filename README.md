# Automated Access Control Test Harness

## Project Overview

The **Automated Access Control Test Harness** is a security testing tool designed to automate the identification and testing of access-control vulnerabilities in web applications and APIs.

The project aims to reduce manual security testing by automatically discovering API endpoints, identifying access-control requirements, generating test cases, executing tests, and reporting potential vulnerabilities.

---

## Project Workflow

```text
Authorized Target URL
        ↓
Endpoint Discovery
        ↓
Endpoint Inventory
        ↓
Authentication Setup
        ↓
Actor / Role Inference
        ↓
Candidate Policy Inference
        ↓
Test Generation
        ↓
Test Execution
        ↓
Findings
        ↓
Security Report
```

---

## My Contribution – Automated Endpoint Discovery

I contributed to the development of the **automated endpoint discovery module**.

The objective of my contribution was to move endpoint identification from a **manual process toward an automated process** within the security testing workflow.

### What I Developed

* Implemented automatic discovery of **OpenAPI/Swagger API descriptions**.
* Developed extraction of API endpoints from discovered API specifications.
* Normalized discovered endpoints into a consistent structure containing:

  * HTTP method
  * Endpoint path
  * Parameters
  * Discovery source
* Added support for **permitted route metadata** when an API description is not available.
* Added automated test cases for endpoint discovery and route normalization.
* Integrated endpoint discovery into the project's modular architecture.

### Contribution Outcome

My contribution allows the tool to automatically build an **endpoint inventory** that can be used by subsequent access-control testing components.

This reduces the need to manually identify API endpoints before security testing and supports the project's goal of creating a more **automated and target-independent access-control testing workflow**.

---

## Security Testing Concepts

### Access Control

Access control determines whether an authenticated user or role is allowed to access a particular resource or perform an action.

This project focuses on automatically testing whether different users or roles can access resources beyond their intended permissions.

### Authentication vs Authorization

* **Authentication** verifies the identity of a user.
* **Authorization** determines what an authenticated user is allowed to access.

The test harness focuses primarily on identifying authorization and access-control issues.

### Endpoint Discovery

Before access-control testing can begin, the tool needs to identify the available API endpoints.

The endpoint discovery module automates this process by:

* Discovering OpenAPI/Swagger API descriptions.
* Extracting API paths and HTTP methods.
* Identifying endpoint parameters.
* Normalizing endpoint information into a consistent format.
* Using permitted route metadata when an API specification is unavailable.

### Automated Testing

The project is designed to reduce repetitive manual security testing by creating an automated workflow from endpoint discovery to access-control testing and vulnerability reporting.

---

## Features

* Automated API Endpoint Discovery
* OpenAPI/Swagger Discovery
* Endpoint Normalization
* Route Metadata Support
* Authentication and Role-based Testing
* Access Control Testing
* Automated Test Generation
* Security Findings
* Vulnerability Reporting
* Pytest-based Test Coverage

---

## Technologies Used

* Python 3
* Flask
* Flask-SQLAlchemy
* Requests
* PyYAML
* PyJWT
* Pytest
* SQLite
* Git & GitHub

---

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

---

## Run the Application

```bash
python3 app.py
```

Open the application:

```text
http://127.0.0.1:5000
```

---

## Run Tests

Run the automated test suite using:

```bash
python3 -m pytest -q
```

The endpoint discovery module includes tests covering:

* OpenAPI endpoint extraction
* Route metadata discovery
* Endpoint normalization
* Empty discovery results

---

## Project Structure

```text
12-fsd-flask/
│
├── harness/
│   ├── discovery/
│   │   ├── api_discovery.py
│   │   └── endpoint_discovery.py
│   └── __init__.py
│
├── tests/
│   └── test_endpoint_discovery.py
│
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Project Goal

The overall goal of the project is to develop a **target-independent automated security testing framework** that can discover application endpoints and systematically test access-control policies.

The endpoint discovery contribution forms the initial stage of this workflow by providing a structured endpoint inventory for the subsequent security-testing components.
