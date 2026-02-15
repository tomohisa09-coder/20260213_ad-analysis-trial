# 🎯 作業計画書：MDファイル対応 & UI改善

## 📝 概要
- **依頼内容**：クリエイティブ分析のMDファイル読み込み対応 + ドラッグ＆ドロップUI改善
- **作業範囲**：`app/app.py` と `app/analysis_engine.py` の修正
- **成果物**：MDファイル（JSON+定性情報）を読み込み、Claude APIに両方渡せるアプリ

## 📋 作業計画（To-Do List）

### Phase 1: MDファイルパーサー追加
- [ ] `analysis_engine.py` に `parse_creative_md()` 関数を追加
  - MDファイルからJSONブロックを抽出（`{` で始まり `}` で終わるブロック）
  - JSONブロック以外の定性テキスト（分析レポート、Expert Insights等）も抽出
  - 各クリエイティブごとに `{json_data, qualitative_text}` をまとめる

### Phase 2: アップロードUI修正
- [ ] `app.py` のクリエイティブアップロード欄の対応形式に `md` を追加
  - JSON / MD 両方アップロード可能に
  - MDの場合は1ファイルに複数クリエイティブ含まれるので自動分割
- [ ] 定性テキストもClaude APIに渡すよう `claude_client.py` / プロンプトを修正
- [ ] ドラッグ＆ドロップの見た目を改善（説明テキストをわかりやすく）

### Phase 3: テスト & デプロイ
- [ ] ローカルで既存MDファイルを使ってテスト
- [ ] コミット・プッシュ（Streamlit Cloudに自動反映）

## 📁 ファイル配置計画
- 修正ファイル：`app/app.py`, `app/analysis_engine.py`, `app/claude_client.py`, `app/prompts/analysis_prompt.md`
- 新規作成：なし

---
**この計画でよろしいですか？**
