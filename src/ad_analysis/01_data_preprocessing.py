"""
Phase 1: データ前処理・統合
- Excelパフォーマンスデータの読み込み・クリーニング
- クリエイティブ属性情報の構造化
- 統合テーブルの作成と保存
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path

# ── パス設定 ──────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
OUT_DIR = ROOT / "data" / "processed" / "ad_analysis"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. Excel パフォーマンスデータの読み込み・クリーニング
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
xlsx_path = RAW_DIR / "kids向け動画CR_-_-_2026_01_23-_-2026_02_13.xlsx"
df = pd.read_excel(xlsx_path)

# 日付型変換
df["レポート開始日"] = pd.to_datetime(df["レポート開始日"])
df["レポート終了日"] = pd.to_datetime(df["レポート終了日"])

# 配信停止日（消化金額=0）のフラグ
df["is_active"] = df["消化金額 (JPY)"] > 0

# 短縮名の付与（分析用）
name_map = {
    "体験動画(フロリオ・コーチ)": "フロリオ・コーチ",
    "体験動画01": "鈴木啓太",
    "体験動画04(#56_20260106_フロリオサッカースクール#5)": "疑い深い親子",
    "体験動画05(#57_20260106_フロリオサッカースクール#6)": "純粋無垢な少年",
}
df["クリエイティブ短縮名"] = df["広告の名前"].map(name_map)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. クリエイティブ属性テーブルの構築
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
creative_attrs = pd.DataFrame([
    {
        "広告の名前": "体験動画(フロリオ・コーチ)",
        "クリエイティブ短縮名": "フロリオ・コーチ",
        "video_id": "core_step_florio_demo_01",
        "creative_type": "expert_demonstration",
        "creative_type_ja": "専門家実演型",
        "duration_sec": 48,
        "duration_category": "長尺",
        "hook_strength_score": 9.2,
        "primary_angle": "immediate_effect_evidence",
        "primary_angle_ja": "即効性×科学的根拠",
        "hook_technique": "failure_demonstration",
        "hook_technique_ja": "失敗実演→成功比較",
        "segment_count": 4,
        "hook_duration_sec": 10,
        "body_duration_sec": 36,
        "cta_duration_sec": 2,
        "has_authority_figure": True,
        "has_split_screen": False,
        "has_skeptic_element": False,
        "has_scientific_explanation": True,
        "target_audience": "30代後半〜慎重派・指導者・保護者",
    },
    {
        "広告の名前": "体験動画01",
        "クリエイティブ短縮名": "鈴木啓太",
        "video_id": "core_step_suzuki_demo_01",
        "creative_type": "celebrity_demonstration",
        "creative_type_ja": "著名人実演型",
        "duration_sec": 50,
        "duration_category": "長尺",
        "hook_strength_score": 9.5,
        "primary_angle": "authority_and_social_proof",
        "primary_angle_ja": "権威性×社会的証明",
        "hook_technique": "climax_first",
        "hook_technique_ja": "クライマックス先行",
        "segment_count": 5,
        "hook_duration_sec": 5,
        "body_duration_sec": 42,
        "cta_duration_sec": 3,
        "has_authority_figure": True,
        "has_split_screen": False,
        "has_skeptic_element": True,
        "has_scientific_explanation": False,
        "target_audience": "直感派・ミーハー・ブランド信頼重視",
    },
    {
        "広告の名前": "体験動画04(#56_20260106_フロリオサッカースクール#5)",
        "クリエイティブ短縮名": "疑い深い親子",
        "video_id": "core_step_skeptic_parent_child_split",
        "creative_type": "split_screen_comparison",
        "creative_type_ja": "画面分割比較型",
        "duration_sec": 12,
        "duration_category": "短尺",
        "hook_strength_score": 8.8,
        "primary_angle": "skepticism_verification",
        "primary_angle_ja": "疑念払拭×親子体験",
        "hook_technique": "negative_hook",
        "hook_technique_ja": "ネガティブフック（疑い）",
        "segment_count": 4,
        "hook_duration_sec": 3,
        "body_duration_sec": 8,
        "cta_duration_sec": 1,
        "has_authority_figure": False,
        "has_split_screen": True,
        "has_skeptic_element": True,
        "has_scientific_explanation": False,
        "target_audience": "TikTok/Reels若年層〜親世代",
    },
    {
        "広告の名前": "体験動画05(#57_20260106_フロリオサッカースクール#6)",
        "クリエイティブ短縮名": "純粋無垢な少年",
        "video_id": "core_step_innocent_boys_multiple_split",
        "creative_type": "split_screen_group_test",
        "creative_type_ja": "画面分割・複数事例型",
        "duration_sec": 19,
        "duration_category": "短尺",
        "hook_strength_score": 8.7,
        "primary_angle": "purity_and_reproducibility",
        "primary_angle_ja": "純粋さ×再現性",
        "hook_technique": "labeling_subjects",
        "hook_technique_ja": "被験者ラベリング（純粋無垢）",
        "segment_count": 5,
        "hook_duration_sec": 4,
        "body_duration_sec": 13,
        "cta_duration_sec": 2,
        "has_authority_figure": False,
        "has_split_screen": True,
        "has_skeptic_element": False,
        "has_scientific_explanation": False,
        "target_audience": "「たまたまでしょ？」と疑う層",
    },
])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. パフォーマンス集計テーブル（アクティブ日のみ）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
active_df = df[df["is_active"]].copy()

# 視聴維持率の計算（インプレッション対比）
for col in ["動画の3秒再生数", "動画の25%再生数", "動画の50%再生数",
            "動画の75%再生数", "動画の95%再生数", "動画の100%再生数"]:
    rate_col = col.replace("再生数", "再生率")
    active_df[rate_col] = active_df[col] / active_df["インプレッション"] * 100

# クリエイティブ別集計
summary = active_df.groupby("広告の名前").agg(
    配信日数=("レポート開始日", "nunique"),
    配信開始日=("レポート開始日", "min"),
    配信終了日=("レポート開始日", "max"),
    消化金額合計=("消化金額 (JPY)", "sum"),
    インプレッション合計=("インプレッション", "sum"),
    リーチ合計=("リーチ", "sum"),
    リンククリック合計=("リンクのクリック", "sum"),
    購入合計=("購入", "sum"),
    平均CTR=("CTR(リンククリックスルー率)", "mean"),
    平均CPC=("CPC(リンククリックの単価) (JPY)", "mean"),
    平均CPM=("CPM(インプレッション単価) (JPY)", "mean"),
    平均フリークエンシー=("フリークエンシー", "mean"),
    # 視聴維持（合計ベースで後から率に変換）
    _3秒再生合計=("動画の3秒再生数", "sum"),
    _25再生合計=("動画の25%再生数", "sum"),
    _50再生合計=("動画の50%再生数", "sum"),
    _75再生合計=("動画の75%再生数", "sum"),
    _95再生合計=("動画の95%再生数", "sum"),
    _100再生合計=("動画の100%再生数", "sum"),
).reset_index()

# 集計ベース指標
summary["全体CTR"] = summary["リンククリック合計"] / summary["インプレッション合計"] * 100
summary["全体CPC"] = summary["消化金額合計"] / summary["リンククリック合計"]
summary["全体CPM"] = summary["消化金額合計"] / summary["インプレッション合計"] * 1000
summary["CPA"] = summary["消化金額合計"] / summary["購入合計"]
summary["日次平均消化"] = summary["消化金額合計"] / summary["配信日数"]

# 視聴維持率（集計ベース）
summary["3秒視聴率"] = summary["_3秒再生合計"] / summary["インプレッション合計"] * 100
summary["25%視聴率"] = summary["_25再生合計"] / summary["インプレッション合計"] * 100
summary["50%視聴率"] = summary["_50再生合計"] / summary["インプレッション合計"] * 100
summary["75%視聴率"] = summary["_75再生合計"] / summary["インプレッション合計"] * 100
summary["95%視聴率"] = summary["_95再生合計"] / summary["インプレッション合計"] * 100
summary["100%視聴率"] = summary["_100再生合計"] / summary["インプレッション合計"] * 100

# クリエイティブ属性と結合
summary = summary.merge(creative_attrs, on="広告の名前", how="left")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. 保存
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 日次パフォーマンスデータ（アクティブ日のみ）
active_df.to_csv(OUT_DIR / "daily_performance.csv", index=False, encoding="utf-8-sig")

# クリエイティブ属性テーブル
creative_attrs.to_csv(OUT_DIR / "creative_attributes.csv", index=False, encoding="utf-8-sig")

# クリエイティブ別サマリー（属性付き）
summary.to_csv(OUT_DIR / "creative_summary.csv", index=False, encoding="utf-8-sig")

print("=== Phase 1 完了 ===")
print(f"\n保存先: {OUT_DIR}")
print(f"  - daily_performance.csv : {len(active_df)} rows")
print(f"  - creative_attributes.csv : {len(creative_attrs)} rows")
print(f"  - creative_summary.csv : {len(summary)} rows")

# サマリー確認
print("\n=== クリエイティブ別KPIサマリー ===")
display_cols = ["クリエイティブ短縮名", "配信日数", "消化金額合計", "インプレッション合計",
                "リンククリック合計", "購入合計", "全体CTR", "全体CPC", "CPA",
                "3秒視聴率", "100%視聴率", "duration_sec", "hook_strength_score"]
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)
pd.set_option("display.float_format", lambda x: f"{x:.2f}")
print(summary[display_cols].to_string(index=False))
