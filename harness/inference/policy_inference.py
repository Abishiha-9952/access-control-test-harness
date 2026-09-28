def infer_policy(endpoints, actors):
    """
    Build a candidate authorization policy
    from discovered endpoints and actors.

    This is an inferred policy, not the
    application's confirmed ground truth.
    """

    policy = []

    for actor in actors:
        for endpoint in endpoints:
            role = actor.get("role", "unknown")
            method = endpoint.get("method", "GET")
            path = endpoint.get("path", "/")

            expected_access = infer_expected_access(
                role,
                method,
                path
            )

            policy.append({
                "role": role,
                "method": method,
                "path": path,
                "expected_access": expected_access
            })

    return policy





def infer_expected_access(role, method, path):
    """
    Infer a candidate access decision.

    The result is an assumption for test generation,
    not the application's confirmed authorization policy.
    """

    role = role.lower()
    method = method.upper()
    path = path.lower()

    if role == "admin":
        return "allow"

    if "/admin" in path:
        return "deny"

    if method in ["DELETE", "PUT", "PATCH"]:
        return "deny"

    return "allow"
