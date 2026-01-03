from __future__ import annotations

import hashlib
import re
import os
from typing import Any, Mapping


_RENDER_PATTERN = re.compile(r"{{\s*([^{}]+?)\s*}}")


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def render_template(template: str, context: Mapping[str, Any] | None, allow_env: bool = False) -> str:
    if not context:
        context = {}

    def _replace(match: re.Match[str]) -> str:
        key = match.group(1).strip()
        if key.startswith("$ctx."):
            ctx_key = key[len("$ctx.") :]
            if ctx_key in context:
                return str(context[ctx_key])
            return ""
        if key.startswith("$env.") and allow_env:
            env_key = key[len("$env.") :]
            return os.getenv(env_key, "")
        return ""

    return _RENDER_PATTERN.sub(_replace, template)


def flatten_prompt_meta(meta: Mapping[str, Any] | None) -> dict[str, Any]:
    if not meta:
        return {}
    flattened: dict[str, Any] = {}
    for key, value in meta.items():
        if isinstance(value, (str, int, float, bool)):
            flattened[f"prompt_meta_{str(key)}"] = value
    return flattened
