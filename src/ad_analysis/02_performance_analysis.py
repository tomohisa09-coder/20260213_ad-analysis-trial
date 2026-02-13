"""
Phase 2: パフォーマンス基礎分析 + 可視化
- KPIサマリーテーブル
- 日次推移グラフ
- 動画視聴維持率カーブ
- コスト効率比較
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from pathlib import Path

# ── パス設定 ──────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "processed" / "ad_analysis"
FIG_DIR = ROOT / "reports" / "figures" / "ad_creative_analysis"
TBL_DIR = ROOT / "reports" / "tables"
FIG_DIR.mkdir(parents=True, exist_ok=True)
TBL_DIR.mkdir(parents=True, exist_ok=True)

# ── データ読み込み ────────────────────────────────────────
daily = pd.read_csv(DATA_DIR / "daily_performance.csv", parse_dates=["レポート開始日", "レポート終了日"])
summary = pd.read_csv(DATA_DIR / "creative_summary.csv")

# ── スタイル設定（FigureGuide_v2準拠）─────────────────────
def setup_style(font_size=14):
    sns.set_style("whitegrid")
    plt.rcParams["font.family"] = ["Hiragino Sans", "DejaVu Sans", "sans-serif"]
    plt.rcParams["font.size"] = font_size
    plt.rcParams["figure.figsize"] = (16, 9)
    sns.set_palette("husl", 12)
    plt.rcParams["axes.linewidth"] = 0.8
    plt.rcParams["axes.edgecolor"] = "black"
    plt.rcParams["xtick.direction"] = "in"
    plt.rcParams["ytick.direction"] = "in"
    plt.rcParams["grid.linewidth"] = 0.5
    plt.rcParams["grid.alpha"] = 0.3

setup_style()

# カラーマップ（クリエイティブ別固定色）
COLORS = {
    "フロリオ・コーチ": "#E74C3C",
    "鈴木啓太": "#3498DB",
    "疑い深い親子": "#2ECC71",
    "純粋無垢な少年": "#F39C12",
}

MARKERS = {
    "フロリオ・コーチ": "o",
    "鈴木啓太": "s",
    "疑い深い親子": "^",
    "純粋無垢な少年": "D",
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 図1: KPIサマリー比較（棒グラフ 2x2）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

metrics = [
    ("全体CTR", "CTR（%）", "bar"),
    ("全体CPC", "CPC（円）", "bar"),
    ("CPA", "CPA（円）", "bar"),
    ("3秒視聴率", "3秒視聴率（%）", "bar"),
]

for ax, (col, ylabel, _) in zip(axes.flat, metrics):
    bars = ax.bar(
        summary["クリエイティブ短縮名"],
        summary[col],
        color=[COLORS[n] for n in summary["クリエイティブ短縮名"]],
        edgecolor="black",
        linewidth=0.5,
    )
    for bar, val in zip(bars, summary[col]):
        fmt = f"{val:.2f}%" if "%" in ylabel or "CTR" in ylabel else f"¥{val:,.0f}" if "円" in ylabel else f"{val:.1f}%"
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() * 1.02,
                fmt, ha="center", va="bottom", fontsize=11, fontweight="bold")
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(col, fontsize=14, fontweight="bold", pad=10)
    vmax = summary[col].max()
    ax.set_ylim(0, vmax * 1.35)
    ax.tick_params(axis="x", rotation=15)

fig.suptitle("CORE STEP クリエイティブ別 主要KPI比較", fontsize=18, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig(FIG_DIR / "01_kpi_comparison.png", dpi=300, bbox_inches="tight")
plt.close()
print("01_kpi_comparison.png saved")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 図2: 日次推移グラフ（消化金額・CTR）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
fig, axes = plt.subplots(2, 1, figsize=(16, 12), sharex=True)

# 2-a: 消化金額の日次推移
ax = axes[0]
for name, group in daily.groupby("クリエイティブ短縮名"):
    ax.plot(group["レポート開始日"], group["消化金額 (JPY)"],
            color=COLORS[name], marker=MARKERS[name], label=name,
            linewidth=2, markersize=6)
ax.set_ylabel("消化金額（円）", fontsize=12)
ax.set_title("日次 消化金額推移", fontsize=14, fontweight="bold", pad=15)
ax.legend(fontsize=10, loc="upper right")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f"¥{x:,.0f}"))
vmax = daily["消化金額 (JPY)"].max()
ax.set_ylim(0, vmax * 1.35)

# 2-b: CTRの日次推移
ax = axes[1]
for name, group in daily.groupby("クリエイティブ短縮名"):
    g = group[group["CTR(リンククリックスルー率)"].notna()]
    if len(g) > 0:
        ax.plot(g["レポート開始日"], g["CTR(リンククリックスルー率)"],
                color=COLORS[name], marker=MARKERS[name], label=name,
                linewidth=2, markersize=6)
ax.set_ylabel("CTR（%）", fontsize=12)
ax.set_xlabel("日付", fontsize=12)
ax.set_title("日次 CTR推移", fontsize=14, fontweight="bold", pad=15)
ax.legend(fontsize=10, loc="upper right")
vmax = daily["CTR(リンククリックスルー率)"].dropna().max()
ax.set_ylim(0, vmax * 1.35 if vmax > 0 else 5)

fig.suptitle("CORE STEP 日次パフォーマンス推移", fontsize=18, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig(FIG_DIR / "02_daily_trend.png", dpi=300, bbox_inches="tight")
plt.close()
print("02_daily_trend.png saved")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 図3: 動画視聴維持率カーブ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
fig, ax = plt.subplots(figsize=(16, 9))

retention_points = ["3秒視聴率", "25%視聴率", "50%視聴率", "75%視聴率", "95%視聴率", "100%視聴率"]
x_labels = ["3秒", "25%", "50%", "75%", "95%", "100%"]

for _, row in summary.iterrows():
    name = row["クリエイティブ短縮名"]
    vals = [row[c] for c in retention_points]
    duration = int(row["duration_sec"])
    label = f"{name}（{duration}秒）"
    ax.plot(x_labels, vals,
            color=COLORS[name], marker=MARKERS[name], label=label,
            linewidth=2.5, markersize=8)
    # 各ポイントに値表示
    for i, v in enumerate(vals):
        offset = 1.2 if v > 5 else 0.5
        ax.annotate(f"{v:.1f}%", (x_labels[i], v),
                    textcoords="offset points", xytext=(0, 10),
                    ha="center", fontsize=9, color=COLORS[name])

ax.set_ylabel("視聴率（%）", fontsize=13)
ax.set_xlabel("視聴到達ポイント", fontsize=13)
ax.set_title("動画視聴維持率カーブ（クリエイティブ比較）", fontsize=16, fontweight="bold", pad=20)
ax.legend(fontsize=11, loc="upper right")
vmax = summary[retention_points].max().max()
ax.set_ylim(0, vmax * 1.35)

plt.tight_layout()
plt.savefig(FIG_DIR / "03_video_retention_curve.png", dpi=300, bbox_inches="tight")
plt.close()
print("03_video_retention_curve.png saved")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 図4: コスト効率マトリックス（CTR vs CPA、バブル=消化金額）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
fig, ax = plt.subplots(figsize=(16, 9))

for _, row in summary.iterrows():
    name = row["クリエイティブ短縮名"]
    ax.scatter(row["全体CTR"], row["CPA"],
               s=row["消化金額合計"] / 30,  # バブルサイズ
               color=COLORS[name], edgecolors="black", linewidth=0.8,
               alpha=0.8, zorder=5)
    ax.annotate(f"{name}\n(¥{row['CPA']:,.0f})",
                (row["全体CTR"], row["CPA"]),
                textcoords="offset points", xytext=(15, 10),
                fontsize=11, fontweight="bold", color=COLORS[name],
                arrowprops=dict(arrowstyle="-", color=COLORS[name], lw=0.8))

ax.set_xlabel("CTR（%）", fontsize=13)
ax.set_ylabel("CPA（円）", fontsize=13)
ax.set_title("コスト効率マトリックス（CTR vs CPA）\nバブルサイズ＝消化金額", fontsize=16, fontweight="bold", pad=20)

# 理想エリア表示（右下＝高CTR・低CPA）
ax.annotate("← 理想エリア\n（高CTR・低CPA）", xy=(2.0, 6000),
            fontsize=12, color="green", alpha=0.6, fontweight="bold")

ax.set_xlim(0, summary["全体CTR"].max() * 1.4)
ax.set_ylim(0, summary["CPA"].max() * 1.35)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f"¥{x:,.0f}"))

plt.tight_layout()
plt.savefig(FIG_DIR / "04_cost_efficiency_matrix.png", dpi=300, bbox_inches="tight")
plt.close()
print("04_cost_efficiency_matrix.png saved")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 図5: 日次CPC・ROAS推移
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
fig, axes = plt.subplots(2, 1, figsize=(16, 12), sharex=True)

# 5-a: CPC推移
ax = axes[0]
for name, group in daily.groupby("クリエイティブ短縮名"):
    g = group[group["CPC(リンククリックの単価) (JPY)"].notna()]
    if len(g) > 0:
        ax.plot(g["レポート開始日"], g["CPC(リンククリックの単価) (JPY)"],
                color=COLORS[name], marker=MARKERS[name], label=name,
                linewidth=2, markersize=6)
ax.set_ylabel("CPC（円）", fontsize=12)
ax.set_title("日次 CPC推移", fontsize=14, fontweight="bold", pad=15)
ax.legend(fontsize=10, loc="upper right")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f"¥{x:,.0f}"))

# 5-b: ROAS推移
ax = axes[1]
for name, group in daily.groupby("クリエイティブ短縮名"):
    g = group[group["購入ROAS(広告費用対効果)"].notna()]
    if len(g) > 0:
        ax.plot(g["レポート開始日"], g["購入ROAS(広告費用対効果)"],
                color=COLORS[name], marker=MARKERS[name], label=name,
                linewidth=2, markersize=6)
ax.axhline(y=1.0, color="red", linestyle="--", alpha=0.5, label="ROAS=1.0（損益分岐）")
ax.set_ylabel("ROAS", fontsize=12)
ax.set_xlabel("日付", fontsize=12)
ax.set_title("日次 ROAS推移", fontsize=14, fontweight="bold", pad=15)
ax.legend(fontsize=10, loc="upper right")

fig.suptitle("CORE STEP コスト効率の日次推移", fontsize=18, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig(FIG_DIR / "05_daily_cpc_roas.png", dpi=300, bbox_inches="tight")
plt.close()
print("05_daily_cpc_roas.png saved")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# KPIサマリーテーブル出力（CSV）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
kpi_cols = [
    "クリエイティブ短縮名", "creative_type_ja", "duration_sec", "duration_category",
    "配信日数", "消化金額合計", "インプレッション合計", "リーチ合計",
    "リンククリック合計", "購入合計", "全体CTR", "全体CPC", "全体CPM",
    "CPA", "日次平均消化",
    "3秒視聴率", "25%視聴率", "50%視聴率", "75%視聴率", "95%視聴率", "100%視聴率",
    "hook_strength_score", "primary_angle_ja", "hook_technique_ja",
]
summary[kpi_cols].to_csv(TBL_DIR / "01_kpi_summary_table.csv", index=False, encoding="utf-8-sig")
print("\n01_kpi_summary_table.csv saved")

print("\n=== Phase 2 完了 ===")
