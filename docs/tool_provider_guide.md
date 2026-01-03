kantan-agents ツール提供ガイド（kantan-agents-tools たたき台）

目的

- 外部パッケージ（例: kantan-agents-tools）から tool と policy を配布するための最小ルールを揃える。
- 利用側（kantan-agents）の `entry-point` 自動収集と、`policy.params` の検証に“寄せる”ための共通言語を作る。

前提

- kantan-agents は `project.entry-points."kantan_agents.tools"` から provider を自動収集する。
- provider は `list_tools()` と `get_policy()` を実装する。
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

    def get_policy(self) -> dict[str, Any] | None:
        ...
```

- `list_tools()` は tool の配列を返す。
  - `agents.FunctionTool` そのもの、または callable（関数）でもよい。
  - callable の場合、kantan-agents 側で `agents.function_tool()` により tool 化される。
- `get_policy()` は policy dict を返す（未提供なら `None`）。

3. entry-point 登録（pyproject.toml）

```toml
[project.entry-points."kantan_agents.tools"]
kantan_agents_tools = "kantan_agents_tools.provider:KantanToolProvider"
```

4. policy 仕様（allow/deny/params）

形

```python
policy = {
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

5. policy.params のサンプル（tool 別）

5.1. 文字列長を制限する（検索）

```python
policy = {
    "allow": ["kantan.search_docs"],
    "deny": [],
    "params": {
        "kantan.search_docs": {
            "query": {"type": "string", "minLength": 1, "maxLength": 200},
        }
    },
}
```

5.2. enum を使う（チケット作成）

```python
policy = {
    "allow": ["myorg.ticket.create"],
    "deny": [],
    "params": {
        "myorg.ticket.create": {
            "priority": {"type": "string", "enum": ["low", "normal", "high"]},
        }
    },
}
```

5.3. 数値範囲を制限する（top_k）

```python
policy = {
    "allow": ["kantan.search_docs"],
    "deny": [],
    "params": {
        "kantan.search_docs": {
            "top_k": {"type": "integer", "minimum": 1, "maximum": 10},
        }
    },
}
```

6. tool 実装テンプレ（name を固定する）

`agents.function_tool` は `name_override` を持つため、関数名に依存せず tool 名を固定できる。

```python
import agents

@agents.function_tool(name_override="kantan.search_docs")
def search_docs(query: str, top_k: int = 5) -> list[str]:
    return []
```

7. provider 実装テンプレ（まとめ）

```python
import agents

@agents.function_tool(name_override="kantan.search_docs")
def search_docs(query: str, top_k: int = 5) -> list[str]:
    return []


class KantanToolProvider:
    def list_tools(self):
        return [search_docs]

    def get_policy(self):
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

8. 予約キーと衝突回避（context）

kantan-agents が扱う主要キー

- `policy`: tool 制御
- `result`: Agents SDK の返値
- `history`: 入力/応答の履歴（有効時）

推奨ルール

- アプリ固有の値は `app_*` のようにプレフィクスを付ける（例: `app_user_id`）。
- `output_dest` は内容が分かるユニークなキー名にする（例: `summary_json`, `evaluation_rubric`）。

9. トラブルシュート（エラーIDの目安）

- E7: provider に `list_tools/get_policy` が無い → I/F 実装を確認する
- E8: tool が許可されていない → `allow/deny` と tool 名の一致を確認する
- E10: tool 入力が JSON オブジェクトではない → tool 引数を dict で受け取れる形にする（モデル側の出力も含めて見直す）

