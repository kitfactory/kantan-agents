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
| F-06 | judge() ヘルパ | rubric structured output の自動保存 | kantan-llm | v0.2 |
| F-07 | 最小利用ドキュメント | tracing 設定 → Agent 作成 → run → SQLite 検索 | kantan-llm | v0.1 |
| F-08 | Handoff のサポート | Agent インスタンス間の handoff を利用可能にする | OpenAI Agents SDK | v0.1 |
| F-09 | RUBRIC schema 定数 | output_type=RUBRIC で rubric structured output を簡易化 | kantan-llm | v0.2 |

主要な仕様メモ

- Agent.run
  - シグネチャ: run(input: str, *, render_vars: dict|None=None, trace_metadata: dict|None=None) -> result
  - render_vars は rendering に必要な情報
  - trace_metadata は trace に記録する付与情報
- Trace metadata 自動注入（Prompt 指定時）
  - agent_name
  - prompt_name
  - prompt_version
  - prompt_id（Prompt が id を持てばそれ、なければ SHA-256 で hash(prompt.text)）
  - prompt_meta_*（Prompt.meta をフラットに展開、スカラーのみ）
  - agent_run_id（run ごとに一意）
  - trace_metadata に同名キーがある場合は自動注入値で上書きする
- instructions が str の場合は注入最小（任意）
  - agent_name と agent_run_id は入れる
  - prompt_name は agent 名から取る
  - prompt_id がない場合は SHA-256 のハッシュにする
- Prompt 型（kantan-lab 側で管理）
  - name: str
  - version: str
  - text: str
  - meta: Mapping[str, Any] | None（最小でOK）
  - id: str | None（無ければ SHA-256 の hash(text) を使う）

ドキュメント（Must）

- Agents SDK と一緒に使う最小例（tracing 設定 → Agent 作成 → run → SQLite 検索）
- metadata キーの標準（上記の固定キー）
