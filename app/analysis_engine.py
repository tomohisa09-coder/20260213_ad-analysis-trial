"""
分析エンジン：データ前処理・集計・グラフ生成
既存スクリプト（01-03）を関数化したもの
"""

import io
import json
import re
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import seaborn as sns


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# スタイル設定
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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


def _get_colors(names):
    """クリエイティブ名に対する色の動的割り当て"""
    palette = sns.color_palette("husl", max(len(names), 4))
    return {n: palette[i] for i, n in enumerate(sorted(names))}


def _get_markers(names):
    markers = ["o", "s", "^", "D", "v", "P", "X", "*"]
    return {n: markers[i % len(markers)] for i, n in enumerate(sorted(names))}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Phase 1: データ前処理
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def process_excel(uploaded_file) -> pd.DataFrame:
    """Excelファイルを読み込みクリーニングする"""
    df = pd.read_excel(uploaded_file)
    df["レポート開始日"] = pd.to_datetime(df["レポート開始日"])
    df["レポート終了日"] = pd.to_datetime(df["レポート終了日"])
    df["is_active"] = df["消化金額 (JPY)"] > 0
    return df


def parse_creative_jsons(json_files: list[dict]) -> list[dict]:
    """
    アップロードされたJSONファイル群をパースする
    json_files: [{"filename": "xxx.json", "content": {...}}, ...]
    """
    creatives = []
    for jf in json_files:
        data = jf["content"]
        summary = data.get("analysis_summary", {})
        timeline = data.get("timeline_analysis", [])

        # タイムラインからhook/body/cta構造を推定
        hook_sec = 0
        body_sec = 0
        cta_sec = 0
        for seg in timeline:
            tr = seg.get("time_range", "00:00-00:00")
            parts = tr.split("-")
            if len(parts) == 2:
                start = _parse_time(parts[0])
                end = _parse_time(parts[1])
                dur = end - start
            else:
                dur = 0
            stype = seg.get("segment_type", "")
            if "hook" in stype:
                hook_sec += dur
            elif "cta" in stype:
                cta_sec += dur
            else:
                body_sec += dur

        total = summary.get("total_duration_sec", hook_sec + body_sec + cta_sec)

        creatives.append({
            "video_id": data.get("video_id", jf["filename"]),
            "creative_type": summary.get("creative_type", "unknown"),
            "duration_sec": total,
            "duration_category": "長尺" if total >= 30 else "短尺",
            "hook_strength_score": summary.get("hook_strength_score", 0),
            "primary_angle": summary.get("primary_angle", ""),
            "overall_sentiment": summary.get("overall_sentiment", ""),
            "segment_count": len(timeline),
            "hook_duration_sec": hook_sec,
            "body_duration_sec": body_sec,
            "cta_duration_sec": cta_sec,
            "target_audience": summary.get("target_audience", ""),
            "_raw_json": data,
            "_qualitative_text": jf.get("qualitative_text", ""),
        })
    return creatives


def parse_creative_md(md_text: str, filename: str = "") -> list[dict]:
    """
    MDファイルからクリエイティブ情報を抽出する
    1つのMDに複数クリエイティブが含まれる場合は分割して返す

    Returns: [{"filename": ..., "content": {...}, "qualitative_text": "..."}, ...]
    """
    # ## N. で始まるセクションで分割
    sections = re.split(r'(?=^## \d+\.)', md_text, flags=re.MULTILINE)

    results = []
    for section in sections:
        # JSONブロックを抽出（{ で始まり } で終わるブロック）
        json_blocks = []
        brace_depth = 0
        current_block = []
        in_block = False

        for line in section.split('\n'):
            stripped = line.rstrip().rstrip(' ')
            if not in_block and stripped.startswith('{'):
                in_block = True
                brace_depth = 0

            if in_block:
                current_block.append(line)
                brace_depth += stripped.count('{') - stripped.count('}')
                if brace_depth <= 0:
                    block_text = '\n'.join(current_block)
                    try:
                        parsed = json.loads(block_text)
                        if "video_id" in parsed:
                            json_blocks.append(parsed)
                    except json.JSONDecodeError:
                        pass
                    current_block = []
                    in_block = False

        if not json_blocks:
            continue

        # 定性テキスト抽出（JSONブロック以外の部分）
        qualitative_parts = []
        in_json = False
        brace_depth = 0
        for line in section.split('\n'):
            stripped = line.rstrip().rstrip(' ')
            if not in_json and stripped.startswith('{'):
                in_json = True
                brace_depth = 0
            if in_json:
                brace_depth += stripped.count('{') - stripped.count('}')
                if brace_depth <= 0:
                    in_json = False
                continue
            # JSONヘッダー行をスキップ
            if stripped in ('JSON', '##') or stripped.startswith('**') and 'JSON' in stripped:
                continue
            qualitative_parts.append(line)

        qualitative_text = '\n'.join(qualitative_parts).strip()

        for json_data in json_blocks:
            results.append({
                "filename": filename,
                "content": json_data,
                "qualitative_text": qualitative_text,
            })

    return results


def _parse_time(t: str) -> int:
    """'00:10' → 10 秒"""
    parts = t.strip().split(":")
    if len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    return 0


def build_summary(df: pd.DataFrame, creative_attrs: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    日次パフォーマンスとクリエイティブ属性からサマリーテーブルを構築
    Returns: (active_df, summary_df)
    """
    active_df = df[df["is_active"]].copy()

    # 視聴維持率
    for col in ["動画の3秒再生数", "動画の25%再生数", "動画の50%再生数",
                "動画の75%再生数", "動画の95%再生数", "動画の100%再生数"]:
        rate_col = col.replace("再生数", "再生率")
        active_df[rate_col] = active_df[col] / active_df["インプレッション"] * 100

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
        _3秒再生合計=("動画の3秒再生数", "sum"),
        _25再生合計=("動画の25%再生数", "sum"),
        _50再生合計=("動画の50%再生数", "sum"),
        _75再生合計=("動画の75%再生数", "sum"),
        _95再生合計=("動画の95%再生数", "sum"),
        _100再生合計=("動画の100%再生数", "sum"),
    ).reset_index()

    summary["全体CTR"] = summary["リンククリック合計"] / summary["インプレッション合計"] * 100
    summary["全体CPC"] = summary["消化金額合計"] / summary["リンククリック合計"]
    summary["全体CPM"] = summary["消化金額合計"] / summary["インプレッション合計"] * 1000
    summary["CPA"] = summary["消化金額合計"] / summary["購入合計"]
    summary["日次平均消化"] = summary["消化金額合計"] / summary["配信日数"]

    for pct, col in [("3秒", "_3秒再生合計"), ("25%", "_25再生合計"), ("50%", "_50再生合計"),
                     ("75%", "_75再生合計"), ("95%", "_95再生合計"), ("100%", "_100再生合計")]:
        summary[f"{pct}視聴率"] = summary[col] / summary["インプレッション合計"] * 100

    # クリエイティブ属性と結合
    if creative_attrs is not None and len(creative_attrs) > 0:
        summary = summary.merge(creative_attrs, on="広告の名前", how="left")

    return active_df, summary


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Phase 2: グラフ生成（各関数はmatplotlib Figureを返す）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def generate_kpi_chart(summary: pd.DataFrame) -> plt.Figure:
    """KPIサマリー比較（棒グラフ 2x2）"""
    setup_style()
    names = summary["クリエイティブ短縮名"].tolist()
    colors = _get_colors(names)

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    metrics = [
        ("全体CTR", "CTR（%）"),
        ("全体CPC", "CPC（円）"),
        ("CPA", "CPA（円）"),
        ("3秒視聴率", "3秒視聴率（%）"),
    ]

    for ax, (col, ylabel) in zip(axes.flat, metrics):
        bars = ax.bar(names, summary[col],
                      color=[colors[n] for n in names], edgecolor="black", linewidth=0.5)
        for bar, val in zip(bars, summary[col]):
            if "円" in ylabel:
                fmt = f"¥{val:,.0f}"
            elif "%" in ylabel or "CTR" in ylabel:
                fmt = f"{val:.2f}%"
            else:
                fmt = f"{val:.1f}%"
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() * 1.02,
                    fmt, ha="center", va="bottom", fontsize=11, fontweight="bold")
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(col, fontsize=14, fontweight="bold", pad=10)
        ax.set_ylim(0, summary[col].max() * 1.35)
        ax.tick_params(axis="x", rotation=15)

    fig.suptitle("クリエイティブ別 主要KPI比較", fontsize=18, fontweight="bold", y=1.02)
    plt.tight_layout()
    return fig


def generate_retention_chart(summary: pd.DataFrame) -> plt.Figure:
    """動画視聴維持率カーブ"""
    setup_style()
    names = summary["クリエイティブ短縮名"].tolist()
    colors = _get_colors(names)
    markers = _get_markers(names)

    fig, ax = plt.subplots(figsize=(16, 9))
    retention_points = ["3秒視聴率", "25%視聴率", "50%視聴率", "75%視聴率", "95%視聴率", "100%視聴率"]
    x_labels = ["3秒", "25%", "50%", "75%", "95%", "100%"]

    for _, row in summary.iterrows():
        name = row["クリエイティブ短縮名"]
        vals = [row.get(c, 0) for c in retention_points]
        dur = int(row.get("duration_sec", 0))
        label = f"{name}（{dur}秒）" if dur > 0 else name
        ax.plot(x_labels, vals, color=colors[name], marker=markers[name],
                label=label, linewidth=2.5, markersize=8)
        for i, v in enumerate(vals):
            ax.annotate(f"{v:.1f}%", (x_labels[i], v),
                        textcoords="offset points", xytext=(0, 10),
                        ha="center", fontsize=9, color=colors[name])

    ax.set_ylabel("視聴率（%）", fontsize=13)
    ax.set_xlabel("視聴到達ポイント", fontsize=13)
    ax.set_title("動画視聴維持率カーブ（クリエイティブ比較）", fontsize=16, fontweight="bold", pad=20)
    ax.legend(fontsize=11, loc="upper right")
    vmax = summary[retention_points].max().max()
    ax.set_ylim(0, (vmax or 1) * 1.35)
    plt.tight_layout()
    return fig


def generate_cost_matrix(summary: pd.DataFrame) -> plt.Figure:
    """コスト効率マトリックス（CTR vs CPA）"""
    setup_style()
    names = summary["クリエイティブ短縮名"].tolist()
    colors = _get_colors(names)

    fig, ax = plt.subplots(figsize=(16, 9))
    for _, row in summary.iterrows():
        name = row["クリエイティブ短縮名"]
        ax.scatter(row["全体CTR"], row["CPA"],
                   s=max(row["消化金額合計"] / 30, 100),
                   color=colors[name], edgecolors="black", linewidth=0.8, alpha=0.8, zorder=5)
        ax.annotate(f"{name}\n(¥{row['CPA']:,.0f})",
                    (row["全体CTR"], row["CPA"]),
                    textcoords="offset points", xytext=(15, 10),
                    fontsize=11, fontweight="bold", color=colors[name],
                    arrowprops=dict(arrowstyle="-", color=colors[name], lw=0.8))

    ax.set_xlabel("CTR（%）", fontsize=13)
    ax.set_ylabel("CPA（円）", fontsize=13)
    ax.set_title("コスト効率マトリックス（CTR vs CPA）\nバブルサイズ＝消化金額",
                 fontsize=16, fontweight="bold", pad=20)
    ax.set_xlim(0, summary["全体CTR"].max() * 1.4)
    ax.set_ylim(0, summary["CPA"].max() * 1.35)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f"¥{x:,.0f}"))
    plt.tight_layout()
    return fig


def generate_daily_trend(daily: pd.DataFrame) -> plt.Figure:
    """日次推移グラフ（消化金額・CTR）"""
    setup_style()
    names = daily["クリエイティブ短縮名"].dropna().unique().tolist()
    colors = _get_colors(names)
    markers = _get_markers(names)

    fig, axes = plt.subplots(2, 1, figsize=(16, 12), sharex=True)

    ax = axes[0]
    for name, group in daily.groupby("クリエイティブ短縮名"):
        ax.plot(group["レポート開始日"], group["消化金額 (JPY)"],
                color=colors[name], marker=markers[name], label=name, linewidth=2, markersize=6)
    ax.set_ylabel("消化金額（円）", fontsize=12)
    ax.set_title("日次 消化金額推移", fontsize=14, fontweight="bold", pad=15)
    ax.legend(fontsize=10, loc="upper right")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f"¥{x:,.0f}"))

    ax = axes[1]
    for name, group in daily.groupby("クリエイティブ短縮名"):
        g = group[group["CTR(リンククリックスルー率)"].notna()]
        if len(g) > 0:
            ax.plot(g["レポート開始日"], g["CTR(リンククリックスルー率)"],
                    color=colors[name], marker=markers[name], label=name, linewidth=2, markersize=6)
    ax.set_ylabel("CTR（%）", fontsize=12)
    ax.set_xlabel("日付", fontsize=12)
    ax.set_title("日次 CTR推移", fontsize=14, fontweight="bold", pad=15)
    ax.legend(fontsize=10, loc="upper right")

    fig.suptitle("日次パフォーマンス推移", fontsize=18, fontweight="bold", y=1.02)
    plt.tight_layout()
    return fig


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# KPIサマリーテキスト生成（Claude APIへの入力用）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def build_kpi_text(summary: pd.DataFrame) -> str:
    """Claude APIに渡すためのKPIサマリーテキストを生成"""
    lines = ["## クリエイティブ別KPIサマリー\n"]
    lines.append("| クリエイティブ | 配信日数 | 消化金額 | Imp | CTR | CPC | CPA | 3秒視聴率 | 100%視聴率 |")
    lines.append("|---|---|---|---|---|---|---|---|---|")

    for _, row in summary.iterrows():
        name = row.get("クリエイティブ短縮名", row["広告の名前"])
        lines.append(
            f"| {name} "
            f"| {int(row['配信日数'])}日 "
            f"| ¥{row['消化金額合計']:,.0f} "
            f"| {row['インプレッション合計']:,.0f} "
            f"| {row['全体CTR']:.2f}% "
            f"| ¥{row['全体CPC']:,.0f} "
            f"| ¥{row['CPA']:,.0f} "
            f"| {row['3秒視聴率']:.1f}% "
            f"| {row['100%視聴率']:.1f}% |"
        )

    # 視聴維持率テーブル
    lines.append("\n## 視聴維持率\n")
    lines.append("| クリエイティブ | 3秒 | 25% | 50% | 75% | 95% | 100% |")
    lines.append("|---|---|---|---|---|---|---|")
    for _, row in summary.iterrows():
        name = row.get("クリエイティブ短縮名", row["広告の名前"])
        lines.append(
            f"| {name} "
            f"| {row['3秒視聴率']:.1f}% "
            f"| {row['25%視聴率']:.1f}% "
            f"| {row['50%視聴率']:.1f}% "
            f"| {row['75%視聴率']:.1f}% "
            f"| {row['95%視聴率']:.1f}% "
            f"| {row['100%視聴率']:.1f}% |"
        )

    return "\n".join(lines)
