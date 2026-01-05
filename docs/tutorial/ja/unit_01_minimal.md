kantan-agents チュートリアル 単元1（v0.1）

タイトル

最小構成で Agent を動かす

概要

この単元では最小の実行例を示す。Agent を作成して run を呼び出し、返ってきた context から SDK の返値を読む。context の詳細は次の単元で扱う。

ステップ

- シンプルな instructions を用意する。
- run を呼び出す（context は省略する）。
- context["result"] を読む。

実現方法

- context を渡さない場合は空の dict を自動生成する。
- run 完了後の context には必ず result が入る。
- history が有効な場合は context["history"] に保存される。
- model を文字列で渡す場合は kantan-llm の get_llm で解決される。
- model に AsyncClientBundle/KantanAsyncLLM を渡す場合は AsyncOpenAI client を注入する。

よくある失敗

- context を変数に受け取らず result を参照できない
- context["result"] ではなく context 自体を出力してしまう

ソースコード
```python
from kantan_agents import Agent

agent = Agent(name="basic-agent", instructions="You are a helpful assistant.")
context = agent.run("Hello")
print(context["result"].final_output)
```

model を指定する場合
```python
from kantan_agents import Agent

agent = Agent(name="basic-agent", instructions="You are a helpful assistant.", model="gpt-5-mini")
context = agent.run("Hello")
print(context["result"].final_output)
```
