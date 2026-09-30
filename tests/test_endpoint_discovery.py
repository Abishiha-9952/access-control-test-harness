from harness.discovery.endpoint_discovery import (
    _extract_openapi_endpoints,
    discover_endpoints,
)


def test_extract_openapi_endpoints():
    document = {
        "openapi": "3.0.0",
        "info": {
            "title": "Test API",
            "version": "1.0.0"
        },
        "paths": {
            "/api/users": {
                "get": {
                    "parameters": [
                        {
                            "name": "page",
                            "in": "query",
                            "required": False
                        }
                    ]
                },
                "post": {
                    "parameters": [
                        {
                            "name": "username",
                            "in": "body",
                            "required": True
                        }
                    ]
                }
            },
            "/api/users/{id}": {
                "get": {
                    "parameters": [
                        {
                            "name": "id",
                            "in": "path",
                            "required": True
                        }
                    ]
                },
                "delete": {}
            }
        }
    }

    endpoints = _extract_openapi_endpoints(document)

    assert len(endpoints) == 4

    assert {
        "method": "GET",
        "path": "/api/users",
        "parameters": [
            {
                "name": "page",
                "location": "query",
                "required": False
            }
        ],
        "source": "openapi"
    } in endpoints

    assert {
        "method": "POST",
        "path": "/api/users",
        "parameters": [
            {
                "name": "username",
                "location": "body",
                "required": True
            }
        ],
        "source": "openapi"
    } in endpoints

    assert {
        "method": "GET",
        "path": "/api/users/{id}",
        "parameters": [
            {
                "name": "id",
                "location": "path",
                "required": True
            }
        ],
        "source": "openapi"
    } in endpoints

    assert {
        "method": "DELETE",
        "path": "/api/users/{id}",
        "parameters": [],
        "source": "openapi"
    } in endpoints


def test_discover_endpoints_with_route_metadata(monkeypatch):
    def fake_discover_api_description(base_url):
        return None

    monkeypatch.setattr(
        "harness.discovery.endpoint_discovery.discover_api_description",
        fake_discover_api_description,
    )

    routes = [
        {
            "path": "/api/products",
            "methods": ["GET", "POST"],
        },
        {
            "path": "/api/products/{id}",
            "methods": ["GET", "DELETE"],
            "parameters": [
                {
                    "name": "id",
                    "location": "path",
                    "required": True,
                }
            ],
        },
    ]

    endpoints = discover_endpoints(
        "http://127.0.0.1:5000",
        route_metadata=routes,
    )

    assert len(endpoints) == 4

    assert {
        "method": "GET",
        "path": "/api/products/{id}",
        "parameters": [
            {
                "name": "id",
                "location": "path",
                "required": True,
            }
        ],
        "source": "route_metadata",
    } in endpoints

    assert {
        "method": "DELETE",
        "path": "/api/products/{id}",
        "parameters": [
            {
                "name": "id",
                "location": "path",
                "required": True,
            }
        ],
        "source": "route_metadata",
    } in endpoints


def test_discover_endpoints_returns_empty_when_nothing_found(monkeypatch):
    def fake_discover_api_description(base_url):
        return None

    monkeypatch.setattr(
        "harness.discovery.endpoint_discovery.discover_api_description",
        fake_discover_api_description,
    )

    endpoints = discover_endpoints(
        "http://127.0.0.1:5000"
    )

    assert endpoints == []


def test_discover_endpoints_with_yaml_openapi(monkeypatch):
    document = {
        "openapi": "3.0.0",
        "info": {
            "title": "YAML Test API",
            "version": "1.0.0",
        },
        "paths": {
            "/api/users": {
                "get": {},
            },
            "/api/users/{id}": {
                "delete": {},
            },
        },
    }

    def fake_discover_api_description(base_url):
        return {
            "url": "http://127.0.0.1:5000/openapi.yaml",
            "document": document,
            "format": "yaml",
        }

    monkeypatch.setattr(
        "harness.discovery.endpoint_discovery.discover_api_description",
        fake_discover_api_description,
    )

    endpoints = discover_endpoints(
        "http://127.0.0.1:5000"
    )

    assert len(endpoints) == 2

    assert {
        "method": "GET",
        "path": "/api/users",
        "parameters": [],
        "source": "openapi",
    } in endpoints

    assert {
        "method": "DELETE",
        "path": "/api/users/{id}",
        "parameters": [],
        "source": "openapi",
    } in endpoints
