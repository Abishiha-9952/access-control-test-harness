try:
    from harness.openapi_parser import parse_openapi
except ModuleNotFoundError:
    from openapi_parser import parse_openapi

import os
import yaml


def load_role_matrix():
    """Load the role matrix used by the access-control harness."""

    base_dir = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )

    matrix_file = os.path.join(
        base_dir,
        "role_matrix.yaml"
    )

    with open(matrix_file, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    if not isinstance(data, dict) or "roles" not in data:
        raise ValueError("Invalid role_matrix.yaml")

    return data


def normalize_path(path):
    """Convert concrete OpenAPI paths back to role-matrix form."""

    parts = path.split("/")

    normalized = []

    for part in parts:
        if part.isdigit():
            normalized.append("{id}")
        else:
            normalized.append(part)

    return "/".join(normalized)


def lookup_role_access(role_matrix, role, method, path):
    """
    Find the configured access rule for a role.

    Example:
        GET /api/users/1
        becomes:
        GET /api/users/{id}
    """

    roles = role_matrix.get("roles", {})
    role_rules = roles.get(role, {})

    normalized = normalize_path(path)

    key = f"{method.upper()} {normalized}"

    rule = role_rules.get(key)

    if isinstance(rule, dict):
        return rule.get("access", "allow")

    return "allow"


def generate_security_tests(openapi_file):
    """
    Generate access-control security tests from an OpenAPI specification.

    The generator uses:
      - OpenAPI security definitions
      - endpoint security requirements
      - path parameters
      - operation metadata
    """

    api = parse_openapi(openapi_file)

    role_matrix = load_role_matrix()

    tests = []
    counter = 1

    security_schemes = api.get("security_schemes", {})
    global_security = api.get("security", [])

    def concrete_path(endpoint, id_value=1):
        """Replace OpenAPI path parameters with test values."""

        path = endpoint["path"]

        for parameter in endpoint.get("parameters", []):
            if parameter.get("in") != "path":
                continue

            name = parameter.get("name")
            parameter_type = parameter.get("type", "string")

            if parameter_type == "integer":
                value = id_value
            else:
                value = str(id_value)

            path = path.replace(
                "{" + name + "}",
                str(value)
            )

        return path

    def add_test(
        role,
        category,
        endpoint,
        access,
        expected,
        path
    ):
        nonlocal counter

        tests.append({
            "id": f"OAS-{counter:03d}",
            "role": role,
            "category": category,
            "method": endpoint["method"],
            "path": path,
            "access": access,
            "expected": expected,
            "operation_id": endpoint.get("operation_id"),
            "summary": endpoint.get("summary", ""),
            "description": endpoint.get("description", ""),
            "parameters": endpoint.get("parameters", []),
            "security": endpoint.get(
                "security",
                global_security
            ),
            "security_schemes": security_schemes,
        })

        counter += 1

    for endpoint in api["endpoints"]:

        original_path = endpoint["path"]

        normal_path = concrete_path(
            endpoint,
            id_value=1
        )

        other_resource_path = concrete_path(
            endpoint,
            id_value=2
        )

        endpoint_security = endpoint.get(
            "security",
            global_security
        )

        protected = bool(endpoint_security)

        # --------------------------------------------------
        # Authentication
        # --------------------------------------------------

        if protected:
            add_test(
                role="guest",
                category="Authentication",
                endpoint=endpoint,
                path=normal_path,
                access="unauthenticated",
                expected=401,
            )

        # --------------------------------------------------
        # Authenticated user
        # --------------------------------------------------

        user_access = lookup_role_access(
            role_matrix,
            "user",
            endpoint["method"],
            normal_path,
        )

        add_test(
            role="user",
            category="Authorization",
            endpoint=endpoint,
            path=normal_path,
            access=user_access,
            expected=None,
        )

        # --------------------------------------------------
        # Admin
        # --------------------------------------------------

        admin_access = lookup_role_access(
            role_matrix,
            "admin",
            endpoint["method"],
            normal_path,
        )

        add_test(
            role="admin",
            category="Authorization",
            endpoint=endpoint,
            path=normal_path,
            access=admin_access,
            expected=None,
        )

        # --------------------------------------------------
        # Horizontal authorization / IDOR
        # --------------------------------------------------

        path_parameters = [
            parameter
            for parameter in endpoint.get("parameters", [])
            if parameter.get("in") == "path"
        ]

        if path_parameters:

            idor_access = lookup_role_access(
                role_matrix,
                "user",
                endpoint["method"],
                other_resource_path,
            )

            # For an "own" resource, another user's ID must be denied.
            if idor_access == "own":
                idor_access = "deny"

            add_test(
                role="user",
                category="Horizontal Authorization / IDOR",
                endpoint=endpoint,
                path=other_resource_path,
                access=idor_access,
                expected=None,
            )

    return {
        "openapi_version": api["openapi_version"],
        "title": api["title"],
        "version": api["version"],
        "security_schemes": security_schemes,
        "security": global_security,
        "tests": tests,
    }


def print_generated_tests(test_data):
    """Display generated tests in a readable format."""

    print("=" * 60)
    print("OPENAPI SECURITY TEST GENERATOR")
    print("=" * 60)

    print(f"API       : {test_data['title']}")
    print(f"Version   : {test_data['version']}")
    print(f"OpenAPI   : {test_data['openapi_version']}")
    print(f"Tests     : {len(test_data['tests'])}")

    print("=" * 60)

    for test in test_data["tests"]:
        print(
            f"{test['id']} | "
            f"{test['role']:5} | "
            f"{test['category']:35} | "
            f"{test['method']:6} | "
            f"{test['path']}"
        )


if __name__ == "__main__":

    import sys

    if len(sys.argv) != 2:
        print(
            "Usage: python3 harness/openapi_test_generator.py "
            "<openapi.yaml>"
        )
        sys.exit(1)

    openapi_file = sys.argv[1]

    test_data = generate_security_tests(openapi_file)

    print_generated_tests(test_data)
