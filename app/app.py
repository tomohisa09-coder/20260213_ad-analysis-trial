"""
動画広告クリエイティブ × パフォーマンス分析アプリ
Gemini手動JSON + Excel → Claude API → レポート自動生成
"""

import json
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os

from analysis_engine import (
    process_excel,
    parse_creative_jsons,
    build_summary,
    build_kpi_text,
    generate_kpi_chart,
    generate_retention_chart,
    generate_cost_matrix,
    generate_daily_trend,
)
from claude_client import run_analysis, MODEL_MAP

load_dotenv()

# ── ページ設定 ────────────────────────────────────────
st.set_page_config(
    page_title="Ad Creative Analyzer",
    page_icon="📊",
    layout="wide",
)

st.title("📊 動画広告クリエイティブ × パフォーマンス分析")
st.caption("Gemini手動JSON + Excel → Claude API → レポート自動生成")

# ── サイドバー: API設定 ──────────────────────────────────
with st.sidebar:
    st.header("⚙️ 設定")
    api_key = st.text_input(
        "Claude API Key",
        value=os.getenv("ANTHROPIC_API_KEY", ""),
        type="password",
        help="Anthropic Console で取得したAPIキーを入力",
    )
    model_choice = st.selectbox("分析モデル", list(MODEL_MAP.keys()))

    st.divider()
    st.markdown("**使い方**")
    st.markdown(
        "1. Excelをアップロード\n"
        "2. JSONをアップロード\n"
        "3. 広告名とJSONを紐付け\n"
        "4. 「分析開始」を押す"
    )

# ── Step 1: ファイルアップロード ──────────────────────────
st.header("Step 1: データアップロード")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 パフォーマンスデータ")
    excel_file = st.file_uploader(
        "Meta広告のExcel/CSVをアップロード",
        type=["xlsx", "xls", "csv"],
        key="excel",
    )

with col2:
    st.subheader("🎬 クリエイティブ分析JSON")
    json_files = st.file_uploader(
        "Geminiで生成したJSONをアップロード（複数可）",
        type=["json"],
        accept_multiple_files=True,
        key="json",
    )

# ── Step 2: データ確認・紐付け ─────────────────────────────
if excel_file and json_files:
    st.header("Step 2: データ確認・紐付け")

    # Excel処理
    df = process_excel(excel_file)
    ad_names = df["広告の名前"].unique().tolist()

    st.subheader("📊 パフォーマンスデータ プレビュー")
    st.dataframe(df.head(10), use_container_width=True)
    st.caption(f"全 {len(df)} 行 / 広告 {len(ad_names)} 本 / "
               f"期間: {df['レポート開始日'].min().strftime('%Y/%m/%d')} 〜 {df['レポート開始日'].max().strftime('%Y/%m/%d')}")

    # JSON処理
    parsed_jsons = []
    for jf in json_files:
        content = json.load(jf)
        parsed_jsons.append({"filename": jf.name, "content": content})

    creatives = parse_creative_jsons(parsed_jsons)

    st.subheader("🎬 クリエイティブ情報")
    for cr in creatives:
        with st.expander(f"📹 {cr['video_id']}（{cr['duration_sec']}秒 / {cr['creative_type']}）"):
            st.json(cr["_raw_json"])

    # 紐付けUI
    st.subheader("🔗 広告名 ↔ クリエイティブJSON の紐付け")
    st.caption("Excel内の広告名と、JSONのクリエイティブを対応させてください")

    mapping = {}
    short_names = {}
    for ad_name in ad_names:
        col_a, col_b = st.columns([2, 1])
        with col_a:
            video_options = ["（対応なし）"] + [cr["video_id"] for cr in creatives]
            selected = st.selectbox(
                f"「{ad_name}」に対応するJSON",
                video_options,
                key=f"map_{ad_name}",
            )
            if selected != "（対応なし）":
                mapping[ad_name] = selected
        with col_b:
            sname = st.text_input("短縮名", value=ad_name[:10], key=f"short_{ad_name}")
            short_names[ad_name] = sname

    # 紐付けからクリエイティブ属性DataFrameを構築
    df["クリエイティブ短縮名"] = df["広告の名前"].map(short_names)

    creative_attrs_rows = []
    for ad_name, video_id in mapping.items():
        cr = next((c for c in creatives if c["video_id"] == video_id), None)
        if cr:
            creative_attrs_rows.append({
                "広告の名前": ad_name,
                "クリエイティブ短縮名": short_names.get(ad_name, ad_name),
                "video_id": cr["video_id"],
                "creative_type": cr["creative_type"],
                "duration_sec": cr["duration_sec"],
                "duration_category": cr["duration_category"],
                "hook_strength_score": cr["hook_strength_score"],
                "primary_angle": cr["primary_angle"],
                "segment_count": cr["segment_count"],
                "hook_duration_sec": cr["hook_duration_sec"],
                "body_duration_sec": cr["body_duration_sec"],
                "cta_duration_sec": cr["cta_duration_sec"],
            })

    creative_attrs = pd.DataFrame(creative_attrs_rows) if creative_attrs_rows else None

    # ── Step 3 & 4: 分析実行 ──────────────────────────────
    st.header("Step 3: 分析実行")

    if st.button("🚀 分析開始", type="primary", use_container_width=True):

        if not mapping:
            st.error("少なくとも1つの広告名とJSONを紐付けてください")
            st.stop()

        # --- 定量分析 ---
        with st.spinner("📊 定量分析を実行中..."):
            active_df, summary = build_summary(df, creative_attrs)

        st.subheader("📋 KPIサマリー")
        display_cols = ["クリエイティブ短縮名", "配信日数", "消化金額合計",
                        "インプレッション合計", "全体CTR", "全体CPC", "CPA",
                        "3秒視聴率", "100%視聴率"]
        available = [c for c in display_cols if c in summary.columns]
        st.dataframe(
            summary[available].style.format({
                "消化金額合計": "¥{:,.0f}",
                "インプレッション合計": "{:,.0f}",
                "全体CTR": "{:.2f}%",
                "全体CPC": "¥{:,.0f}",
                "CPA": "¥{:,.0f}",
                "3秒視聴率": "{:.1f}%",
                "100%視聴率": "{:.1f}%",
            }),
            use_container_width=True,
        )

        # --- グラフ表示 ---
        st.subheader("📈 パフォーマンスグラフ")
        tab1, tab2, tab3, tab4 = st.tabs(["KPI比較", "視聴維持率", "コスト効率", "日次推移"])

        with tab1:
            fig = generate_kpi_chart(summary)
            st.pyplot(fig)
        with tab2:
            fig = generate_retention_chart(summary)
            st.pyplot(fig)
        with tab3:
            fig = generate_cost_matrix(summary)
            st.pyplot(fig)
        with tab4:
            fig = generate_daily_trend(active_df)
            st.pyplot(fig)

        # --- AI分析 ---
        st.subheader("🤖 AI分析（Claude API）")

        if not api_key:
            st.warning("サイドバーにClaude API Keyを入力してください")
            st.stop()

        kpi_text = build_kpi_text(summary)
        creative_json_for_api = [cr for cr in creatives if cr["video_id"] in mapping.values()]

        with st.spinner(f"🧠 {model_choice} で分析中...（30秒〜1分ほどかかります）"):
            try:
                report = run_analysis(
                    api_key=api_key,
                    kpi_summary_text=kpi_text,
                    creative_jsons=creative_json_for_api,
                    model_label=model_choice,
                )
                st.session_state["report"] = report
            except Exception as e:
                st.error(f"API呼び出しエラー: {e}")
                st.stop()

        st.markdown(report)

        # --- エクスポート ---
        st.header("Step 4: エクスポート")

        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button(
                "📥 レポートをダウンロード（Markdown）",
                data=report,
                file_name="analysis_report.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with col_dl2:
            st.download_button(
                "📥 レポートをダウンロード（テキスト）",
                data=report,
                file_name="analysis_report.txt",
                mime="text/plain",
                use_container_width=True,
            )

elif excel_file:
    st.info("クリエイティブ分析JSON（Gemini出力）もアップロードしてください")
elif json_files:
    st.info("パフォーマンスデータ（Excel/CSV）もアップロードしてください")
else:
    st.info("Excel（パフォーマンスデータ）と JSON（クリエイティブ分析）をアップロードしてください")
