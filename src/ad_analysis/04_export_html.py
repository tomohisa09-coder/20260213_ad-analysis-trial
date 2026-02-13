"""
Markdown → HTML変換（画像base64埋め込み）
ブラウザで開いて全選択→Notionにペーストで画像ごと取り込み可能
"""

import base64
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MD_PATH = ROOT / "reports" / "docs" / "ad_creative_analysis_report.md"
FIG_DIR = ROOT / "reports" / "figures" / "ad_creative_analysis"
OUT_PATH = ROOT / "reports" / "docs" / "ad_creative_analysis_report.html"

md_text = MD_PATH.read_text(encoding="utf-8")

# ── 画像パスの解決とbase64変換 ──────────────────────────
def resolve_image(match):
    alt = match.group(1)
    rel_path = match.group(2)
    # MD→HTMLの相対パスを実ファイルに変換
    abs_path = (MD_PATH.parent / rel_path).resolve()
    if not abs_path.exists():
        return f"<p>[Image not found: {rel_path}]</p>"
    b64 = base64.b64encode(abs_path.read_bytes()).decode()
    suffix = abs_path.suffix.lstrip(".")
    mime = f"image/{suffix}" if suffix != "jpg" else "image/jpeg"
    return f'<img src="data:{mime};base64,{b64}" alt="{alt}" style="max-width:100%; margin:16px 0; border-radius:8px; box-shadow:0 2px 8px rgba(0,0,0,0.1);">'

md_text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", resolve_image, md_text)

# ── インライン変換 ────────────────────────────────────
def apply_inline(text):
    """インラインマークダウン変換"""
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`([^`]+)`", r'<code style="background:#f0f0f0; padding:2px 6px; border-radius:3px; font-size:13px;">\1</code>', text)
    return text

# ── Markdown → HTML 簡易変換 ──────────────────────────
lines = md_text.split("\n")
html_lines = []
in_table = False
in_code = False
in_ul = False

for line in lines:
    stripped = line.strip()

    # コードブロック
    if stripped.startswith("```"):
        if in_code:
            html_lines.append("</code></pre>")
            in_code = False
        else:
            html_lines.append('<pre style="background:#f4f4f4; padding:16px; border-radius:8px; overflow-x:auto; font-size:13px;"><code>')
            in_code = True
        continue
    if in_code:
        html_lines.append(line)
        continue

    # テーブル
    if "|" in stripped and not stripped.startswith("<"):
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if all(set(c) <= set("- :") for c in cells):
            continue  # セパレータ行をスキップ
        if not in_table:
            html_lines.append('<table style="border-collapse:collapse; width:100%; margin:16px 0; font-size:14px;">')
            tag = "th"
            in_table = True
        else:
            tag = "td"
        bg = ' style="background:#2C3E50; color:white; font-weight:bold; padding:10px 12px; border:1px solid #ddd; text-align:center;"' if tag == "th" else ' style="padding:10px 12px; border:1px solid #ddd; text-align:center;"'
        row = "<tr>" + "".join(f"<{tag}{bg}>{c}</{tag}>" for c in cells) + "</tr>"
        html_lines.append(row)
        continue
    else:
        if in_table:
            html_lines.append("</table>")
            in_table = False

    # リスト
    if re.match(r"^[-*]\s", stripped):
        if not in_ul:
            html_lines.append("<ul>")
            in_ul = True
        content = re.sub(r"^[-*]\s", "", stripped)
        content = apply_inline(content)
        html_lines.append(f"  <li>{content}</li>")
        continue
    elif re.match(r"^\d+\.\s", stripped):
        content = re.sub(r"^\d+\.\s", "", stripped)
        content = apply_inline(content)
        html_lines.append(f'<div style="margin-left:24px; margin-bottom:4px;">{content}</div>')
        continue
    else:
        if in_ul:
            html_lines.append("</ul>")
            in_ul = False

    # 見出し
    if stripped.startswith("#"):
        m = re.match(r"(#{1,6})\s+(.*)", stripped)
        if m:
            level = len(m.group(1))
            text = apply_inline(m.group(2))
            sizes = {1: "28px", 2: "24px", 3: "20px", 4: "17px", 5: "15px", 6: "14px"}
            margins = {1: "40px 0 16px", 2: "32px 0 12px", 3: "24px 0 10px", 4: "20px 0 8px"}
            color = "#1a1a2e" if level <= 2 else "#2C3E50"
            border = "border-bottom:2px solid #3498DB; padding-bottom:8px;" if level <= 2 else ""
            html_lines.append(f'<h{level} style="font-size:{sizes.get(level,"14px")}; margin:{margins.get(level,"16px 0 8px")}; color:{color}; {border}">{text}</h{level}>')
            continue

    # 水平線
    if stripped == "---":
        html_lines.append('<hr style="border:none; border-top:2px solid #eee; margin:32px 0;">')
        continue

    # img（既に変換済み）
    if stripped.startswith("<img"):
        html_lines.append(stripped)
        continue

    # 空行
    if not stripped:
        html_lines.append("")
        continue

    # 通常段落
    html_lines.append(f"<p>{apply_inline(stripped)}</p>")

if in_table:
    html_lines.append("</table>")
if in_ul:
    html_lines.append("</ul>")


# apply_inline を全行に再適用（テーブル以外の行）
final_lines = []
for line in html_lines:
    if not line.startswith("<t") and not line.startswith("<img"):
        line = apply_inline(line)
    final_lines.append(line)

# ── HTML組み立て ──────────────────────────────────────
html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CORE STEP クリエイティブ分析レポート</title>
<style>
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Hiragino Sans', 'Segoe UI', sans-serif;
    max-width: 900px;
    margin: 0 auto;
    padding: 40px 24px;
    line-height: 1.8;
    color: #333;
    background: #fff;
  }}
  p {{ margin: 8px 0; }}
  li {{ margin: 4px 0; }}
  strong {{ color: #1a1a2e; }}
  table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
  th {{ background: #2C3E50; color: white; }}
  td, th {{ padding: 10px 12px; border: 1px solid #ddd; text-align: center; font-size: 14px; }}
  tr:nth-child(even) td {{ background: #f9f9f9; }}
  img {{ max-width: 100%; }}
</style>
</head>
<body>
{chr(10).join(final_lines)}
</body>
</html>"""

OUT_PATH.write_text(html, encoding="utf-8")
print(f"HTML saved: {OUT_PATH}")
print(f"File size: {OUT_PATH.stat().st_size / 1024 / 1024:.1f} MB")
