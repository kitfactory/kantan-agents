from __future__ import annotations

from typing import Callable

import agents


def add_trace_processor(processor: Callable) -> None:
    agents.add_trace_processor(processor)


def set_trace_processors(processors: list[Callable]) -> None:
    agents.set_trace_processors(processors)
