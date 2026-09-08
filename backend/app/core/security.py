from typing import Any
from urllib.parse import unquote, urlparse

from app.core.exceptions import BadRequestError

SENSITIVE_KEY_MARKERS = (
    "password",
    "secret",
    "token",
    "authorization",
    "api_key",
    "apikey",
    "credential",
    "access_key",
    "private_key",
)


def is_sensitive_key(key: str) -> bool:
    normalized = key.lower().replace("-", "_")
    return any(marker in normalized for marker in SENSITIVE_KEY_MARKERS)


def redact_secrets(value: Any) -> Any:
    """Strip secrets from JSON payloads before they are stored."""
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            if is_sensitive_key(str(key)):
                redacted[key] = "***REDACTED***"
            else:
                redacted[key] = redact_secrets(item)
        return redacted
    if isinstance(value, list):
        return [redact_secrets(item) for item in value]
    return value


def validate_relative_path(path: str) -> str:
    """Reject absolute URLs, protocol-relative hosts, and path traversal."""
    candidate = path.strip()
    if not candidate.startswith("/") or candidate.startswith("//"):
        raise BadRequestError("Path must be a relative API path starting with '/'")
    if "\\" in candidate or "\\" in unquote(candidate):
        raise BadRequestError("Path must not contain backslashes")

    decoded = unquote(candidate)
    parsed = urlparse(candidate)
    decoded_parsed = urlparse(decoded)
    if parsed.scheme or parsed.netloc or decoded_parsed.scheme or decoded_parsed.netloc:
        raise BadRequestError("Absolute or host-qualified URLs are not allowed")
    if "://" in decoded:
        raise BadRequestError("Absolute or host-qualified URLs are not allowed")

    segments = (parsed.path or "").split("/")
    if ".." in segments or ".." in unquote(parsed.path or "").split("/"):
        raise BadRequestError("Path traversal is not allowed")

    normalized_path = parsed.path.rstrip("/") or "/"
    if parsed.query:
        return f"{normalized_path}?{parsed.query}"
    return normalized_path


def path_for_policy_match(path: str) -> str:
    parsed = urlparse(path)
    return (parsed.path or "/").rstrip("/") or "/"
