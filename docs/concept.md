kantan-agents 要件定義（v0.1）

目的

- kantan-llm の get_llm により多様なプロバイダ/モデルの LLM を利用しつつ、Trace 機能も活用する。
- kantan-agents は OpenAI Agents SDK を基盤にしながら、kantan-llm の LLM/Trace を組み合わせることで、
  自動的に整った Trace 記録が残る体験を提供する（本ライブラリの重要点）。
- さらに別ライブラリの kantan-lab を提供し、蓄積されたデータからプロンプトの改善・進化を行う。

想定ユーザーと困りごと

- Agents SDK を使いつつ、プロンプト/評価の履歴を手作業で整理したくない開発者
- LLM/Trace の切り替えや記録の一貫性を保ちたい運用担当

ユースケース

- Agents SDK のコードを大きく変えずに、統一された Trace メタデータを自動保存したい
- kantan-lab でプロンプトのバージョンや評価結果を分析したい

使用するライブラリ

- OpenAI Agents SDK
- kantan-llm（get_llm / Trace）
- kantan-lab（分析・改善）

ソフトウェア全体設計の概要

- kantan-agents は Agents SDK の薄いラッパとして、LLM 取得と Trace 記録を kantan-llm に寄せる。
- Trace に保存するメタデータのキーを標準化し、kantan-lab で分析しやすい構造にする。
- Trace/検索基盤自体は再実装しない。

非ゴール

- Chat/Responses の選択に介入しない（Agents SDK の判断に任せる）
- Tracer/検索基盤を再実装しない（kantan-llm を正本にする）
- Prompt レジストリや差分管理など“管理系”は持たない（kantan-lab へ）

機能一覧（Spec ID 付き）

| Spec ID | 機能 | 詳細 | 依存関係 | MVP/Phase |
| --- | --- | --- | --- | --- |
| F-01 | Agents SDK tracing API の再エクスポート | add_trace_processor / set_trace_processors を薄く再エクスポート | OpenAI Agents SDK | v0.1 |
| F-02 | Agent クラス（コンストラクタ） | instructions 必須、renderer 任意、Prompt 指定可 | OpenAI Agents SDK | v0.1 |
| F-03 | Agent.run と Trace メタデータ自動注入 | prompt/agent/run の標準キーを Trace に注入 | kantan-llm Trace | v0.1 |
| F-04 | Prompt 型（kantan-lab 管理） | name/version/text/meta/id を最小定義 | kantan-lab | v0.1 |
| F-05 | Trace メタデータ標準キー | kantan-lab 分析用のキー規約 | kantan-llm Trace / kantan-lab | v0.1 |
| F-06 | judge() ヘルパ | rubric structured output の自動保存（内部補助、基本は RUBRIC） | kantan-llm | v0.2 |
| F-07 | 最小利用ドキュメント | tracing 設定 → Agent 作成 → run → SQLite 検索 | kantan-llm | v0.1 |
| F-08 | Handoff のサポート | Agent インスタンス間の handoff を利用可能にする | OpenAI Agents SDK | v0.1 |
| F-09 | RUBRIC schema 定数 | output_type=RUBRIC で rubric structured output を簡易化 | kantan-llm | v0.2 |
| F-10 | Context/Policy 機能 | Context の返却、policy 制御、テンプレート変数/環境変数対応 | OpenAI Agents SDK | v0.2 |
| F-11 | Tool Policy 収集 | entry-point から tool/policy を収集して統合 | importlib.metadata | v0.2 |
| F-12 | History 機能 | 入力/応答の履歴を context に保持 | OpenAI Agents SDK | v0.2 |
| F-13 | output_dest 機能 | structured output を context の任意キーに保存 | OpenAI Agents SDK | v0.2 |

主要な仕様メモ

- Agent.run
  - シグネチャ: run(input: str, context: dict | None = None) -> context
  - context は rendering/policy/result を含む辞書
  - context が None または空の dict の場合は Agent 内で補完する
  - history は context["history"] に配列として保持する
  - output_dest 指定時は structured output を context に保存する
  - context.result は Agents SDK の返値
- テンプレート変数
  - {{ }} 内で $ctx.xxx と $env.ENV_NAME を展開する
  - 未定義参照は空文字
  - $env はコンストラクタで opt-in（default False）
- Trace metadata 自動注入（Prompt 指定時）
  - agent_name
  - prompt_name
  - prompt_version
  - prompt_id（Prompt が id を持てばそれ、なければ SHA-256 で hash(prompt.text)）
  - prompt_meta_*（Prompt.meta をフラットに展開、スカラーのみ）
  - agent_run_id（run ごとに一意）
- instructions が str の場合は注入最小（任意）
  - agent_name と agent_run_id は入れる
  - prompt_name は agent 名から取る
  - prompt_id がない場合は SHA-256 のハッシュにする
- Policy
  - 形式: allow/deny/params（階層なし）
  - allow/deny は "*" を許可
  - 競合時は deny 優先
  - params は JSON Schema 互換の最小サブセット
- Policy レイヤーと統合順序
  - 基本ポリシー → tool 由来ポリシー → 明示ポリシー
  - allow/deny は union、params は tool 名ごとに merge
- Tool Policy 収集
  - project.entry-points."kantan_agents.tools" から provider を収集する
- History
  - Agent の history 引数で保存数を制御する（default 50）
  - history=0 の場合は保存しない
- Prompt 型（kantan-lab 側で管理）
  - name: str
  - version: str
  - text: str
  - meta: Mapping[str, Any] | None（最小でOK）
  - id: str | None（無ければ SHA-256 の hash(text) を使う）

ドキュメント（Must）

- Agents SDK と一緒に使う最小例（tracing 設定 → Agent 作成 → run → SQLite 検索）
- metadata キーの標準（上記の固定キー）
