from __future__ import annotations

from typing import Any


def judge(score: float, comments: list[str]) -> dict[str, Any]:
    return {
        "output_kind": "judge",
        "rubric": {
            "score": score,
            "comments": comments,
        },
    }
