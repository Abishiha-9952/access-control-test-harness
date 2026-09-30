"""
Endpoint discovery and normalization.

Converts an OpenAPI/Swagger document or permitted route metadata
into a normalized endpoint inventory that can be consumed by
the other project modules.
"""

from .api_discovery import discover_api_description

HTTP_METHODS = {
    "get", "post", "put", "patch", "delete", "head", "options", "trace",
}


def _normalize_parameter(parameter):
    return {
        "name": parameter.get("name"),
        "location": parameter.get("in"),
        "required": parameter.get("required", False),
    }


def _extract_openapi_endpoints(document):
    endpoints = []
    paths = document.get("paths", {})

    if not isinstance(paths, dict):
        return endpoints

    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue

        path_parameters = path_item.get("parameters", [])

        for method, operation in path_item.items():
            method_lower = method.lower()

            if method_lower not in HTTP_METHODS:
                continue

            if not isinstance(operation, dict):
                continue

            parameters = []

            for parameter in path_parameters:
                if isinstance(parameter, dict):
                    parameters.append(
                        _normalize_parameter(parameter)
                    )

            for parameter in operation.get("parameters", []):
                if isinstance(parameter, dict):
                    parameters.append(
                        _normalize_parameter(parameter)
                    )

            endpoints.append({
                "method": method_lower.upper(),
                "path": path,
                "parameters": parameters,
                "source": "openapi",
            })

    return endpoints


def normalize_routes(routes):
    endpoints = []

    for route in routes:
        if not isinstance(route, dict):
            continue

        path = route.get("path")
        methods = route.get("methods", [])

        if not path:
            continue

        if not isinstance(methods, (list, tuple, set)):
            continue

        for method in methods:
            method = str(method).upper()

            if method not in {m.upper() for m in HTTP_METHODS}:
                continue

            endpoints.append({
                "method": method,
                "path": path,
                "parameters": route.get("parameters", []),
                "source": route.get("source", "route_metadata"),
            })

    return endpoints


def discover_endpoints(base_url, route_metadata=None):
    api_description = discover_api_description(base_url)

    if api_description is not None:
        document = api_description["document"]
        return _extract_openapi_endpoints(document)

    if route_metadata is not None:
        return normalize_routes(route_metadata)

    return []
