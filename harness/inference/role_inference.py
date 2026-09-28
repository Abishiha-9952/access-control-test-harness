import base64
import json

def _decode_jwt_payload(token):
    """Utility to extract claims from standard JWT payloads."""
    try:
        parts = token.split(".")
        if len(parts) == 3:
            padding = "=" * (4 - len(parts[1]) % 4)
            payload_b64 = parts[1] + padding
            decoded = base64.urlsafe_b64decode(payload_b64).decode("utf-8")
            return json.loads(decoded)
    except Exception:
        pass
    return {}

def infer_actors(auth_contexts_by_user):
    """
    Dynamically infers actor roles from authentication contexts and token claims.
    """
    actors = {
        "anonymous": {
            "role": "anonymous",
            "headers": {}
        }
    }

    for user_id, auth_ctx in auth_contexts_by_user.items():
        headers = auth_ctx.get("headers", {})
        inferred_role = "authenticated_user"

        if auth_ctx.get("mechanism") == "JWT":
            token = auth_ctx.get("tokens", {}).get("default", "")
            payload = _decode_jwt_payload(token)

            role_claim = payload.get("role") or payload.get("roles") or payload.get("scope")
            if role_claim:
                inferred_role = str(role_claim).lower()
            elif payload.get("is_admin") or payload.get("admin"):
                inferred_role = "admin"

        actors[f"actor_{user_id}"] = {
            "role": inferred_role,
            "headers": headers
        }

    return actors
