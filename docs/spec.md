kantan-agents 仕様（v0.1）

1. Agents SDK tracing API の再エクスポート（F-01）

1.1. add_trace_processor を呼び出したとき、Agents SDK と同一の例外/引数で処理する（F-01）

- Given: Agents SDK が利用可能である
- When: kantan-agents の add_trace_processor を呼び出す
- Then: Agents SDK の add_trace_processor と同等に振る舞い、例外/引数の扱いは同一である

1.2. set_trace_processors を呼び出したとき、Agents SDK と同一の例外/引数で処理する（F-01）

- Given: Agents SDK が利用可能である
- When: kantan-agents の set_trace_processors を呼び出す
- Then: Agents SDK の set_trace_processors と同等に振る舞い、例外/引数の扱いは同一である

2. Agent クラス（F-02/F-03/F-10/F-12/F-13）

2.1. Agent を生成したとき、instructions を必須として保持する（F-02）

- Given: name と instructions が指定される
- When: Agent を生成する
- Then: instructions は必須として保持され、指定が無い場合はエラーとする

2.2. Agent を生成したとき、tools/renderer/metadata/output_type/handoffs/allow_env/history/output_dest を任意で受け入れる（F-02/F-10/F-12/F-13）

- Given: tools と renderer と metadata と output_type と handoffs と allow_env と history と output_dest が任意で指定される
- When: Agent を生成する
- Then: tools は Agents SDK の tools に渡す
- And: renderer は任意として保持し、metadata は保持する
- And: output_type は Agents SDK の output_type に渡す
- And: handoffs は Agents SDK の handoffs に渡す
- And: allow_env はテンプレートで $env を利用できるかどうかを制御する
- And: history は context に保存する履歴件数を制御する
- And: output_dest は structured output を格納する context のキー名を制御する

2.3. Prompt を指定して run したとき、Trace に標準メタデータを自動注入する（F-03/F-05）

- Given: instructions が Prompt である
- When: Agent.run を呼び出す
- Then: Trace metadata に標準キーを自動注入する

2.4. instructions が str の場合に run したとき、最小の標準メタデータを注入する（F-03/F-05）

- Given: instructions が str である
- When: Agent.run を呼び出す
- Then: agent_name と agent_run_id を注入する
- And: prompt_name は agent 名から取得する
- And: prompt_id は無指定の場合にハッシュ値を使う

2.5. context を指定して run したとき、レンダリングと tool_rules と結果格納に用いる（F-10）

- Given: context が指定される
- When: Agent.run を呼び出す
- Then: context はレンダリング変数と tool_rules の参照に使用される
- And: context.result に Agents SDK の返値を格納する

2.6. context が None または空の dict の場合、context を補完する（F-10）

- Given: context が None または空の dict である
- When: Agent.run を呼び出す
- Then: Agent 内で tool_rules と result を補完して利用する

2.7. Agent.run の返値は context とする（F-10）

- Given: context を使用して Agent.run を呼び出す
- When: Agent.run が完了する
- Then: context を返す

2.8. Prompt.meta を展開するとき、スカラー値のみを採用する（F-03/F-05）

- Given: Prompt.meta に複数型の値が含まれる
- When: Trace metadata へ prompt_meta_* を展開する
- Then: 文字列/数値（int/float）/真偽値のみを採用し、その他は無視する

2.9. run_async を呼び出したとき、run と同等の context を返す（F-10）

- Given: context を使用して Agent.run_async を呼び出す
- When: Agent.run_async が完了する
- Then: run と同様に context を返す

3. Prompt 型（kantan-lab 管理）（F-04）

3.1. Prompt.id が存在する場合、その値を prompt_id に用いる（F-04）

- Given: Prompt.id が存在する
- When: Trace metadata へ prompt_id を注入する
- Then: Prompt.id を使用する

3.2. Prompt.id が無い場合、text を安定ハッシュして prompt_id に用いる（F-04）

- Given: Prompt.id が None である
- When: Trace metadata へ prompt_id を注入する
- Then: text を UTF-8 で SHA-256 した 16 進文字列を使用する

4. Trace メタデータ標準キー（F-05）

4.1. Prompt を instruction として指定して run したとき、標準キーを付与する（F-05）

- Given: instructions が Prompt である
- When: Agent.run を呼び出す
- Then: 次のキーを Trace metadata に付与する
  - agent_name
  - prompt_name
  - prompt_version
  - prompt_id
  - prompt_meta_*（Prompt.meta をフラット展開）
  - agent_run_id

4.2. instructions が str の場合、最小の標準キーを付与する（F-05）

- Given: instructions が str である
- When: Agent.run を呼び出す
- Then: agent_name と agent_run_id を付与する

5. judge() ヘルパ（F-06）

5.1. rubric の structured output を行ったとき、kantan-llm 側で自動保存される（F-06）

- Given: output_kind="judge" に対応する rubric の structured output を行う
- When: Agent.run が完了する
- Then: kantan-llm の規約に従って Trace へ自動保存される（保存先キーは kantan-llm の仕様に準拠）

5.2. output_type=RUBRIC を指定できる（F-06）

- Given: rubric の structured output を出したい
- When: Agent の output_type に RUBRIC を指定する
- Then: rubric の schema を使用した structured output が可能になる

5.3. Agent の最終出力を Trace に反映する（F-06）

- Given: structured output または rubric を返す
- When: Agent.run が完了する
- Then: 最終出力を generation span として Trace に記録する

補足: judge() は内部補助であり、ユーザー向けの基本ルートは output_type=RUBRIC を使う。

6. ドキュメント（F-07）

6.1. 最小利用例を提供する（F-07）

- Given: kantan-llm を利用する
- When: ドキュメントを参照する
- Then: tracing 設定 → Agent 作成 → run → SQLite 検索の例が含まれる

6.2. metadata キーの標準を明記する（F-07）

- Given: Trace を分析したい
- When: ドキュメントを参照する
- Then: 標準メタデータキー一覧が明記されている

8. Context/ToolRules（F-10）

8.1. テンプレートで $ctx と $env を利用できる（F-10）

- Given: instructions のレンダリングが行われる
- When: テンプレート内で $ctx.xxx を参照する
- Then: context に含まれる値を参照する
- And: 未定義参照は空文字として扱う
- And: allow_env が True の場合に限り $env.ENV_NAME を参照できる

8.2. tool_rules は allow/deny/params で構成する（F-10）

- Given: context.tool_rules が指定される
- When: tool_rules を参照する
- Then: tool_rules は allow/deny/params の 3 要素で構成する
- And: allow/deny は "*" を指定できる
- And: allow/deny が競合する場合は deny を優先する

8.3. tool_rules.params は JSON Schema 互換の最小サブセットを用いる（F-10）

- Given: tool_rules.params を指定する
- When: tool パラメータの検証に利用する
- Then: type/enum/minLength/maxLength/pattern/minimum/maximum を利用できる

8.4. get_context_with_tool_rules は定数値またはカスタム tool_rules を受け付ける（F-10）

- Given: ToolRulesMode（ALLOW_ALL/DENY_ALL/RECOMMENDED）または tool_rules dict を渡す
- When: get_context_with_tool_rules を呼び出す
- Then: tool_rules を含む context を返す

9. ToolRules 収集（F-11）

9.1. entry-point から tool/tool_rules を収集する（F-11）

- Given: project.entry-points."kantan_agents.tools" が定義される
- When: Agent が tool/tool_rules を収集する
- Then: entry-point から provider を取得して tool/tool_rules を収集する

9.2. tool 由来の tool_rules 設定と明示 tool_rules 設定を統合する（F-11）

- Given: tool 由来の tool_rules 設定と明示 tool_rules 設定が存在する
- When: tool_rules 設定を統合する
- Then: 明示 tool_rules 設定を優先する
- And: allow/deny は union で統合する
- And: params は tool 名ごとに merge する

9.3. 基本 tool_rules 設定と tool 由来 tool_rules 設定を統合する（F-11）

- Given: 基本 tool_rules 設定と tool 由来 tool_rules 設定が存在する
- When: tool_rules 設定を統合する
- Then: tool 由来 tool_rules 設定を優先する

9.4. provider は tool と tool_rules を取得できる I/F を提供する（F-11）

- Given: entry-point から provider を取得する
- When: tool/tool_rules を収集する
- Then: provider は list_tools と get_tool_rules を提供する

9.5. list_provider_tools は provider 由来の tool 名を返す（F-11）

- Given: entry-point provider から tool が取得できる
- When: list_provider_tools を呼び出す
- Then: provider 由来の tool 名一覧を返す

9.6. get_provider_tool_rules は provider 由来の tool_rules 設定を返す（F-11）

- Given: entry-point provider から tool_rules 設定が取得できる
- When: get_provider_tool_rules を呼び出す
- Then: provider 由来の tool_rules 設定（allow/deny/params）を返す

9.7. get_effective_tool_rules は provider 由来と明示 tool_rules 設定を統合する（F-11）

- Given: provider 由来の tool_rules 設定と明示 tool_rules 設定が存在する
- When: get_effective_tool_rules を呼び出す
- Then: provider 由来の tool_rules 設定に明示 tool_rules 設定を統合した結果を返す
- And: tool_rules 引数が context.tool_rules より優先される

10. History（F-12）

10.1. history を指定して run したとき、入力/応答を context.history に保存する（F-12）

- Given: history が 1 以上である
- When: Agent.run を呼び出す
- Then: context.history に user/assistant の入力と応答を追加する
- And: context.history は dict の配列で role/text を持つ

10.2. history 上限を超えたとき、古い履歴から削除する（F-12）

- Given: context.history が上限を超える
- When: Agent.run が完了する
- Then: 古い履歴から削除して上限以内に保つ
- And: 上限は context.history の要素数で判断する

10.3. history が 0 の場合、履歴を保存しない（F-12）

- Given: history が 0 である
- When: Agent.run を呼び出す
- Then: context.history を更新しない

11. output_dest（F-13）

11.1. output_dest を指定した場合、structured output を context に保存する（F-13）

- Given: output_dest が指定され、structured output が dict として取得できる
- When: Agent.run が完了する
- Then: context[output_dest] に structured output を保存する
- And: context[output_dest] が存在する場合は上書きする

入力バリデーション

7.1. Agent 生成時に instructions が未指定の場合はエラーとする（F-02）

- Given: instructions が None または未指定
- When: Agent を生成する
- Then: エラー E1 を返す

7.2. Prompt.text が空文字の場合はエラーとする（F-04）

- Given: Prompt.text が空文字
- When: Prompt を生成する
- Then: エラー E2 を返す

7.3. Prompt.name または Prompt.version が空文字の場合はエラーとする（F-04）

- Given: Prompt.name または Prompt.version が空文字
- When: Prompt を生成する
- Then: エラー E3 を返す

7.4. context.tool_rules が dict 以外の場合はエラーとする（F-10）

- Given: context.tool_rules が dict 以外である
- When: Agent.run を呼び出す
- Then: エラー E18 を返す

エラー/メッセージ一覧

| Error ID | メッセージ |
| --- | --- |
| E1 | [kantan-agents][E1] instructions is required |
| E2 | [kantan-agents][E2] Prompt.text must not be empty |
| E3 | [kantan-agents][E3] Prompt.name and Prompt.version must not be empty |
| E4 | [kantan-agents][E4] Tool must define name |
| E5 | [kantan-agents][E5] Context must be a dict |
| E6 | [kantan-agents][E6] Context history must be a list |
| E7 | [kantan-agents][E7] Tool provider must implement list_tools and get_tool_rules |
| E8 | [kantan-agents][E8] Tool is not allowed: {tool_name} |
| E9 | [kantan-agents][E9] Unknown ToolRulesMode: {mode} |
| E10 | [kantan-agents][E10] Tool input must be a JSON object |
| E11 | [kantan-agents][E11] Tool parameter type mismatch: {tool_name}.{param_name} |
| E12 | [kantan-agents][E12] Tool parameter enum mismatch: {tool_name}.{param_name} |
| E13 | [kantan-agents][E13] Tool parameter minLength mismatch: {tool_name}.{param_name} |
| E14 | [kantan-agents][E14] Tool parameter maxLength mismatch: {tool_name}.{param_name} |
| E15 | [kantan-agents][E15] Tool parameter pattern mismatch: {tool_name}.{param_name} |
| E16 | [kantan-agents][E16] Tool parameter minimum mismatch: {tool_name}.{param_name} |
| E17 | [kantan-agents][E17] Tool parameter maximum mismatch: {tool_name}.{param_name} |
| E18 | [kantan-agents][E18] Tool rules must be a dict |
