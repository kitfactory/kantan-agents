kantan-agents アーキテクチャ（v0.1）

レイヤー構造と依存方向

- Presentation/API 層
  - 公開 API: Agent, Prompt, tracing API 再エクスポート, judge()
- Application/Domain 層
  - Trace メタデータ標準化ルール
  - Prompt/Agent の入力バリデーション
- Infrastructure 層
  - OpenAI Agents SDK
  - kantan-llm（get_llm / Trace）
  - kantan-lab（分析対象としての依存）

依存方向: Presentation/API → Application/Domain → Infrastructure

主要インターフェース（I/F）

- Agent
  - __init__(name: str, instructions: str | Prompt, *, tools: list | None = None, renderer: Callable | None = None, metadata: dict | None = None, output_type: type | None = None, handoffs: list | None = None)
  - run(input: str, *, render_vars: dict | None = None, trace_metadata: dict | None = None) -> Any
- Prompt
  - name: str
  - version: str
  - text: str
  - meta: Mapping[str, Any] | None
  - id: str | None
- RUBRIC
  - rubric structured output の schema 定数
- tracing API 再エクスポート
  - add_trace_processor(processor: Callable) -> None
  - set_trace_processors(processors: list[Callable]) -> None

Agent クラス I/F（メソッド別の引数説明）

__init__(name: str, instructions: str | Prompt, *, tools: list | None = None, renderer: Callable | None = None, metadata: dict | None = None, output_type: type | None = None, handoffs: list | None = None)

| 引数 | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| name | str | yes | Agent 名。Trace の agent_name に利用する。 |
| instructions | str \| Prompt | yes | 指示文または Prompt。Prompt の場合は標準メタデータを自動注入する。 |
| tools | list \| None | no | Agents SDK の tools。None の場合は未指定。 |
| renderer | Callable \| None | no | instructions をレンダリングする関数。None の場合はデフォルト。 |
| metadata | dict \| None | no | Agent に紐づく固定の付与情報。Trace へ付与する。 |
| output_type | type \| None | no | structured output 用の出力型。Agents SDK の output_type に渡す。 |
| handoffs | list \| None | no | handoff 可能な Agent インスタンスの一覧。Agents SDK の handoffs に渡す。 |

run(input: str, *, render_vars: dict | None = None, trace_metadata: dict | None = None) -> Any

| 引数 | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| input | str | yes | Agent への入力。 |
| render_vars | dict \| None | no | rendering に必要な情報。 |
| trace_metadata | dict \| None | no | Trace に記録する付与情報。自動注入キーと衝突する場合は自動注入が優先。 |

返値: Agents SDK の run と同じ返値。

データ設計（最小）

- Trace metadata 標準キー
  - agent_name
  - prompt_name
  - prompt_version
  - prompt_id
  - prompt_meta_*（スカラーのみ）
  - agent_run_id

責務の分離

- Agent は Agents SDK の利用を隠蔽せず、Trace のメタデータ整形に集中する。
- Prompt は kantan-lab 管理前提の最小モデルとし、管理機能は持たない。
- Trace への書き込み自体は kantan-llm に委譲し、Agent はメタデータの付与のみを担当する。
- 標準の renderer は {{ }} 形式で変数をレンダリングする。

ログ/エラー方針

- エラーは [kantan-agents][E#] 形式で返す。
- 例外メッセージは docs/spec.md のエラー一覧に一致させる。
