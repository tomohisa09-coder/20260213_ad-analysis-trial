# Ad Creative Analyzer

動画広告クリエイティブ × パフォーマンス分析の Streamlit アプリケーション。

Gemini で手動生成した動画分析 JSON/MD と、広告管理画面からエクスポートした Excel を組み合わせ、Claude API（Sonnet 4.5）による自動分析レポートを生成します。

## デモ

Streamlit Community Cloud にデプロイ済み（社内限定・パスワード認証あり）

## 主な機能

- **データアップロード**: Excel/CSV（パフォーマンスデータ）+ JSON/MD（クリエイティブ分析）をドラッグ＆ドロップ
- **広告×クリエイティブ紐付け**: UI 上で広告名と動画クリエイティブを手動マッピング
- **定量分析 & グラフ自動生成**:
  - KPI 比較（CTR / CPC / CPA / 3秒視聴率）
  - 動画視聴維持率カーブ
  - コスト効率マトリックス（CTR vs CPA）
  - 日次パフォーマンス推移
- **AI 分析レポート**: Claude API によるクリエイティブ×パフォーマンスのクロス分析
- **エクスポート**: Markdown / テキスト形式でレポートダウンロード

## 技術スタック

| カテゴリ | ツール |
|---|---|
| フロントエンド | Streamlit |
| AI 分析 | Claude API（Sonnet 4.5） |
| データ処理 | pandas, numpy |
| 可視化 | matplotlib, seaborn |
| 日本語フォント | matplotlib-fontja（IPAexGothic） |
| デプロイ | Streamlit Community Cloud |

## プロジェクト構成

```
├── app/
│   ├── app.py                  # Streamlit メインアプリ
│   ├── analysis_engine.py      # データ処理・集計・グラフ生成
│   ├── claude_client.py        # Claude API 連携
│   └── prompts/
│       └── analysis_prompt.md  # 分析プロンプトテンプレート
├── data/
│   └── raw/                    # 生データ（Excel, JSON, MD）
├── .streamlit/
│   └── config.toml             # Streamlit テーマ設定
├── requirements.txt            # Python 依存パッケージ
└── CLAUDE.md                   # Claude Code 指示書
```

## セットアップ

### ローカル開発

```bash
# 仮想環境の作成・有効化
python -m venv .venv
source .venv/bin/activate

# 依存パッケージのインストール
pip install -r requirements.txt

# 環境変数の設定（.env ファイル）
echo "ANTHROPIC_API_KEY=sk-ant-xxxxx" > .env

# アプリ起動
cd app
streamlit run app.py
```

### Streamlit Community Cloud デプロイ

1. GitHub リポジトリを Streamlit Community Cloud に接続
2. Main file path: `app/app.py`
3. Streamlit Secrets に以下を設定:
   - `APP_PASSWORD`: ログインパスワード
   - `ANTHROPIC_API_KEY`: Anthropic API キー

## 使い方

1. **Excel をアップロード**: 広告管理画面からエクスポートしたパフォーマンスデータ
2. **JSON or MD をアップロード**: Gemini で生成したクリエイティブ分析（1動画1ファイル）
3. **紐付け**: 各広告名に対応するクリエイティブを選択
4. **分析開始**: ボタンを押すと定量分析 → グラフ生成 → AI 分析が自動実行

### クリエイティブ分析ファイル形式

**JSON 形式**（推奨）:
```json
{
  "video_id": "動画A",
  "analysis_summary": {
    "creative_type": "testimonial",
    "total_duration_sec": 30,
    "hook_strength_score": 8,
    "primary_angle": "social_proof"
  },
  "timeline_analysis": [...]
}
```

**MD 形式**: Markdown 内に上記 JSON を含めるか、コードフェンス（```json）で囲む。JSON 外のテキストは定性分析として自動抽出されます。

## 開発メモ

### 日本語フォント対応

Streamlit Cloud（Linux）でのグラフ日本語表示には `matplotlib-fontja` を使用。`import matplotlib_fontja` で IPAexGothic フォントが自動登録されます。`sns.set_style()` がフォント設定を上書きするため、`setup_style()` 内で seaborn スタイル適用後にフォントを再設定しています。

### MD パーサー

1動画1MD ファイルの方針。ファイル内の最初の `video_id` 付き JSON ブロックを自動検出し、Gemini が出力する不正な JSON 値（例: `2（分割画面あり）`）も自動修復します。
