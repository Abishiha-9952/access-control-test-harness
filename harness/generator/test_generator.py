def generate_tests(endpoints, policy):
    """
    Generate access-control test cases
    from an inferred authorization policy.
    """

    tests = []
   
    tests.append({
    "test_type": "authentication",
    "description": "Verify that unauthenticated users cannot access protected endpoints."
})

    tests.append({
    "test_type": "vertical_authorization",
    "description": "Verify that lower-privileged roles cannot access higher-privileged resources."
})

    tests.append({
    "test_type": "horizontal_authorization",
    "description": "Verify that one user cannot access another user's resources."
})

    tests.append({
    "test_type": "jwt_validation",
    "description": "Verify that JWT tokens are properly validated before granting access."
})

    for rule in policy:
        tests.append({
            "role": rule["role"],
            "method": rule["method"],
            "path": rule["path"],
            "expected_access": rule["expected_access"],
        })

    return tests

def build_test_case(role, method, path, expected_access):
    """
    Build a single access-control test case.
    """

    return {
        "role": role,
        "method": method,
        "path": path,
        "expected_access": expected_access,
    }
