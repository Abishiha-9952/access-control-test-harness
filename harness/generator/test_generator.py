def generate_tests(policy):
    """
    Generate access-control test cases
    from an inferred authorization policy.
    """

    tests = []

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
