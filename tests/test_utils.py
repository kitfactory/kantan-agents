from kantan_agents.utils import flatten_prompt_meta, render_template


def test_render_template_uses_ctx():
    template = "Hello {{ $ctx.name }}!"
    rendered = render_template(template, {"name": "world"})
    assert rendered == "Hello world!"


def test_render_template_uses_empty_string_for_missing_keys():
    template = "Hello {{ $ctx.name }}!"
    rendered = render_template(template, {"other": "x"})
    assert rendered == "Hello !"


def test_flatten_prompt_meta_filters_scalars():
    meta = {"variant": "A", "count": 2, "flag": True, "obj": {"a": 1}}
    flattened = flatten_prompt_meta(meta)
    assert flattened == {
        "prompt_meta_variant": "A",
        "prompt_meta_count": 2,
        "prompt_meta_flag": True,
    }
