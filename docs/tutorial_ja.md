kantan-agents チュートリアル（v0.1）

このチュートリアルは単元別のドキュメントに分割する。各単元でステップ、実現方法、ソースコードを示す。

前提

- OPENAI_API_KEY が環境変数に設定済み
- テスト/動作確認では gpt-5-mini を使用

Context と policy の初期値

- Agent.run は context の辞書を返す。SDK の返値は context["result"] に入る。
- async が必要な場合は await Agent.run_async(...) を使う。
- context は省略できる。省略時は空の dict を自動生成する。
- 空の dict を渡した場合、Agent が tool/provider の policy を補完する。
- context を渡す場合は get_context_with_policy(PolicyMode.ALLOW_ALL | PolicyMode.DENY_ALL | PolicyMode.RECOMMENDED) で事前作成できる。
- PolicyMode.RECOMMENDED は tool/provider の policy を基準にする。
- history が有効な場合は context["history"] に保存される。

単元一覧

- 単元1: 最小構成で Agent を動かす (`docs/tutorial/ja/unit_01_minimal.md`)
- 単元2: context でテンプレートを使う (`docs/tutorial/ja/unit_02_context_template.md`)
- 単元3: tracing を有効化して記録を残す (`docs/tutorial/ja/unit_03_tracing_sqlite.md`)
- 単元4: policy でツール利用を制御する (`docs/tutorial/ja/unit_04_policy_tools.md`)
- 単元5: Prompt 型でバージョン付き指示を使う (`docs/tutorial/ja/unit_05_prompt.md`)
- 単元6: structured output を使う (`docs/tutorial/ja/unit_06_structured_output.md`)
- 単元7: handoffs でサブエージェントへ委譲する (`docs/tutorial/ja/unit_07_handoffs.md`)
- 単元8: ツールを使った評価とプロンプト分析 (`docs/tutorial/ja/unit_08_rubric.md`)
- 単元9: entry-point でツールを追加する (`docs/tutorial/ja/unit_09_entry_points.md`)
- 単元10: kantan-llm で Trace を検索する (`docs/tutorial/ja/unit_10_search_service.md`)

推奨ルート

- 単元1 → 単元2 で context とテンプレートの基本を押さえる。
- 単元5 で Prompt メタデータを理解する。
- 単元3 で tracing、単元8 で LLM-as-a-judge を学ぶ。
- 最小の context テンプレートは `docs/usage.md` を参照する。
- 単元4 と単元9 は応用なので、必要になるまでは後回しでよい。
