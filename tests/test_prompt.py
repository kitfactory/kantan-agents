import pytest

from kantan_agents.prompt import Prompt
from kantan_agents.utils import hash_text


def test_prompt_resolve_id_uses_hash_when_missing():
    prompt = Prompt(name="n", version="v1", text="hello")
    assert prompt.resolve_id() == hash_text("hello")


def test_prompt_resolve_id_uses_given_id():
    prompt = Prompt(name="n", version="v1", text="hello", id="pid")
    assert prompt.resolve_id() == "pid"


def test_prompt_requires_text():
    with pytest.raises(ValueError) as excinfo:
        Prompt(name="n", version="v1", text="")
    assert str(excinfo.value) == "[kantan-agents][E2] Prompt.text must not be empty"


def test_prompt_requires_name_and_version():
    with pytest.raises(ValueError) as excinfo:
        Prompt(name="", version="v1", text="hi")
    assert str(excinfo.value) == "[kantan-agents][E3] Prompt.name and Prompt.version must not be empty"

    with pytest.raises(ValueError) as excinfo:
        Prompt(name="n", version="", text="hi")
    assert str(excinfo.value) == "[kantan-agents][E3] Prompt.name and Prompt.version must not be empty"
