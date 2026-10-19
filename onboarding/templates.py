"""Safe placeholder rendering for text templates."""
import re

PLACEHOLDER_RE = re.compile(r"{{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*}}")


def validate_template(template: str, allowed_fields: set[str]) -> None:
    found = set(PLACEHOLDER_RE.findall(template))
    unknown = sorted(found - allowed_fields)
    if unknown:
        raise ValueError(f"Unknown template placeholder(s): {', '.join(unknown)}")
    if not found:
        raise ValueError("Template must contain at least one {{ placeholder }}.")


def render_template(template: str, values: dict[str, str]) -> str:
    validate_template(template, set(values))
    return PLACEHOLDER_RE.sub(lambda match: values[match.group(1)], template)
