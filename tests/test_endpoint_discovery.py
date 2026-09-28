from harness.discovery.endpoint_discovery import _extract_openapi_endpoints


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
