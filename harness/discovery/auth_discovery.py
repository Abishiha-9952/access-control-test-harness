import requests

def discover_auth(base_url, discovered_endpoints=None, credentials=None):
    """
    Dynamically identifies authentication mechanisms from discovered endpoints
    or OpenAPI specifications.
    """
    auth_context = {
        "mechanism": "unknown",
        "tokens": {},
        "headers": {},
        "login_endpoint": None
    }

    candidate_login_paths = []
    if discovered_endpoints:
        for ep in discovered_endpoints:
            path = ep.get("path", "").lower() if isinstance(ep, dict) else str(ep).lower()
            if any(keyword in path for keyword in ["login", "auth", "token", "session", "sign-in"]):
                candidate_login_paths.append(ep.get("path") if isinstance(ep, dict) else ep)

    if not candidate_login_paths:
        candidate_login_paths = ["/api/login", "/login", "/api/v1/auth/token"]

    if credentials:
        for path in candidate_login_paths:
            full_url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
            try:
                response = requests.post(full_url, json=credentials, timeout=5)
                if response.status_code in [200, 201]:
                    auth_context["login_endpoint"] = path
                    data = response.json() if "application/json" in response.headers.get("Content-Type", "") else {}

                    if "token" in data or "access_token" in data:
                        token = data.get("token") or data.get("access_token")
                        auth_context["mechanism"] = "JWT"
                        auth_context["tokens"]["default"] = token
                        auth_context["headers"]["Authorization"] = f"Bearer {token}"
                        break
                    elif response.cookies:
                        auth_context["mechanism"] = "cookie"
                        auth_context["headers"]["Cookie"] = "; ".join([f"{k}={v}" for k, v in response.cookies.items()])
                        break
            except Exception:
                continue

    return auth_context
