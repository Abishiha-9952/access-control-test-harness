import yaml


HTTP_METHODS = {
    "get",
    "post",
    "put",
    "patch",
    "delete",
    "head",
    "options",
    "trace",
}


def load_openapi_spec(file_path):
    """Load and validate an OpenAPI YAML specification."""

    with open(file_path, "r", encoding="utf-8") as file:
        spec = yaml.safe_load(file)

    if not isinstance(spec, dict):
        raise ValueError("Invalid OpenAPI specification")

    if "openapi" not in spec:
        raise ValueError("Missing 'openapi' field")

    if "info" not in spec:
        raise ValueError("Missing 'info' field")

    if "paths" not in spec:
        raise ValueError("Missing 'paths' field")

    if not isinstance(spec["paths"], dict):
        raise ValueError("'paths' must be a mapping")

    return spec


def parse_parameter(parameter):
    """Normalize an OpenAPI parameter."""

    if not isinstance(parameter, dict):
        return None

    schema = parameter.get("schema", {})

    if not isinstance(schema, dict):
        schema = {}

    return {
        "name": parameter.get("name", ""),
        "in": parameter.get("in", ""),
        "required": parameter.get("required", False),
        "type": schema.get("type"),
        "format": schema.get("format"),
        "description": parameter.get("description", ""),
    }


def parse_parameters(path_parameters, operation_parameters):
    """
    Combine path-level and operation-level parameters.

    Operation-level parameters override path-level parameters
    with the same name and location.
    """

    combined = {}

    for parameter in path_parameters:
        parsed = parse_parameter(parameter)

        if parsed:
            key = (parsed["name"], parsed["in"])
            combined[key] = parsed

    for parameter in operation_parameters:
        parsed = parse_parameter(parameter)

        if parsed:
            key = (parsed["name"], parsed["in"])
            combined[key] = parsed

    return list(combined.values())


def detect_path_parameters(path):
    """
    Detect parameters written directly in the URL.

    Example:
        /api/users/{id}

    returns:
        ["id"]
    """

    parameters = []

    parts = path.split("{")

    for part in parts[1:]:
        if "}" in part:
            name = part.split("}", 1)[0]

            if name:
                parameters.append(name)

    return parameters


def parse_endpoints(spec):
    """Extract endpoints, methods, parameters and metadata."""

    endpoints = []

    paths = spec.get("paths", {})

    for path, path_item in paths.items():

        if not isinstance(path_item, dict):
            continue

        path_parameters = path_item.get("parameters", [])

        for method, operation in path_item.items():

            method = method.lower()

            if method not in HTTP_METHODS:
                continue

            if not isinstance(operation, dict):
                operation = {}

            operation_parameters = operation.get(
                "parameters",
                []
            )

            parameters = parse_parameters(
                path_parameters,
                operation_parameters
            )

            # Detect {id}-style parameters even when the
            # OpenAPI document does not explicitly define them.
            detected_parameters = detect_path_parameters(path)

            existing_names = {
                parameter["name"]
                for parameter in parameters
                if parameter["in"] == "path"
            }

            for name in detected_parameters:

                if name not in existing_names:

                    parameters.append({
                        "name": name,
                        "in": "path",
                        "required": True,
                        "type": None,
                        "format": None,
                        "description": "",
                    })

            endpoints.append({
                "path": path,
                "method": method.upper(),
                "operation_id": operation.get(
                    "operationId"
                ),
                "summary": operation.get(
                    "summary",
                    ""
                ),
                "description": operation.get(
                    "description",
                    ""
                ),
                "security": operation.get(
                    "security",
                    spec.get("security", [])
                ),
                "parameters": parameters,
            })

    return endpoints


def parse_openapi(file_path):
    """Load and parse an OpenAPI specification."""

    spec = load_openapi_spec(file_path)

    components = spec.get("components", {})

    return {
        "openapi_version": spec.get("openapi"),
        "title": spec.get("info", {}).get("title", ""),
        "version": spec.get("info", {}).get("version", ""),
        "security_schemes": components.get(
            "securitySchemes", {}
        ),
        "security": spec.get("security", []),
        "endpoints": parse_endpoints(spec),
    }


if __name__ == "__main__":
    print("OpenAPI parser module")
