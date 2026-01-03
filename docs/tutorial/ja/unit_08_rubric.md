kantan-agents チュートリアル 単元8（v0.1）

タイトル

ツールを使った評価とプロンプト分析

概要

この単元では一度生成した結果を、別の評価プロンプトで rubric 形式に評価する。いわゆる LLM-as-a-judge のパターンであり、rubric は Trace に保存されるため、評価の蓄積と比較に使える。

ステップ

- 生成用の Prompt で結果を作る。
- 評価用の Prompt で rubric を出力する。
- rubric を取得する。

実現方法

- 生成と評価を別の Agent で行う。
- 評価側は output_type=RUBRIC を使う。

ソースコード
```python
from kantan_agents import Agent, PolicyMode, Prompt, RUBRIC, get_context_with_policy

generator_prompt = Prompt(
    name="A",
    version="v1",
    text="Write a short, clear explanation of trace metadata in one sentence.",
)
generator = Agent(name="generator", instructions=generator_prompt)

context = get_context_with_policy(PolicyMode.RECOMMENDED)
context = generator.run("Explain trace metadata.", context)
generated = context["result"].final_output

judge_prompt = Prompt(
    name="A-judge",
    version="v1",
    text="Evaluate the answer and output a rubric with score (0-1) and comments.",
)
judge = Agent(name="judge", instructions=judge_prompt, output_type=RUBRIC)
judge_context = get_context_with_policy(PolicyMode.RECOMMENDED)
judge_context = judge.run(str(generated), judge_context)
print(judge_context["result"].final_output)
```
