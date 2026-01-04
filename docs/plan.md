kantan-agents 作業計画（v0.1）

- [x] 要件定義を確認し、機能表の Spec ID に合意する
- [x] F-01: tracing API 再エクスポートを実装する（add_trace_processor / set_trace_processors）
- [x] F-01: 再エクスポートのテストを実行する
- [x] F-04: Prompt 型を実装する（name/version/text/meta/id）
- [x] F-04: Prompt 入力バリデーションのテストを実行する
- [x] F-02: Agent コンストラクタを実装する（output_type/handoffs/renderer/metadata 含む）
- [x] F-02: Agent 初期化のテストを実行する
- [x] F-03/F-05: Agent.run の Trace メタデータ自動注入を実装する
- [x] F-03/F-05: Trace メタデータ注入のテストを実行する
- [x] F-08: handoffs を Agents SDK に受け渡す実装を確認する
- [x] F-08: handoffs のテストを実行する
- [x] F-06: judge() ヘルパの入出力連携を実装する
- [x] F-06: rubric structured output の記録テストを実行する（gpt-5.1-mini の利用可否に依存）
- [x] F-09: RUBRIC schema 定数を実装する
- [x] F-07: 最小利用ドキュメントを作成する（tracing 設定 → Agent 作成 → run → SQLite 検索）
- [x] F-10: Context/ToolRules の仕様更新（run/テンプレート/ToolRulesMode）
- [x] F-10: Context/ToolRules の設計反映（Agent/renderer/get_context_with_tool_rules）
- [x] F-10: Context/ToolRules のテストを実行する
- [x] F-11: entry-point による tool/tool_rules 収集仕様を更新する
- [x] F-11: tool/tool_rules 収集の実装と統合ルールを確認する
- [x] F-11: tool/tool_rules 収集のテストを実行する
- [x] F-10/F-11: usage/tutorial を Context/ToolRules に合わせて更新する
- [x] F-12: history 機能の仕様更新（context/history/テンプレート）
- [x] F-12: history 機能の設計反映（Agent/history）
- [x] F-12: history のテストを実行する
- [x] F-13: output_dest の仕様更新（context/output）
- [x] F-13: output_dest の設計反映（Agent/output_dest）
- [x] F-13: output_dest のテストを実行する

<details>
<summary>補足</summary>

テスト方針メモ

- モックは補助。可能な範囲で実経路のテストを通す。
- テストが難航したらステップごとにデバッグメッセージを追加する。
- function calling / structured output / rubric が予定通り Trace に記録されることを確認する。

環境変数

- OPENAI_API_KEY: テスト時に使用（OpenAI API Key）
- テストでは gpt-5-mini を使用する。

チュートリアル（段階的）

- [x] 実装完成後、実装に合わせたチュートリアルを作成する
- [x] 単元を段階的に分け、各単元を「利用ケース → 実現方法 → ソースコード」で構成する
- [x] 最終単元はツールを使ったエージェントで評価（rubric）とプロンプト分析の事例にする
</details>
