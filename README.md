# Automated Access Control Test Harness


## Overview

The Access Control Test Harness is a security testing project designed to automate the detection of access control vulnerabilities in REST APIs.

The project builds on the concept of manual access control testing and extends it into an automated and reusable testing approach.

## Contribution

My contribution focuses on developing the **candidate policy inference and automated test generation** components.

The purpose of this contribution is to convert manually defined access control testing concepts into automatically generated security test cases.

### Main Contributions

- Developed a candidate authorization policy inference module.
- Generated provisional authorization rules from discovered actors and API endpoints.
- Clearly marked the generated model as a **Candidate/Inferred Policy**, rather than confirmed application policy.
- Developed an automated test generator that converts candidate policy rules into test definitions.
- Added test categories for:
  - Authentication / missing authentication
  - Vertical privilege escalation
  - Horizontal privilege escalation (IDOR/BOLA)
  - JWT validation
- Added generated access-control test cases based on the inferred policy.
- Added a GitHub Actions workflow to validate policy inference and test generation automatically.

## Project Flow

```text
Discovered Endpoints + Actors
              |
              v
     Candidate Policy
        Inference
              |
              v
   Candidate Authorization
          Policy
              |
              v
      Automated Test
         Generator
              |
              v
       Generated Test
          Cases
