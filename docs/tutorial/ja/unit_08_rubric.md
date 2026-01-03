kantan-agents チュートリアル 単元8（v0.1）

タイトル

ツールを使った評価とプロンプト分析

概要

この単元ではツール実行と rubric 出力を組み合わせる。rubric は Trace に保存されるため、評価の蓄積と比較に使える。

ステップ

- ツール関数を用意する。
- output_type に RUBRIC を指定する。
- run して rubric を取得する。

実現方法

- tools と output_type=RUBRIC を併用する。
- rubric の内容は final_output から読める。

ソースコード
```python
from kantan_agents import Agent, PolicyMode, RUBRIC, get_context_with_policy


def word_count(text: str) -> int:
    return len(text.split())

agent = Agent(
    name="evaluator",
    instructions="Use word_count and then output a rubric with score and comments.",
    tools=[word_count],
    output_type=RUBRIC,
)
context = get_context_with_policy(PolicyMode.RECOMMENDED)
context = agent.run("Assess this sentence: 'Tracing enables analysis.'", context)
print(context["result"].final_output)
```
