from kantan_agents import RUBRIC


def test_rubric_schema_fields():
    schema = RUBRIC.model_json_schema()
    props = schema.get("properties", {})
    assert "score" in props
    assert "comments" in props
