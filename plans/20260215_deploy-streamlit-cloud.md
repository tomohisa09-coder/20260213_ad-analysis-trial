# 🎯 作業計画書：Streamlit Community Cloud デプロイ

## 📝 概要
- **依頼内容**：社内メンバーが使えるようアプリをデプロイ。APIキー・モデル選択は非表示にし、パスワード認証を追加
- **作業範囲**：アプリのUI簡素化 → デプロイ設定 → Streamlit Community Cloudへデプロイ
- **成果物**：社内メンバーがURLアクセスで使えるWebアプリ

## 📋 作業計画（To-Do List）

### Phase 1: アプリUI修正
- [x] サイドバーからAPIキー入力欄を削除（Secretsから自動取得に変更）
- [x] サイドバーからモデル選択を削除（Sonnet 4.5固定）
- [x] パスワード認証画面を追加（正しいパスワードを入力しないとアプリが使えない）
- [x] ローカルテスト確認

### Phase 2: デプロイ設定ファイル作成
- [x] `requirements.txt` 作成（Streamlit Cloud用の依存パッケージ一覧）
- [x] `.streamlit/config.toml` 作成（テーマ・サーバー設定）

### Phase 3: GitHubプッシュ & デプロイ
- [x] 変更をコミット・プッシュ
- [x] Streamlit Community Cloudでのデプロイ手順をガイド
- [x] デプロイ完了（リポジトリをPublicに変更して対応）

## 🔧 技術詳細

### パスワード認証の仕組み
```
アプリ起動 → パスワード入力画面
  → 正しい → メイン画面表示
  → 間違い → エラー表示、再入力を促す
```
パスワードは Streamlit Secrets に保存（`APP_PASSWORD`）

### Secrets に登録する値（デプロイ時にブラウザGUIで設定）
```toml
ANTHROPIC_API_KEY = "sk-ant-api03-..."
APP_PASSWORD = "任意のパスワード"
```

### UIの変更イメージ
**Before（現在）**
- サイドバー：APIキー入力、モデル選択、使い方ガイド

**After（修正後）**
- サイドバー：使い方ガイドのみ
- APIキー → `st.secrets["ANTHROPIC_API_KEY"]` から自動取得
- モデル → `claude-sonnet-4-5-20250929` 固定

## 📁 ファイル配置計画
- 修正ファイル：`app/app.py`, `app/claude_client.py`
- 新規作成：`requirements.txt`, `.streamlit/config.toml`

## 🚨 リスク・注意事項
- Streamlit Community Cloud は無料だがURLを知っている人は誰でもアクセス可能 → パスワード認証で対策
- APIキーの流出防止 → Secrets管理で対応（コードには一切書かない）
- 無料プランはアプリが一定期間非アクティブだとスリープする（アクセスすると自動復帰）

---
**この計画でよろしいですか？**
