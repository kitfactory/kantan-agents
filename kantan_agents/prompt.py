from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .utils import hash_text


@dataclass(frozen=True)
class Prompt:
    name: str
    version: str
    text: str
    meta: Mapping[str, Any] | None = None
    id: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("[kantan-agents][E3] Prompt.name and Prompt.version must not be empty")
        if not isinstance(self.version, str) or not self.version.strip():
            raise ValueError("[kantan-agents][E3] Prompt.name and Prompt.version must not be empty")
        if not isinstance(self.text, str) or not self.text.strip():
            raise ValueError("[kantan-agents][E2] Prompt.text must not be empty")

    def resolve_id(self) -> str:
        if self.id:
            return self.id
        return hash_text(self.text)
