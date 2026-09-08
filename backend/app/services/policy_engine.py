import re
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.security import path_for_policy_match
from app.models.policy import Policy

_PARAM_PATTERN = re.compile(r"\{[^{}/]+\}")


def _is_param_segment(segment: str) -> bool:
    return segment.startswith("{") and segment.endswith("}") and len(segment) > 2


def pattern_to_regex(path_pattern: str) -> re.Pattern[str]:
    normalized = path_for_policy_match(path_pattern)
    regex = "^"
    cursor = 0
    for match in _PARAM_PATTERN.finditer(normalized):
        regex += re.escape(normalized[cursor:match.start()])
        regex += r"[^/]+"
        cursor = match.end()
    regex += re.escape(normalized[cursor:])
    regex += "$"
    return re.compile(regex)


def path_matches(path_pattern: str, request_path: str) -> bool:
    return bool(pattern_to_regex(path_pattern).fullmatch(path_for_policy_match(request_path)))


def _specificity(path_pattern: str) -> tuple[int, int, int]:
    segments = [segment for segment in path_for_policy_match(path_pattern).strip("/").split("/") if segment]
    static_count = sum(1 for segment in segments if not _is_param_segment(segment))
    param_count = len(segments) - static_count
    return (static_count, len(segments), -param_count)


def find_matching_policy(
    db: Session,
    agent_id: UUID,
    method: str,
    request_path: str,
) -> Policy | None:
    candidates = (
        db.query(Policy)
        .filter(
            Policy.agent_id == agent_id,
            Policy.method == method.upper(),
            Policy.active.is_(True),
        )
        .all()
    )
    matches = [policy for policy in candidates if path_matches(policy.path_pattern, request_path)]
    if not matches:
        return None
    matches.sort(key=lambda policy: (policy.priority, *_specificity(policy.path_pattern)), reverse=True)
    return matches[0]
