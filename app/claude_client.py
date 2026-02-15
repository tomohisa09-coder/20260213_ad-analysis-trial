"""
Claude API連携：プロンプト構築とAPI呼び出し
"""

import json
from pathlib import Path
from anthropic import Anthropic


PROMPT_TEMPLATE = (Path(__file__).parent / "prompts" / "analysis_prompt.md").read_text(encoding="utf-8")

MODEL_MAP = {
    "Sonnet 4.5（推奨・低コスト）": "claude-sonnet-4-5-20250929",
    "Opus 4.6（最高品質・高コスト）": "claude-opus-4-6",
}


def run_analysis(
    api_key: str,
    kpi_summary_text: str,
    creative_jsons: list[dict],
    model_label: str = "Sonnet 4.5（推奨・低コスト）",
) -> str:
    """
    Claude APIを呼び出してクロス分析レポートを生成する

    Args:
        api_key: Anthropic API Key
        kpi_summary_text: build_kpi_text() の出力
        creative_jsons: parse_creative_jsons() の出力リスト
        model_label: MODEL_MAP のキー

    Returns:
        分析レポート（Markdown文字列）
    """
    client = Anthropic(api_key=api_key)

    # JSONからAPI入力用テキストを構築（_raw_jsonを使用）
    json_text_parts = []
    for cr in creative_jsons:
        raw = cr.get("_raw_json", cr)
        json_text_parts.append(json.dumps(raw, ensure_ascii=False, indent=2))
    creative_json_text = "\n\n---\n\n".join(json_text_parts)

    # プロンプト組み立て
    prompt = PROMPT_TEMPLATE.format(
        kpi_summary=kpi_summary_text,
        creative_json=creative_json_text,
    )

    model_id = MODEL_MAP.get(model_label, "claude-sonnet-4-5-20250929")

    message = client.messages.create(
        model=model_id,
        max_tokens=8192,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text
