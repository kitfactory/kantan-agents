kantan-agents チュートリアル 単元5（v0.1）

タイトル

Prompt 型でバージョン付き指示を使う

概要

この単元では Prompt を使って指示のバージョン管理を行う。Prompt の情報は Trace メタデータに自動注入されるため、後から比較や分析がしやすい。
この情報は Trace の metadata に記録され、span ではない。

ステップ

- name/version/text を持つ Prompt を作成する。
- Prompt を Agent に渡す。
- run して結果を確認する。

実現方法

- Prompt.meta にはスカラー値のみを入れる。
- Prompt.id を省略した場合は自動生成される。

ソースコード
```python
from kantan_agents import Agent, PolicyMode, Prompt, get_context_with_policy

prompt = Prompt(
    name="qa",
    version="v1",
    text="Answer the user briefly.",
    meta={"variant": "A"},
)

agent = Agent(name="prompted-agent", instructions=prompt)
context = get_context_with_policy(PolicyMode.RECOMMENDED)
context = agent.run("Explain tracing in one sentence.", context)
print(context["result"].final_output)
```
