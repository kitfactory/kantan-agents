kantan-agents チュートリアル 単元9（v0.1）

タイトル

entry-point でツールを追加する

概要

この単元では外部パッケージからツールと policy を提供する方法を説明する。entry-point に登録しておけば、利用者は追加設定なしでツールを利用できる。独自ツール配布が不要なら後回しでよい。

ステップ

- project.entry-points に provider を登録する。
- list_tools と get_policy を実装する。
- パッケージをインストールして自動登録させる。

実現方法

- group 名は "kantan_agents.tools" を使う。
- tool には安定した name を持たせる。
- 詳細なガイドは `docs/tool_provider_guide.md` を参照する。

ソースコード
```toml
[project.entry-points."kantan_agents.tools"]
my_tools = "my_package.tools:MyToolProvider"
```

```python
class MyToolProvider:
    def list_tools(self):
        return [my_tool_function]

    def get_policy(self):
        return {
            "allow": ["my_tool_function"],
            "deny": [],
            "params": {"my_tool_function": {"text": {"type": "string", "maxLength": 200}}},
        }
```
