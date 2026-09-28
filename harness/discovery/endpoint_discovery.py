"""
Endpoint discovery and normalization.

Converts an OpenAPI/Swagger document or permitted route metadata
into a normalized endpoint inventory that can be consumed by
the other project modules.
"""

from .api_discovery import discover_api_description


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


def _normalize_parameter(parameter):
    """Convert an OpenAPI parameter into the project's common format."""
    return {
        "name": parameter.get("name"),
        "location": parameter.get("in"),
        "required": parameter.get("required", False),
    }


def _extract_openapi_endpoints(document):
    """Extract normalized endpoints from an OpenAPI/Swagger document."""
    endpoints = []

    paths = document.get("paths", {})

    if not isinstance(paths, dict):
        return endpoints

    for path, path_item in paths.items():

        if not isinstance(path_item, dict):
            continue

        # Parameters defined at the path level.
        path_parameters = path_item.get("parameters", [])

        for method, operation in path_item.items():

            method_lower = method.lower()

            if method_lower not in HTTP_METHODS:
                continue

            if not isinstance(operation, dict):
                continue

            parameters = []

            # Add path-level parameters.
            for parameter in path_parameters:
                if isinstance(parameter, dict):
                    parameters.append(
                        _normalize_parameter(parameter)
                    )

            # Add operation-level parameters.
            for parameter in operation.get("parameters", []):
                if isinstance(parameter, dict):
                    parameters.append(
                        _normalize_parameter(parameter)
                    )

            endpoints.append(
                {
                    "method": method_lower.upper(),
                    "path": path,
                    "parameters": parameters,
                    "source": "openapi",
                }
            )

    return endpoints


def normalize_routes(routes):
    """
    Normalize permitted route metadata.

    This allows another authorized discovery source to provide
    route information without hardcoding Target 1, Target 2,
    or Target 3 into this module.

    Args:
        routes: Iterable of route dictionaries.

    Returns:
        List of normalized endpoint dictionaries.
    """
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

            endpoints.append(
                {
                    "method": method,
                    "path": path,
                    "parameters": route.get("parameters", []),
                    "source": route.get(
                        "source",
                        "route_metadata"
                    ),
                }
            )

    return endpoints


def discover_endpoints(base_url, route_metadata=None):
    """
    Discover and normalize endpoints for an authorized target.

    The function first attempts to discover an OpenAPI/Swagger
    description. If one is not available, optional permitted
    route metadata can be normalized instead.

    Args:
        base_url: Authorized target base URL.
        route_metadata: Optional permitted route metadata.

    Returns:
        List of normalized endpoint dictionaries.
    """
    api_description = discover_api_description(base_url)

    if api_description is not None:

        document = api_description["document"]

        if api_description["format"] == "json":
            return _extract_openapi_endpoints(document)

    # Fallback to permitted route metadata.
    if route_metadata is not None:
        return normalize_routes(route_metadata)

    return []
