from kantan_agents.judge import judge


def test_judge_returns_rubric_payload():
    payload = judge(0.5, ["ok"])
    assert payload == {
        "output_kind": "judge",
        "rubric": {"score": 0.5, "comments": ["ok"]},
    }
