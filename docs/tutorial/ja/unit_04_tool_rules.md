kantan-agents チュートリアル 単元4（v0.1）

タイトル

tool_rules でツール利用を制御する

概要

この単元ではツールの許可・禁止とパラメータ制限を行う。allow/deny/params で構成し、allow と deny が競合した場合は deny を優先する。入力制限を加えることで安全性を高められる。ツール制御が不要な場合は後回しでよい。

ステップ

- ツール関数を用意して Agent に渡す。
- allow/deny/params を含む tool_rules 設定を作る。
- context に tool_rules 設定を入れて run する。

実現方法

- allow/deny は list か "*" を指定できる。
- params は JSON Schema の最小サブセットを使う。

ソースコード
```python
from kantan_agents import Agent, ToolRulesMode, get_context_with_tool_rules


def word_count(text: str) -> int:
    return len(text.split())


agent = Agent(
    name="tools-agent",
    instructions="Use word_count and answer briefly.",
    tools=[word_count],
)
tool_rules = {
    "allow": ["word_count"],
    "deny": [],
    "params": {"word_count": {"text": {"type": "string", "maxLength": 200}}},
}
context = get_context_with_tool_rules(ToolRulesMode.RECOMMENDED)
context["tool_rules"] = tool_rules
context = agent.run("Count the words in this sentence.", context)
print(context["result"].final_output)
```
