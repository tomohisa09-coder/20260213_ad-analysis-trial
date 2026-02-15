# 作業計画書：Streamlit 広告クリエイティブ分析アプリ

## 概要
- **依頼内容**：Gemini手動JSON + Excel → Streamlit → Claude API（Sonnet）→ レポート自動生成 のWebアプリを構築
- **作業範囲**：依存ライブラリ導入 → 既存スクリプト関数化 → Streamlit UI → Claude API連携 → テスト
- **成果物**：`app/` ディレクトリ配下にStreamlitアプリ一式
- **テストデータ**：`data/raw/` の既存データ（CORE STEP 4クリエイティブ分）

## アーキテクチャ

```
app/
├── app.py              # Streamlitメイン（UIとフロー制御）
├── analysis_engine.py  # データ前処理・集計・グラフ生成（01-03を関数化）
├── claude_client.py    # Claude API呼び出し + プロンプトテンプレート
└── prompts/
    └── analysis_prompt.md  # Claude用プロンプトテンプレート
```

## ユーザーフロー（画面遷移）

```
Step 1: アップロード
  ├─ Excel/CSV（Meta広告パフォーマンスデータ）
  ├─ JSON（Geminiで生成したクリエイティブ構造）× 動画数分
  └─ [任意] 広告名とJSON video_idの紐付け

Step 2: データ確認
  ├─ アップロードデータのプレビュー表示
  ├─ クリエイティブ対応表の確認・修正
  └─ 「分析開始」ボタン

Step 3: 定量分析（自動・即時）
  ├─ KPIサマリーテーブル表示
  ├─ グラフ群をStreamlit内に描画
  └─ 視聴維持率カーブ表示

Step 4: AI分析（Claude API）
  ├─ スピナー表示中にClaude Sonnetが分析
  ├─ クロス分析・勝因敗因・改善提案を生成
  └─ レポートをMarkdownで表示

Step 5: エクスポート
  ├─ レポート全文ダウンロード（Markdown）
  └─ Notion用HTMLダウンロード（base64画像埋め込み）
```

## 作業計画（To-Do List）

### Phase 1: 環境構築
- [ ] streamlit, anthropic パッケージのインストール
- [ ] `.env` にClaude API Keyを設定（.gitignoreに追加）
- [ ] `app/` ディレクトリ構造の作成

### Phase 2: 既存スクリプトの関数化（analysis_engine.py）
- [ ] 01_data_preprocessing → `process_excel()`, `parse_creative_json()`, `build_summary()` に分解
- [ ] 02_performance_analysis → `generate_kpi_chart()`, `generate_trend_chart()`, `generate_retention_chart()` に分解
- [ ] 03_cross_analysis → `generate_cross_charts()`, `generate_scorecard()` に分解
- [ ] ファイルパス依存を排除し、DataFrameの入出力で完結させる

### Phase 3: Claude API連携（claude_client.py）
- [ ] Anthropic Python SDK を使ったAPI呼び出し関数
- [ ] プロンプトテンプレート作成（KPIサマリー + JSON構造を渡す）
- [ ] レスポンスのMarkdownパース

### Phase 4: Streamlit UI（app.py）
- [ ] Step 1: ファイルアップロードUI（Excel + JSON）
- [ ] Step 2: データプレビュー＋対応表確認
- [ ] Step 3: 定量分析の自動実行＋グラフ表示
- [ ] Step 4: Claude API分析実行＋レポート表示
- [ ] Step 5: エクスポート機能（MD + HTML）

### Phase 5: テスト・動作確認
- [ ] 既存データ（CORE STEP 4本）でE2Eテスト
- [ ] エラーハンドリング（ファイル形式不正、API失敗時）

## 確認・検証項目
- [ ] Claude APIキーが.gitignoreに含まれている
- [ ] 既存データで前回と同等品質のレポートが出力される
- [ ] Streamlitがローカルで正常起動する

## リスク・注意事項
- **APIキーの管理**: `.env` ファイルは絶対にGitHubにプッシュしない
- **JSONスキーマの柔軟性**: Geminiの出力が微妙に揺れる可能性 → バリデーション追加
- **コスト**: Sonnet 4.5で1回あたり約¥50-100（月30回でも¥3,000以内）

## ファイル配置計画
- アプリ本体：`app/`
- プロンプト：`app/prompts/`
- 環境設定：`.env`（.gitignore対象）

---
**この計画でよろしいですか？**
