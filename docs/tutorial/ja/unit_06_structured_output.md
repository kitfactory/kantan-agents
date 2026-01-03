kantan-agents チュートリアル 単元6（v0.1）

タイトル

structured output を使う

概要

この単元では Pydantic モデルを使った構造化出力を扱う。structured output は型が保証されるため、後段の処理が簡潔になる。

ステップ

- Pydantic モデルを定義する。
- output_type として Agent に渡す。
- output_dest を指定して structured output を context に保存する。
- final_output をモデルとして読む。

実現方法

- final_output はモデルのインスタンスになる。
- モデルの属性アクセスで値を取り出せる。
- output_dest を指定すると context に dict 形式で保存される。
- output_dest は既存キーを上書きし、dict で取得できない場合は保存されない。
- output_dest の命名は内容が分かるキー（例: summary_json, evaluation_rubric）を推奨する。

ソースコード
```python
from pydantic import BaseModel
from kantan_agents import Agent, PolicyMode, get_context_with_policy

class Summary(BaseModel):
    title: str
    bullets: list[str]

agent = Agent(
    name="structured-agent",
    instructions="Summarize the input.",
    output_type=Summary,
    output_dest="summary_json",
)
context = get_context_with_policy(PolicyMode.RECOMMENDED)
context = agent.run("Summarize the release notes.", context)
print(context["result"].final_output)
print(context["summary_json"]["title"])
```
