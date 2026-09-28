"""
API description discovery.

Discovers OpenAPI or Swagger API descriptions exposed by an
authorized target.
"""

from urllib.parse import urljoin

import requests
import yaml


API_DESCRIPTION_PATHS = (
    "/openapi.json",
    "/swagger.json",
    "/openapi.yaml",
    "/swagger.yaml",
    "/api/openapi.json",
    "/api/swagger.json",
)


def _is_api_description(document):
    """Return True when a document looks like OpenAPI or Swagger."""
    if not isinstance(document, dict):
        return False

    # OpenAPI 3.x
    if isinstance(document.get("openapi"), str):
        return True

    # Swagger 2.x
    if isinstance(document.get("swagger"), str):
        return True

    return False


def discover_api_description(base_url):
    """
    Discover an OpenAPI/Swagger description.

    Args:
        base_url: Authorized target base URL.

    Returns:
        A dictionary containing the discovered document, or None.
    """
    base_url = base_url.rstrip("/") + "/"

    headers = {
        "User-Agent": "AccessControlTestHarness/1.0"
    }

    for path in API_DESCRIPTION_PATHS:
        url = urljoin(base_url, path.lstrip("/"))

        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=5,
            )

            if response.status_code != 200:
                continue

            content_type = response.headers.get(
                "Content-Type",
                ""
            ).lower()

            # Try JSON first.
            try:
                document = response.json()

                if _is_api_description(document):
                    return {
                        "url": url,
                        "document": document,
                        "format": "json",
                    }

            except ValueError:
                pass

            # Try YAML when the response is YAML or when the
            # endpoint uses a .yaml/.yml extension.
            if (
                "yaml" in content_type
                or "yml" in content_type
                or path.endswith((".yaml", ".yml"))
            ):
                try:
                    document = yaml.safe_load(response.text)

                    if _is_api_description(document):
                        return {
                            "url": url,
                            "document": document,
                            "format": "yaml",
                        }

                except yaml.YAMLError:
                    continue

        except requests.RequestException:
            continue

    return None
