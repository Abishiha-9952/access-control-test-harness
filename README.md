# Access Control Test Harness - Authentication & Role Inference

## Overview

The Access Control Test Harness relies on accurate authentication discovery and actor role inference to dynamically establish testing contexts against target REST APIs.

This module automates the identification of authentication mechanisms and infers actor roles without relying on hardcoded application routes or target-specific schemas.

## Contribution

My contribution focuses on developing the **authentication mechanism discovery and actor/role inference** components.

The purpose of this contribution is to dynamically discover how a target application authenticates users and automatically map actor permissions for downstream access control testing.

### Main Contributions

- Developed a target-independent authentication mechanism discovery module (`harness/discovery/auth_discovery.py`).
- Extracted authentication tokens (JWT) and session cookies dynamically from discovered endpoints and user credentials.
- Developed an actor and role inference module (`harness/inference/role_inference.py`).
- Implemented a custom URL-safe Base64 JWT parser to dynamically decode claims (`role`, `roles`, `scope`, `admin`) without external library dependencies.
- Generated structured actor contexts (anonymous, authenticated, administrative) paired with their corresponding authorization headers.
- Enabled seamless integration with the test harness execution engine and candidate policy generator.

## Project Flow

```text
Discovered Endpoints + User Credentials
              |
              v
  Authentication Discovery
       (auth_discovery.py)
              |
              v
    Authentication Contexts
    (JWT / Session Cookies)
              |
              v
        Role Inference
      (role_inference.py)
              |
              v
    Inferred Actor Profiles
   & Authorization Headers
              |
              v
 Candidate Policy & Test Generator
