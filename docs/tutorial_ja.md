kantan-agents チュートリアル（v0.1）

このチュートリアルは単元別のドキュメントに分割する。各単元でステップ、実現方法、ソースコードを示す。

最初に得ること

- model 名の切り替えを 1 行で行う
- tracing を早い段階で有効にして観測する
- Prompt メタデータと structured output で記録を充実させる

推奨ルート（Kantan-first）

1. まず `Agent` + `Prompt` でバージョン付き指示にする  
2. model 名を変えるだけでモデル切り替え  
3. tracing を早めに有効化（SQLite など）  
4. tools は entry-point 経由で追加し、`tool_rules` で制御  
5. structured output / `RUBRIC` で評価し、改善を回す  

Escape Hatches（必要な場合）

- async は ASGI のための escape hatch として、必要時のみ使う  
- Agents SDK を直接使う場合も、Prompt 情報と Trace metadata の一貫性を保つ  
- tracing processor は差し替え可能（SQLite/外部基盤など）  

前提

- OPENAI_API_KEY が環境変数に設定済み
- テスト/動作確認では gpt-5-mini を使用

Context と tool_rules の初期値

- Agent.run は context の辞書を返す。SDK の返値は context["result"] に入る。
- model を文字列で渡す場合は kantan-llm の get_llm で解決される。
- model に AsyncClientBundle/KantanAsyncLLM を渡す場合は AsyncOpenAI client を注入する。
- async が必要な場合は await Agent.run_async(...) を使う。
- context は省略できる。省略時は空の dict を自動生成する。
- 空の dict を渡した場合、Agent が tool/provider の tool_rules 設定を補完する。
- context を渡す場合は get_context_with_tool_rules(ToolRulesMode.ALLOW_ALL | ToolRulesMode.DENY_ALL | ToolRulesMode.RECOMMENDED) で事前作成できる。
- ToolRulesMode.RECOMMENDED は tool/provider の tool_rules 設定を基準にする。
- history が有効な場合は context["history"] に保存される。

単元一覧

- 単元1: 最小構成で Agent を動かす (`docs/tutorial/ja/unit_01_minimal.md`)
- 単元2: context でテンプレートを使う (`docs/tutorial/ja/unit_02_context_template.md`)
- 単元3: tracing を有効化して記録を残す (`docs/tutorial/ja/unit_03_tracing_sqlite.md`)
- 単元4: tool_rules でツール利用を制御する (`docs/tutorial/ja/unit_04_tool_rules.md`)
- 単元5: Prompt 型でバージョン付き指示を使う (`docs/tutorial/ja/unit_05_prompt.md`)
- 単元6: structured output を使う (`docs/tutorial/ja/unit_06_structured_output.md`)
- 単元7: handoffs でサブエージェントへ委譲する (`docs/tutorial/ja/unit_07_handoffs.md`)
- 単元8: ツールを使った評価とプロンプト分析 (`docs/tutorial/ja/unit_08_rubric.md`)
- 単元9: entry-point でツールを追加する (`docs/tutorial/ja/unit_09_entry_points.md`)
- 単元10: kantan-llm で Trace を検索する (`docs/tutorial/ja/unit_10_search_service.md`)

推奨ルート

- 単元1 で最小構成の Agent を動かす。
- 単元3 で tracing を早めに有効化する。
- 単元5 で Prompt メタデータを理解して記録を充実させる。
- 単元6 で structured output を使う。
- 単元2 はテンプレートや context 変数が必要になったら読む。
- 単元8 は評価、単元10 は検索に進む。
- 単元4 と単元9 は応用なので、必要になるまでは後回しでよい。
