import yaml


# ============================================================
# CONFIGURATION
# ============================================================

OPENAPI_FILE = "../openapi.yaml"
ROLE_MATRIX_FILE = "../role_matrix.yaml"


# ============================================================
# LOAD YAML
# ============================================================

def load_yaml(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


# ============================================================
# LOAD OPENAPI ENDPOINTS
# ============================================================

def load_openapi_endpoints():
    openapi = load_yaml(OPENAPI_FILE)

    endpoints = set()

    for path, path_definition in openapi.get("paths", {}).items():

        for method in path_definition:

            # OpenAPI can contain non-method fields.
            # Only HTTP methods are required here.
            if method.lower() not in {
                "get",
                "post",
                "put",
                "patch",
                "delete",
                "options",
                "head"
            }:
                continue

            endpoints.add(
                f"{method.upper()} {path}"
            )

    return endpoints


# ============================================================
# GENERATE ACCESS-CONTROL TESTS
# ============================================================

def generate_tests():

    openapi_endpoints = load_openapi_endpoints()

    role_matrix = load_yaml(ROLE_MATRIX_FILE)

    tests = []

    for role, endpoints in role_matrix.get("roles", {}).items():

        for endpoint, rule in endpoints.items():

            parts = endpoint.split(" ", 1)

            if len(parts) != 2:
                continue

            method = parts[0].upper()
            path = parts[1]

            normalized_endpoint = f"{method} {path}"

            # ------------------------------------------------
            # Verify endpoint exists in OpenAPI
            # ------------------------------------------------

            if normalized_endpoint not in openapi_endpoints:

                print(
                    f"WARNING: {normalized_endpoint} "
                    f"is not defined in openapi.yaml"
                )

                continue

            tests.append(
                {
                    "role": role,
                    "method": method,
                    "path": path,
                    "access": rule.get("access", "deny")
                }
            )

    return tests


# ============================================================
# DISPLAY GENERATED TESTS
# ============================================================

def print_tests(tests):

    print()
    print("Generated Access-Control Tests")
    print("=" * 70)

    for test in tests:

        print(
            f'{test["role"]:8} | '
            f'{test["method"]:7} | '
            f'{test["path"]:35} | '
            f'{test["access"]}'
        )

    print("=" * 70)

    print(
        f"Total tests: {len(tests)}"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    tests = generate_tests()

    print_tests(tests)
