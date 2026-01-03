kantan-agents アーキテクチャ（v0.1）

レイヤー構造と依存方向

- Presentation/API 層
  - 公開 API: Agent, Prompt, tracing API 再エクスポート, judge()（内部補助）
- Application/Domain 層
  - Trace メタデータ標準化ルール
  - Prompt/Agent の入力バリデーション
  - Context/Policy の統合ルール
- Infrastructure 層
  - OpenAI Agents SDK
  - kantan-llm（get_llm / Trace）
  - kantan-lab（分析対象としての依存）
  - importlib.metadata（entry-point 収集）

依存方向: Presentation/API → Application/Domain → Infrastructure

主要インターフェース（I/F）

- Agent
  - __init__(name: str, instructions: str | Prompt, *, tools: list | None = None, renderer: Callable | None = None, metadata: dict | None = None, output_type: type | None = None, handoffs: list | None = None, allow_env: bool = False, history: int = 50, output_dest: str | None = None)
  - run(input: str, context: dict | None = None) -> dict
  - run_async(input: str, context: dict | None = None) -> dict
- Context
  - policy: dict | None
  - result: Any | None
- PolicyMode
  - ALLOW_ALL
  - DENY_ALL
  - RECOMMENDED
- ToolProvider
  - list_tools() -> list
  - get_policy() -> dict
- get_context_with_policy
  - get_context_with_policy(mode_or_policy: PolicyMode | dict) -> dict
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
- entry-point 収集
  - group: project.entry-points."kantan_agents.tools"

Agent クラス I/F（メソッド別の引数説明）

__init__(name: str, instructions: str | Prompt, *, tools: list | None = None, renderer: Callable | None = None, metadata: dict | None = None, output_type: type | None = None, handoffs: list | None = None, allow_env: bool = False, history: int = 50, output_dest: str | None = None)

| 引数 | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| name | str | yes | Agent 名。Trace の agent_name に利用する。 |
| instructions | str \| Prompt | yes | 指示文または Prompt。Prompt の場合は標準メタデータを自動注入する。 |
| tools | list \| None | no | Agents SDK の tools。None の場合は未指定。 |
| renderer | Callable \| None | no | instructions をレンダリングする関数。None の場合はデフォルト。 |
| metadata | dict \| None | no | Agent に紐づく固定の付与情報。Trace へ付与する。 |
| output_type | type \| None | no | structured output 用の出力型。Agents SDK の output_type に渡す。 |
| handoffs | list \| None | no | handoff 可能な Agent インスタンスの一覧。Agents SDK の handoffs に渡す。 |
| allow_env | bool | no | true の場合に $env 参照を許可する。 |
| history | int | no | context に保存する履歴件数。0 の場合は保存しない。 |
| output_dest | str \| None | no | structured output を保存する context のキー名。 |

run(input: str, context: dict | None = None) -> dict

run_async(input: str, context: dict | None = None) -> dict

| 引数 | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| input | str | yes | Agent への入力。 |
| context | dict \| None | no | rendering/policy/result を保持する Context。None/空の dict の場合は補完する。 |

返値: context。

run_async も同じ引数で context を返す。

データ設計（最小）

- Context
  - policy
  - result
  - history
    - role
    - text
  - output_dest 指定時の出力キー
- Trace metadata 標準キー
  - agent_name
  - prompt_name
  - prompt_version
  - prompt_id
  - prompt_meta_*（スカラーのみ）
  - agent_run_id
- Policy
  - allow: list[str] | "*"
  - deny: list[str] | "*"
  - params: dict[str, dict]

責務の分離

- Agent は Agents SDK の利用を隠蔽せず、Trace のメタデータ整形に集中する。
- Prompt は kantan-lab 管理前提の最小モデルとし、管理機能は持たない。
- Trace への書き込み自体は kantan-llm に委譲し、Agent はメタデータの付与のみを担当する。
- 標準の renderer は {{ }} 形式で変数をレンダリングし、$ctx/$env を扱う。
- structured output / rubric は generation span として Trace に記録する。

ログ/エラー方針

- エラーは [kantan-agents][E#] 形式で返す。
- 例外メッセージは docs/spec.md のエラー一覧に一致させる。
