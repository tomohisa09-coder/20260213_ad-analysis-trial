"""
Phase 3-4: クリエイティブ構造×パフォーマンスのクロス分析 + 深堀り分析
- クリエイティブ属性とKPIの対応分析
- フック手法・動画構造と視聴維持率の関係
- 短尺 vs 長尺の効率性比較
- 勝ちパターン抽出・敗因分析
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import seaborn as sns
from pathlib import Path

# ── パス設定 ──────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "processed" / "ad_analysis"
FIG_DIR = ROOT / "reports" / "figures" / "ad_creative_analysis"
TBL_DIR = ROOT / "reports" / "tables"

# ── データ読み込み ────────────────────────────────────────
summary = pd.read_csv(DATA_DIR / "creative_summary.csv")
daily = pd.read_csv(DATA_DIR / "daily_performance.csv", parse_dates=["レポート開始日"])

# ── スタイル設定 ──────────────────────────────────────────
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

COLORS = {
    "フロリオ・コーチ": "#E74C3C",
    "鈴木啓太": "#3498DB",
    "疑い深い親子": "#2ECC71",
    "純粋無垢な少年": "#F39C12",
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 図6: クリエイティブ構造 × パフォーマンス統合ダッシュボード
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
fig, axes = plt.subplots(2, 3, figsize=(20, 13))

# 6-a: フック強度スコア vs CTR
ax = axes[0, 0]
for _, row in summary.iterrows():
    name = row["クリエイティブ短縮名"]
    ax.scatter(row["hook_strength_score"], row["全体CTR"],
               s=200, color=COLORS[name], edgecolors="black", linewidth=0.8, zorder=5)
    ax.annotate(name, (row["hook_strength_score"], row["全体CTR"]),
                textcoords="offset points", xytext=(8, 8), fontsize=9, color=COLORS[name])
ax.set_xlabel("フック強度スコア", fontsize=11)
ax.set_ylabel("CTR（%）", fontsize=11)
ax.set_title("フック強度 vs CTR", fontsize=13, fontweight="bold")
ax.set_xlim(8.5, 9.8)

# 6-b: 動画尺 vs 3秒視聴率
ax = axes[0, 1]
for _, row in summary.iterrows():
    name = row["クリエイティブ短縮名"]
    ax.scatter(row["duration_sec"], row["3秒視聴率"],
               s=200, color=COLORS[name], edgecolors="black", linewidth=0.8, zorder=5)
    ax.annotate(name, (row["duration_sec"], row["3秒視聴率"]),
                textcoords="offset points", xytext=(8, 8), fontsize=9, color=COLORS[name])
ax.set_xlabel("動画尺（秒）", fontsize=11)
ax.set_ylabel("3秒視聴率（%）", fontsize=11)
ax.set_title("動画尺 vs 3秒視聴率", fontsize=13, fontweight="bold")

# 6-c: 動画尺 vs 100%視聴率
ax = axes[0, 2]
for _, row in summary.iterrows():
    name = row["クリエイティブ短縮名"]
    ax.scatter(row["duration_sec"], row["100%視聴率"],
               s=200, color=COLORS[name], edgecolors="black", linewidth=0.8, zorder=5)
    ax.annotate(name, (row["duration_sec"], row["100%視聴率"]),
                textcoords="offset points", xytext=(8, 8), fontsize=9, color=COLORS[name])
ax.set_xlabel("動画尺（秒）", fontsize=11)
ax.set_ylabel("100%視聴率（%）", fontsize=11)
ax.set_title("動画尺 vs 視聴完了率", fontsize=13, fontweight="bold")

# 6-d: フック時間比率 vs CTR
ax = axes[1, 0]
summary["hook_ratio"] = summary["hook_duration_sec"] / summary["duration_sec"] * 100
for _, row in summary.iterrows():
    name = row["クリエイティブ短縮名"]
    ax.scatter(row["hook_ratio"], row["全体CTR"],
               s=200, color=COLORS[name], edgecolors="black", linewidth=0.8, zorder=5)
    ax.annotate(f"{name}\n(Hook {row['hook_duration_sec']}秒/{row['duration_sec']}秒)",
                (row["hook_ratio"], row["全体CTR"]),
                textcoords="offset points", xytext=(8, 8), fontsize=8, color=COLORS[name])
ax.set_xlabel("フック時間比率（%）", fontsize=11)
ax.set_ylabel("CTR（%）", fontsize=11)
ax.set_title("フック時間比率 vs CTR", fontsize=13, fontweight="bold")

# 6-e: セグメント密度（セグメント数/秒）vs CTR
ax = axes[1, 1]
summary["segment_density"] = summary["segment_count"] / summary["duration_sec"]
for _, row in summary.iterrows():
    name = row["クリエイティブ短縮名"]
    ax.scatter(row["segment_density"], row["全体CTR"],
               s=200, color=COLORS[name], edgecolors="black", linewidth=0.8, zorder=5)
    ax.annotate(f"{name}\n({row['segment_count']}seg/{row['duration_sec']}秒)",
                (row["segment_density"], row["全体CTR"]),
                textcoords="offset points", xytext=(8, 8), fontsize=8, color=COLORS[name])
ax.set_xlabel("セグメント密度（seg/秒）", fontsize=11)
ax.set_ylabel("CTR（%）", fontsize=11)
ax.set_title("セグメント密度 vs CTR", fontsize=13, fontweight="bold")

# 6-f: 権威性要素の有無 vs CPA
ax = axes[1, 2]
auth_data = summary.copy()
auth_data["authority_label"] = auth_data["has_authority_figure"].map({True: "権威性あり", False: "権威性なし"})
for _, row in auth_data.iterrows():
    name = row["クリエイティブ短縮名"]
    x_pos = 0 if row["has_authority_figure"] else 1
    ax.scatter(x_pos, row["CPA"],
               s=300, color=COLORS[name], edgecolors="black", linewidth=0.8, zorder=5)
    ax.annotate(f"{name}\n¥{row['CPA']:,.0f}",
                (x_pos, row["CPA"]),
                textcoords="offset points", xytext=(15, 5), fontsize=9, color=COLORS[name])
ax.set_xticks([0, 1])
ax.set_xticklabels(["権威性あり\n（専門家/著名人）", "権威性なし\n（一般人のみ）"])
ax.set_ylabel("CPA（円）", fontsize=11)
ax.set_title("権威性の有無 vs CPA", fontsize=13, fontweight="bold")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f"¥{x:,.0f}"))
ax.set_ylim(0, auth_data["CPA"].max() * 1.35)

fig.suptitle("クリエイティブ構造 × パフォーマンス 多角的分析",
             fontsize=18, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig(FIG_DIR / "06_creative_structure_analysis.png", dpi=300, bbox_inches="tight")
plt.close()
print("06_creative_structure_analysis.png saved")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 図7: 動画構造タイムライン比較（横棒グラフ）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
fig, ax = plt.subplots(figsize=(16, 7))

segment_colors = {"hook": "#E74C3C", "body": "#3498DB", "cta": "#2ECC71"}
y_positions = list(range(len(summary)))
names = summary["クリエイティブ短縮名"].tolist()

for i, (_, row) in enumerate(summary.iterrows()):
    # Hook
    ax.barh(i, row["hook_duration_sec"], left=0,
            color=segment_colors["hook"], edgecolor="black", linewidth=0.5, height=0.6)
    ax.text(row["hook_duration_sec"] / 2, i, f"Hook\n{int(row['hook_duration_sec'])}秒",
            ha="center", va="center", fontsize=9, fontweight="bold", color="white")

    # Body
    ax.barh(i, row["body_duration_sec"], left=row["hook_duration_sec"],
            color=segment_colors["body"], edgecolor="black", linewidth=0.5, height=0.6)
    body_center = row["hook_duration_sec"] + row["body_duration_sec"] / 2
    ax.text(body_center, i, f"Body\n{int(row['body_duration_sec'])}秒",
            ha="center", va="center", fontsize=9, fontweight="bold", color="white")

    # CTA
    cta_left = row["hook_duration_sec"] + row["body_duration_sec"]
    ax.barh(i, row["cta_duration_sec"], left=cta_left,
            color=segment_colors["cta"], edgecolor="black", linewidth=0.5, height=0.6)

    # 右端にKPI
    total = row["duration_sec"]
    ax.text(total + 1, i,
            f"CTR={row['全体CTR']:.2f}% | CPA=¥{row['CPA']:,.0f}",
            ha="left", va="center", fontsize=10, fontweight="bold")

ax.set_yticks(y_positions)
ax.set_yticklabels([f"{n}\n({int(summary.iloc[i]['duration_sec'])}秒)" for i, n in enumerate(names)], fontsize=11)
ax.set_xlabel("秒数", fontsize=12)
ax.set_title("動画構造タイムライン比較（Hook / Body / CTA）", fontsize=16, fontweight="bold", pad=20)
ax.set_xlim(0, 65)

# 凡例
patches = [mpatches.Patch(color=c, label=l) for l, c in segment_colors.items()]
ax.legend(handles=patches, loc="upper right", fontsize=10)

ax.invert_yaxis()
plt.tight_layout()
plt.savefig(FIG_DIR / "07_video_structure_timeline.png", dpi=300, bbox_inches="tight")
plt.close()
print("07_video_structure_timeline.png saved")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 図8: 短尺 vs 長尺 効率性レーダーチャート
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
fig, axes = plt.subplots(1, 2, figsize=(18, 8))

# 長尺グループ（フロリオ + 鈴木）vs 短尺グループ（04 + 05）
long_form = summary[summary["duration_category"] == "長尺"]
short_form = summary[summary["duration_category"] == "短尺"]

# 比較指標の正規化（0-100スケール）
compare_metrics = {
    "CTR": ("全体CTR", True),       # 高い方が良い
    "CPC効率": ("全体CPC", False),   # 低い方が良い
    "CPA効率": ("CPA", False),       # 低い方が良い
    "3秒視聴率": ("3秒視聴率", True),
    "視聴完了率": ("100%視聴率", True),
    "Hook強度": ("hook_strength_score", True),
}

# 各クリエイティブの正規化値を計算
for metric_name, (col, higher_better) in compare_metrics.items():
    vmin = summary[col].min()
    vmax = summary[col].max()
    if vmax == vmin:
        summary[f"norm_{metric_name}"] = 50
    elif higher_better:
        summary[f"norm_{metric_name}"] = (summary[col] - vmin) / (vmax - vmin) * 100
    else:
        summary[f"norm_{metric_name}"] = (1 - (summary[col] - vmin) / (vmax - vmin)) * 100

# 長尺 vs 短尺 棒グラフ比較
norm_cols = [f"norm_{m}" for m in compare_metrics.keys()]
metric_labels = list(compare_metrics.keys())

long_avg = summary[summary["duration_category"] == "長尺"][norm_cols].mean()
short_avg = summary[summary["duration_category"] == "短尺"][norm_cols].mean()

# 左: グループ比較
ax = axes[0]
x = np.arange(len(metric_labels))
w = 0.35
bars1 = ax.bar(x - w/2, long_avg.values, w, label="長尺（48-50秒）", color="#3498DB", edgecolor="black", linewidth=0.5)
bars2 = ax.bar(x + w/2, short_avg.values, w, label="短尺（12-19秒）", color="#F39C12", edgecolor="black", linewidth=0.5)

for bar, val in zip(bars1, long_avg.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f"{val:.0f}",
            ha="center", va="bottom", fontsize=9, fontweight="bold")
for bar, val in zip(bars2, short_avg.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f"{val:.0f}",
            ha="center", va="bottom", fontsize=9, fontweight="bold")

ax.set_xticks(x)
ax.set_xticklabels(metric_labels, fontsize=10, rotation=20, ha="right")
ax.set_ylabel("正規化スコア（0-100）", fontsize=11)
ax.set_title("長尺 vs 短尺：パフォーマンス比較", fontsize=14, fontweight="bold")
ax.legend(fontsize=10, loc="upper right")
ax.set_ylim(0, 120)

# 右: 個別クリエイティブ比較
ax = axes[1]
x = np.arange(len(metric_labels))
w = 0.2
for i, (_, row) in enumerate(summary.iterrows()):
    name = row["クリエイティブ短縮名"]
    vals = [row[c] for c in norm_cols]
    ax.bar(x + (i - 1.5) * w, vals, w, label=name, color=COLORS[name], edgecolor="black", linewidth=0.5)

ax.set_xticks(x)
ax.set_xticklabels(metric_labels, fontsize=10, rotation=20, ha="right")
ax.set_ylabel("正規化スコア（0-100）", fontsize=11)
ax.set_title("クリエイティブ別：多次元パフォーマンス比較", fontsize=14, fontweight="bold")
ax.legend(fontsize=9, loc="upper right")
ax.set_ylim(0, 120)

fig.suptitle("動画フォーマット別 効率性比較", fontsize=18, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig(FIG_DIR / "08_format_efficiency_comparison.png", dpi=300, bbox_inches="tight")
plt.close()
print("08_format_efficiency_comparison.png saved")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 図9: 視聴ドロップオフ分析（各区間の離脱率）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
fig, ax = plt.subplots(figsize=(16, 9))

retention_cols = ["3秒視聴率", "25%視聴率", "50%視聴率", "75%視聴率", "95%視聴率", "100%視聴率"]
x_labels = ["0→3秒", "3秒→25%", "25%→50%", "50%→75%", "75%→95%", "95%→100%"]

for _, row in summary.iterrows():
    name = row["クリエイティブ短縮名"]
    rates = [row[c] for c in retention_cols]
    # 各区間のドロップオフ（前区間からの離脱率）
    dropoffs = [100 - rates[0]]  # 最初: 100% → 3秒
    for j in range(1, len(rates)):
        if rates[j-1] > 0:
            dropoff = (rates[j-1] - rates[j]) / rates[j-1] * 100
        else:
            dropoff = 0
        dropoffs.append(dropoff)

    ax.plot(x_labels, dropoffs,
            color=COLORS[name], marker="o", label=f"{name}（{int(row['duration_sec'])}秒）",
            linewidth=2.5, markersize=8)

    for i, v in enumerate(dropoffs):
        ax.annotate(f"{v:.1f}%", (x_labels[i], v),
                    textcoords="offset points", xytext=(0, 10),
                    ha="center", fontsize=9, color=COLORS[name])

ax.set_ylabel("区間離脱率（%）", fontsize=13)
ax.set_xlabel("視聴区間", fontsize=13)
ax.set_title("動画視聴 区間別ドロップオフ率\n（各区間で何%の視聴者が離脱したか）",
             fontsize=16, fontweight="bold", pad=20)
ax.legend(fontsize=11, loc="upper right")
ax.set_ylim(0, 100)

plt.tight_layout()
plt.savefig(FIG_DIR / "09_dropoff_analysis.png", dpi=300, bbox_inches="tight")
plt.close()
print("09_dropoff_analysis.png saved")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 図10: 総合スコアカード
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
fig, ax = plt.subplots(figsize=(18, 8))
ax.axis("off")

# スコアカードテーブル
table_data = []
headers = [
    "クリエイティブ", "タイプ", "尺", "フック手法",
    "CTR", "CPC", "CPA", "ROAS日平均",
    "3秒率", "完了率", "Hook強度", "総合評価"
]

for _, row in summary.iterrows():
    # ROAS計算（日次平均）
    cr_daily = daily[daily["クリエイティブ短縮名"] == row["クリエイティブ短縮名"]]
    roas_vals = cr_daily["購入ROAS(広告費用対効果)"].dropna()
    avg_roas = roas_vals.mean() if len(roas_vals) > 0 else 0

    # 総合評価（独自スコアリング）
    score = 0
    score += min(row["全体CTR"] / 2.5 * 30, 30)  # CTR（最大30点）
    score += min(max(0, 1 - row["CPA"] / 20000) * 25, 25)  # CPA効率（最大25点）
    score += min(row["3秒視聴率"] / 45 * 20, 20)  # 3秒視聴率（最大20点）
    score += min(row["100%視聴率"] / 8 * 15, 15)  # 完了率（最大15点）
    score += min(row["hook_strength_score"] / 10 * 10, 10)  # フック強度（最大10点）

    # 評価ランク
    if score >= 75:
        rank = "S"
    elif score >= 60:
        rank = "A"
    elif score >= 45:
        rank = "B"
    else:
        rank = "C"

    table_data.append([
        row["クリエイティブ短縮名"],
        row["creative_type_ja"],
        f"{int(row['duration_sec'])}秒",
        row["hook_technique_ja"],
        f"{row['全体CTR']:.2f}%",
        f"¥{row['全体CPC']:,.0f}",
        f"¥{row['CPA']:,.0f}",
        f"{avg_roas:.2f}" if avg_roas > 0 else "N/A",
        f"{row['3秒視聴率']:.1f}%",
        f"{row['100%視聴率']:.1f}%",
        f"{row['hook_strength_score']}",
        f"{rank} ({score:.0f}点)",
    ])

table = ax.table(
    cellText=table_data,
    colLabels=headers,
    cellLoc="center",
    loc="center",
)

table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 2.5)

# ヘッダースタイル
for j in range(len(headers)):
    cell = table[0, j]
    cell.set_facecolor("#2C3E50")
    cell.set_text_props(color="white", fontweight="bold", fontsize=9)

# 行ごとの色分け
row_colors = ["#FDEBD0", "#D6EAF8", "#D5F5E3", "#FEF9E7"]
for i in range(len(table_data)):
    for j in range(len(headers)):
        cell = table[i + 1, j]
        cell.set_facecolor(row_colors[i])
        # 総合評価列のハイライト
        if j == len(headers) - 1:
            rank = table_data[i][-1][0]
            if rank == "S":
                cell.set_text_props(color="#E74C3C", fontweight="bold")
            elif rank == "A":
                cell.set_text_props(color="#3498DB", fontweight="bold")

ax.set_title("CORE STEP クリエイティブ 総合スコアカード",
             fontsize=18, fontweight="bold", pad=30)

plt.tight_layout()
plt.savefig(FIG_DIR / "10_scorecard.png", dpi=300, bbox_inches="tight")
plt.close()
print("10_scorecard.png saved")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# クロス分析テーブル出力
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
cross_cols = [
    "クリエイティブ短縮名", "creative_type_ja", "duration_sec", "duration_category",
    "hook_technique_ja", "primary_angle_ja", "hook_strength_score",
    "segment_count", "hook_duration_sec", "body_duration_sec", "cta_duration_sec",
    "hook_ratio", "segment_density",
    "has_authority_figure", "has_split_screen", "has_skeptic_element", "has_scientific_explanation",
    "全体CTR", "全体CPC", "CPA", "3秒視聴率", "100%視聴率",
]
summary[cross_cols].to_csv(TBL_DIR / "02_cross_analysis_table.csv", index=False, encoding="utf-8-sig")
print("\n02_cross_analysis_table.csv saved")

print("\n=== Phase 3-4 完了 ===")
