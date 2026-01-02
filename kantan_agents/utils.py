from __future__ import annotations

import hashlib
import re
from typing import Any, Mapping


_RENDER_PATTERN = re.compile(r"{{\s*([a-zA-Z0-9_.-]+)\s*}}")


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def render_template(template: str, render_vars: Mapping[str, Any] | None) -> str:
    if not render_vars:
        return template

    def _replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in render_vars:
            return match.group(0)
        return str(render_vars[key])

    return _RENDER_PATTERN.sub(_replace, template)


def flatten_prompt_meta(meta: Mapping[str, Any] | None) -> dict[str, Any]:
    if not meta:
        return {}
    flattened: dict[str, Any] = {}
    for key, value in meta.items():
        if isinstance(value, (str, int, float, bool)):
            flattened[f"prompt_meta_{str(key)}"] = value
    return flattened
