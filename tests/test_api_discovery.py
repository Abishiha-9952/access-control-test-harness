from unittest.mock import Mock

from harness.discovery.api_discovery import discover_api_description


def test_discover_openapi_json(monkeypatch):
    response = Mock()
    response.status_code = 200
    response.headers = {"Content-Type": "application/json"}
    response.json.return_value = {
        "openapi": "3.0.0",
        "info": {
            "title": "Test API",
            "version": "1.0.0",
        },
        "paths": {
            "/users": {
                "get": {}
            }
        },
    }

    monkeypatch.setattr(
        "harness.discovery.api_discovery.requests.get",
        lambda *args, **kwargs: response,
    )

    result = discover_api_description("http://example.com")

    assert result is not None
    assert result["format"] == "json"
    assert result["url"] == "http://example.com/openapi.json"
    assert result["document"]["openapi"] == "3.0.0"


def test_discover_swagger_json(monkeypatch):
    response = Mock()
    response.status_code = 200
    response.headers = {"Content-Type": "application/json"}
    response.json.return_value = {
        "swagger": "2.0",
        "info": {
            "title": "Test API",
            "version": "1.0.0",
        },
        "paths": {
            "/users": {
                "get": {}
            }
        },
    }

    def fake_get(url, **kwargs):
        if url.endswith("/swagger.json"):
            return response

        not_found = Mock()
        not_found.status_code = 404
        not_found.headers = {}
        return not_found

    monkeypatch.setattr(
        "harness.discovery.api_discovery.requests.get",
        fake_get,
    )

    result = discover_api_description("http://example.com")

    assert result is not None
    assert result["format"] == "json"
    assert result["url"] == "http://example.com/swagger.json"
    assert result["document"]["swagger"] == "2.0"


def test_discover_openapi_yaml(monkeypatch):
    response = Mock()
    response.status_code = 200
    response.headers = {
        "Content-Type": "application/yaml"
    }
    response.text = """
openapi: 3.0.0
info:
  title: Test API
  version: 1.0.0
paths:
  /users:
    get: {}
"""

    response.json.side_effect = ValueError()

    def fake_get(url, **kwargs):
        if url.endswith("/openapi.yaml"):
            return response

        not_found = Mock()
        not_found.status_code = 404
        not_found.headers = {}
        return not_found

    monkeypatch.setattr(
        "harness.discovery.api_discovery.requests.get",
        fake_get,
    )

    result = discover_api_description("http://example.com")

    assert result is not None
    assert result["format"] == "yaml"
    assert result["url"] == "http://example.com/openapi.yaml"
    assert result["document"]["openapi"] == "3.0.0"


def test_ignore_invalid_api_document(monkeypatch):
    response = Mock()
    response.status_code = 200
    response.headers = {"Content-Type": "application/json"}
    response.json.return_value = {
        "message": "This is not an API specification"
    }
    response.text = '{"message": "This is not an API specification"}'

    monkeypatch.setattr(
        "harness.discovery.api_discovery.requests.get",
        lambda *args, **kwargs: response,
    )

    result = discover_api_description("http://example.com")

    assert result is None


def test_handle_request_failure(monkeypatch):
    import requests

    def fake_get(*args, **kwargs):
        raise requests.RequestException("Connection failed")

    monkeypatch.setattr(
        "harness.discovery.api_discovery.requests.get",
        fake_get,
    )

    result = discover_api_description("http://example.com")

    assert result is None
