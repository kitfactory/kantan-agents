import os
import socket
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse
from typing import Callable

import agents
import pytest
from agents.models.openai_provider import OpenAIProvider
from kantan_llm.providers import resolve_provider_config

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

@dataclass(frozen=True)
class ModelTarget:
    name: str
    model: str
    base_url: str | None
    api_key: str | None
    model_provider_factory: Callable[[], object] | None


def _can_connect(base_url: str) -> bool:
    parsed = urlparse(base_url)
    if not parsed.hostname:
        return False
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    try:
        with socket.create_connection((parsed.hostname, port), timeout=0.5):
            return True
    except OSError:
        return False


def _integration_targets():
    targets: list[ModelTarget] = []
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        targets.append(ModelTarget("openai", "gpt-5-mini", None, openai_key, None))

    lmstudio_base_url = os.getenv("LMSTUDIO_BASE_URL", "http://192.168.11.16:1234")
    if _can_connect(lmstudio_base_url):
        lmstudio_model = os.getenv("LMSTUDIO_MODEL", "openai/gpt-oss-20b")
        lmstudio_key = os.getenv("LMSTUDIO_API_KEY", "lmstudio")
        cfg = resolve_provider_config(
            provider="lmstudio",
            api_key=lmstudio_key,
            base_url=lmstudio_base_url,
        )

        def _factory(cfg=cfg):
            return OpenAIProvider(
                api_key=cfg.api_key,
                base_url=cfg.base_url,
                use_responses=False,
            )

        targets.append(ModelTarget("lmstudio", lmstudio_model, cfg.base_url, cfg.api_key, _factory))

    if not targets:
        return [pytest.param(None, marks=pytest.mark.skip(reason="No model target available"))]
    return targets


@pytest.fixture(params=_integration_targets(), ids=lambda target: target.name if target else "no-target")
def model_target(request):
    if request.param is None:
        pytest.skip("No model target available")
    return request.param


@pytest.fixture
def model_env(monkeypatch, model_target):
    if model_target.base_url:
        agents.set_default_openai_api("chat_completions")
    else:
        agents.set_default_openai_api("responses")
    monkeypatch.setenv("OPENAI_DEFAULT_MODEL", model_target.model)
    return model_target
