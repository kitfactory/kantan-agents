kantan-agents ツール提供ガイド（kantan-agents-tools たたき台）

目的

- 外部パッケージ（例: kantan-agents-tools）から tool と tool_rules 設定を配布するための最小ルールを揃える。
- 利用側（kantan-agents）の `entry-point` 自動収集と、`tool_rules.params` の検証に“寄せる”ための共通言語を作る。

前提

- kantan-agents は `project.entry-points."kantan_agents.tools"` から provider を自動収集する。
- provider は `list_tools()` と `get_tool_rules()` を実装する。
- tool 呼び出し時の入力は JSON オブジェクト（dict 相当）であることを前提にし、検証に失敗するとエラーになる。

1. Tool 名のルール（重要）

推奨

- tool 名は安定した文字列にする（関数名に依存しない）。
- 衝突を避けるため、名前空間を付ける（例: `kantan.search_docs` / `myorg.ticket.create`）。

注意

- 同名 tool が複数ある場合、後勝ちで上書きされる（provider より `Agent(tools=[...])` 側を優先するのが安全）。

2. Provider I/F（固定）

最低限

```python
from typing import Any

class ToolProvider:
    def list_tools(self) -> list[Any]:
        ...

    def get_tool_rules(self) -> dict[str, Any] | None:
        ...
```

- `list_tools()` は tool の配列を返す。
  - `agents.FunctionTool` そのもの、または callable（関数）でもよい。
  - callable の場合、kantan-agents 側で `agents.function_tool()` により tool 化される。
- `get_tool_rules()` は tool_rules 設定の dict を返す（未提供なら `None`）。

3. entry-point 登録（pyproject.toml）

```toml
[project.entry-points."kantan_agents.tools"]
kantan_agents_tools = "kantan_agents_tools.provider:KantanToolProvider"
```

4. 推奨設定の取得と統合

kantan-agents は Agent 初期化時に entry-point provider を読み込み、`list_tools()` と `get_tool_rules()` の結果を統合する。

統合順序

- 基本 tool_rules 設定（`ToolRulesMode.RECOMMENDED` 相当）
- provider 由来 tool_rules 設定（`get_tool_rules()`）
- 明示 tool_rules 設定（`context["tool_rules"]` または `get_context_with_tool_rules(...)` で渡した dict）

統合ルール

- `allow`/`deny` は union。どちらかに `"*"` があれば `"*"`。
- tool 判定では `deny` が常に優先。
- `params` は tool 名ごとに dict を merge。同名キーは上書き。

利用側の最小例

```python
from kantan_agents import Agent, ToolRulesMode, get_context_with_tool_rules

agent = Agent(name="provider-agent", instructions="Use tools when needed.")

context = get_context_with_tool_rules(ToolRulesMode.RECOMMENDED)
context["tool_rules"]["allow"] = ["myorg.search"]
context["tool_rules"]["params"] = {
    "myorg.search": {"query": {"type": "string", "minLength": 1, "maxLength": 200}}
}

context = agent.run("Find docs about tracing.", context)
print(context["result"].final_output)
```

確認用ヘルパ

- `list_provider_tools()` で provider 由来の tool 名一覧を取得できる。
- `get_provider_tool_rules()` で provider 由来の tool_rules 設定を取得できる。

5. tool_rules 仕様（allow/deny/params）

形

```python
tool_rules = {
    "allow": ["tool.name.a", "tool.name.b"] | "*" | None,
    "deny": ["tool.name.x"] | "*" | None,
    "params": {
        "tool.name.a": {
            "param": {"type": "string", "maxLength": 200},
        },
    },
}
```

- `deny` は常に優先される（allow に含まれていても deny なら不可）。
- `params` は tool 名ごとに、引数名→ルールの dict を持つ。
- 利用可能なルール（最小サブセット）
  - `type` / `enum` / `minLength` / `maxLength` / `pattern` / `minimum` / `maximum`

制約（現時点）

- `params` の検証は “トップレベルの引数” にのみ適用する（ネストした object の内部キーまでは検証しない）。
- tool 実装側でネストを扱いたい場合は、引数をフラットにする（例: `user_id`, `ticket_title`）か、tool 側で追加バリデーションする。

6. tool_rules.params のサンプル（tool 別）

6.1. 文字列長を制限する（検索）

```python
tool_rules = {
    "allow": ["kantan.search_docs"],
    "deny": [],
    "params": {
        "kantan.search_docs": {
            "query": {"type": "string", "minLength": 1, "maxLength": 200},
        }
    },
}
```

6.2. enum を使う（チケット作成）

```python
tool_rules = {
    "allow": ["myorg.ticket.create"],
    "deny": [],
    "params": {
        "myorg.ticket.create": {
            "priority": {"type": "string", "enum": ["low", "normal", "high"]},
        }
    },
}
```

6.3. 数値範囲を制限する（top_k）

```python
tool_rules = {
    "allow": ["kantan.search_docs"],
    "deny": [],
    "params": {
        "kantan.search_docs": {
            "top_k": {"type": "integer", "minimum": 1, "maximum": 10},
        }
    },
}
```

7. tool 実装テンプレ（name を固定する）

`agents.function_tool` は `name_override` を持つため、関数名に依存せず tool 名を固定できる。

```python
import agents

@agents.function_tool(name_override="kantan.search_docs")
def search_docs(query: str, top_k: int = 5) -> list[str]:
    return []
```

8. provider 実装テンプレ（まとめ）

```python
import agents

@agents.function_tool(name_override="kantan.search_docs")
def search_docs(query: str, top_k: int = 5) -> list[str]:
    return []


class KantanToolProvider:
    def list_tools(self):
        return [search_docs]

    def get_tool_rules(self):
        return {
            "allow": ["kantan.search_docs"],
            "deny": [],
            "params": {
                "kantan.search_docs": {
                    "query": {"type": "string", "minLength": 1, "maxLength": 200},
                    "top_k": {"type": "integer", "minimum": 1, "maximum": 10},
                }
            },
        }
```

9. 予約キーと衝突回避（context）

kantan-agents が扱う主要キー

- `tool_rules`: tool 制御
- `result`: Agents SDK の返値
- `history`: 入力/応答の履歴（有効時）

推奨ルール

- アプリ固有の値は `app_*` のようにプレフィクスを付ける（例: `app_user_id`）。
- `output_dest` は内容が分かるユニークなキー名にする（例: `summary_json`, `evaluation_rubric`）。

10. チェックリスト（provider 実装）

- `list_tools()` と `get_tool_rules()` を実装した
- tool 名が安定した文字列で、名前空間付きである
- `get_tool_rules()` が allow/deny/params を返す（未提供なら None を返す）
- entry-point `kantan_agents.tools` に登録した
- tool 入力が JSON オブジェクト前提で扱える設計にした

11. トラブルシュート（エラーIDの目安）

- E7: provider に `list_tools/get_tool_rules` が無い → I/F 実装を確認する
- E8: tool が許可されていない → `allow/deny` と tool 名の一致を確認する
- E10: tool 入力が JSON オブジェクトではない → tool 引数を dict で受け取れる形にする（モデル側の出力も含めて見直す）
