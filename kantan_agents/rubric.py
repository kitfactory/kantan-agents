from __future__ import annotations

from pydantic import BaseModel


class _RubricSchema(BaseModel):
    score: float
    comments: list[str]


RUBRIC = _RubricSchema
