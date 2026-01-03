kantan-agents チュートリアル 単元1（v0.1）

タイトル

最小構成で Agent を動かす

概要

この単元では最小の実行例を示す。Agent を作成して run を呼び出し、context から SDK の返値を読む。以降の単元でも同じ流れを使う。

ステップ

- シンプルな instructions を用意する。
- 推奨の context を用意する。
- run を呼び出して context["result"] を読む。

実現方法

- get_context_with_policy(PolicyMode.RECOMMENDED) を基準にする。
- run 完了後の context には必ず result が入る。
- history が有効な場合は context["history"] に保存される。

ソースコード
```python
from kantan_agents import Agent, PolicyMode, get_context_with_policy

agent = Agent(name="basic-agent", instructions="You are a helpful assistant.")
context = get_context_with_policy(PolicyMode.RECOMMENDED)
context = agent.run("Hello", context)
print(context["result"].final_output)
```
