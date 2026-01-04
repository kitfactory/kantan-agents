kantan-agents チュートリアル 単元7（v0.1）

タイトル

handoffs でサブエージェントへ委譲する

概要

この単元では複数 Agent の役割分担を行う。manager Agent が状況に応じて specialist に委譲するため、複雑なタスクを分割できる。

ステップ

- 専門エージェントを用意する。
- manager に handoffs を渡す。
- manager から実行して委譲を確認する。

実現方法

- handoffs には Agent インスタンスを渡す。
- 指示文で担当範囲を明確にする。

ソースコード
```python
from kantan_agents import Agent, ToolRulesMode, get_context_with_tool_rules

booking_agent = Agent(name="booking", instructions="Handle booking tasks.")
refund_agent = Agent(name="refund", instructions="Handle refund tasks.")

manager = Agent(
    name="manager",
    instructions="Route tasks to specialists.",
    handoffs=[booking_agent, refund_agent],
)
context = get_context_with_tool_rules(ToolRulesMode.RECOMMENDED)
context = manager.run("I need a refund for last week's order.", context)
print(context["result"].final_output)
```
