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

2. Agent クラス（F-02/F-03）

2.1. Agent を生成したとき、instructions を必須として保持する（F-02）

- Given: name と instructions が指定される
- When: Agent を生成する
- Then: instructions は必須として保持され、指定が無い場合はエラーとする

2.2. Agent を生成したとき、renderer/metadata/output_type/handoffs を任意で受け入れる（F-02）

- Given: renderer と metadata と output_type と handoffs が任意で指定される
- When: Agent を生成する
- Then: renderer は任意として保持し、metadata は保持する
- And: output_type は Agents SDK の output_type に渡す
- And: handoffs は Agents SDK の handoffs に渡す

2.3. Prompt を指定して run したとき、Trace に標準メタデータを自動注入する（F-03/F-05）

- Given: instructions が Prompt である
- When: Agent.run を呼び出す
- Then: Trace metadata に標準キーを自動注入する
- And: trace_metadata に同名キーがある場合は自動注入値で上書きする

2.4. instructions が str の場合に run したとき、最小の標準メタデータを注入する（F-03/F-05）

- Given: instructions が str である
- When: Agent.run を呼び出す
- Then: agent_name と agent_run_id を注入する
- And: prompt_name は agent 名から取得する
- And: prompt_id は無指定の場合にハッシュ値を使う

2.5. render_vars と trace_metadata を受け取ったとき、それぞれの用途で扱う（F-03）

- Given: render_vars と trace_metadata が指定される
- When: Agent.run を呼び出す
- Then: render_vars はレンダリングにのみ使用される
- And: trace_metadata は Trace に記録する付与情報として扱う

2.7. Agent.run の返値は Agents SDK と同一とする（F-03）

- Given: Agents SDK が利用可能である
- When: Agent.run を呼び出す
- Then: Agents SDK の run と同じ返値を返す

2.6. Prompt.meta を展開するとき、スカラー値のみを採用する（F-03/F-05）

- Given: Prompt.meta に複数型の値が含まれる
- When: Trace metadata へ prompt_meta_* を展開する
- Then: 文字列/数値（int/float）/真偽値のみを採用し、その他は無視する

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

6. ドキュメント（F-07）

6.1. 最小利用例を提供する（F-07）

- Given: kantan-llm を利用する
- When: ドキュメントを参照する
- Then: tracing 設定 → Agent 作成 → run → SQLite 検索の例が含まれる

6.2. metadata キーの標準を明記する（F-07）

- Given: Trace を分析したい
- When: ドキュメントを参照する
- Then: 標準メタデータキー一覧が明記されている

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

エラー/メッセージ一覧

| Error ID | メッセージ |
| --- | --- |
| E1 | [kantan-agents][E1] instructions is required |
| E2 | [kantan-agents][E2] Prompt.text must not be empty |
| E3 | [kantan-agents][E3] Prompt.name and Prompt.version must not be empty |
