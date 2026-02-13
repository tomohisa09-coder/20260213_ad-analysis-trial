# Figure Guide v2（共通スタイル）

本ガイドは、プロジェクト横断で再現可能な図表スタイル・余白・注記・凡例・保存先命名の共通ルールをまとめたものです。特定の実装やコード構成（例: `src/final`）に依存せず、必要に応じて各プロジェクトで調整して利用してください。旧ガイド（FigureGuide_color.md）は参考資料とし、本ドキュメントを標準の推奨とします。

## 範囲と原則
- 対象: 本ガイドに準拠して作成する図表一般（KPIテーブル含む）
- 原則: 再現性と可読性を優先。各プロジェクトの要件に応じて調整可能
- 再現性: 保存パス/命名・倍率・注記形式を固定。例外運用は理由を記録

## 1) ディレクトリと命名規則
- ルート: `reports/figures/` 配下にレポート単位のフォルダを作成
  - 例: `reports/figures/11period_afp/`
  - 他レポートは `reports/figures/<report_slug>/`（ハイフン/アンダースコア可）
- ファイル命名: 実行順に 2桁連番 + 下線 + 説明（英小文字/数字/下線）
  - 例: `01_afp_market_impact_integrated.png`
  - 以降 `02_…`, `03A_…`, `03B_…` のように既存踏襲

## 2) ベーススタイル（共通）
- 図サイズ: `(16, 9)`、保存: `dpi=300`, `bbox_inches='tight'`
- フォント: `Hiragino Sans` → `DejaVu Sans` → `sans-serif` フォールバック
- 背景: seaborn `whitegrid`
- パレット: seaborn `husl`（12色）。ブランド指定色が入れば差し替え
- 軸/枠: `axes.linewidth=0.8`, `axes.edgecolor='black'`
- 目盛: `xtick.direction='in'`, `ytick.direction='in'`
- グリッド: y軸主体、`alpha=0.3`（全体rcは0.5/0.7だが各図で0.3に調整）
- タイトル: `pad=20`

推奨初期化（例）

```python
def setup_style(font_size: int = 16):
    import matplotlib.pyplot as plt, seaborn as sns
    sns.set_style("whitegrid")
    plt.rcParams['font.family'] = ['Hiragino Sans', 'DejaVu Sans', 'sans-serif']
    plt.rcParams['font.size'] = font_size
    plt.rcParams['figure.figsize'] = (16, 9)
    sns.set_palette("husl", 12)
    plt.rcParams['axes.linewidth'] = 0.8
    plt.rcParams['axes.edgecolor'] = 'black'
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    plt.rcParams['grid.linewidth'] = 0.5
    plt.rcParams['grid.alpha'] = 0.7
```

## 3) 注記・ラベル（値表示）
- バーや折れ線の値を棒・点の上に表示。重なり回避のため「しきい値 or 比率」のオフセット併用
- 書式と既定オフセット
  - 人・件: テキスト=`'{int(v)}人'` / `'{int(v)}件'`、オフセット=`max(1, v*0.05)`
  - %: テキスト=`'{v:.1f}%'`、オフセット=`max(0.5, v*0.03)`
  - 円: テキスト=`'¥{v:,.0f}'`、オフセット=`max(100, v*0.03)`
- 折れ線の注記: `xytext=(0, 10)` を基本、中心揃え
- フォント: デフォルト通常。03Aの主要ラベルは太字12pt（現行踏襲）

ユーティリティ例:
```python
def label_offset(v, unit):
    if unit == 'person' or unit == 'count':
        return max(1, v*0.05)
    if unit == 'percent':
        return max(0.5, v*0.03)
    if unit == 'yen':
        return max(100, v*0.03)
    return max(1, v*0.03)
```

## 4) 軸レンジ（上限マージン）
- 下限は 0 固定（KPIテーブルを除く）
- 上限は図種と注記密度に応じた倍率で最大値に余白を加える
  - 単純棒/折れ線＋注記あり: `1.35 × max`
  - 多系列バー（グループ）: `1.30 × max`
  - シンプル（注記少ない）: `1.20 × max`
  - トップ5等で注記密: `1.40 × max`
- 特例: 03A 上段（構成比3系列）は固定 `ylim=(0, 140)` を維持

ユーティリティ例:
```python
def set_ylim_with_margin(ax, vmax, kind='simple'):
    factors = {
        'simple': 1.20,
        'line': 1.35,
        'bar': 1.35,
        'grouped': 1.30,
        'dense': 1.40,
    }
    f = factors.get(kind, 1.30)
    ax.set_ylim(0, (vmax or 1) * f)
```

## 5) 凡例
- 原則位置: `upper right`
- フォントサイズ: 10（密な場合 8）
- 目標/平均線など補助線は凡例で明示（例: 04で平均線を凡例に表示）

## 6) 書式・単位
- yラベルに単位を併記（例: `売上金額（円）`, `割合（%）`, `新規顧客数（人）`）
- 桁区切り: 円は `¥{:,}`、人数・件数は `,` 区切り
- xラベルが長い場合は `rotation=45, ha='right'`

## 7) 図タイプ別の例（参考）
以下は適用イメージの一例です。必ずしもこの通りに作る必要はありません。目的・データ特性に合わせて本ガイドの原則内で調整してください。

- 市場インパクト系
  - シェア棒: `1.2×max`（%）、中央にサマリーテーブルを添える例
  - 売上推移（折れ線）: `1.3×max`、各点に金額注記
- 新規獲得系
  - 月次新規数（多系列バー）: `1.2×max`
  - 新規率（%比較）: `1.2×max`
  - 平均売上/新規売上合計: `1.2×max`
- 新規コホート・LTV系
  - 構成比3系列の例: 上段を `ylim=(0, 140)` に固定、ラベル太字12pt
  - 平均LTV: `1.35×max`
- 詳細分布系
  - ヒスト: `edgecolor='black'`, `alpha=0.7`、空きパネルは `axis('off')`
- 商品パフォーマンス系
  - 達成率/売上/ユーザー単価: `1.4×max`、100%破線・全体平均点線
  - 新規獲得率: `1.4×max`
- KPIテーブル系
  - ヘッダ青白、カテゴリ別背景色。大きめ表示例: `font_size=13`, `scale_y=3.2`

## 8) 保存手順（標準）
- 例:
```python
from pathlib import Path
out_dir = Path('reports/figures/<report_slug>')  # レポート用サブフォルダ
out = out_dir / '01_example_figure.png'         # 01からの連番命名
plt.savefig(out, dpi=300, bbox_inches='tight')
```
- レポートごとに `reports/figures/` 直下へ適切なサブフォルダを作成
- ファイル名は本ガイドの命名規則に合わせること

## 9) 品質チェックリスト
- 注記が枠・タイトル・凡例に干渉していない（倍率・オフセット確認）
- 単位・桁区切りが正しい
- 凡例位置・サイズが適切（右上/10pt、密なら8pt）
- 連番・保存先ディレクトリが正しい
- 再実行で完全上書きされる（固定命名）

## 10) 変更運用
- 定義・倍率・命名を変更する場合：
  1) 本ガイドと対象スクリプトを同時更新
  2) 影響する図の見え方を比較画像でレビュー
  3) 変更履歴を計画書/PRに明記

---
最終更新: v2（husl継続、保存先はレポート別サブフォルダ＋連番命名）。
