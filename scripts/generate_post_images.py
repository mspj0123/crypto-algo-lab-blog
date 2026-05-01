"""
ブログ記事用グラフ画像を生成するスクリプト。
assets/images/ に PNG ファイルを出力する。
"""

import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# 日本語フォント設定（環境に応じて変更）
import matplotlib.font_manager as fm

def _setup_japanese_font():
    """利用可能な日本語フォントを設定する。"""
    candidates = [
        "Noto Sans CJK JP", "Noto Sans JP",
        "IPAexGothic", "IPAGothic", "TakaoGothic",
        "Hiragino Sans", "Yu Gothic", "Meiryo",
        "DejaVu Sans",  # フォールバック
    ]
    available = {f.name for f in fm.fontManager.ttflist}
    for font in candidates:
        if font in available:
            plt.rcParams["font.family"] = font
            return font
    return "DejaVu Sans"

FONT = _setup_japanese_font()
print(f"使用フォント: {FONT}")

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "images")
os.makedirs(OUT_DIR, exist_ok=True)

# カラーパレット（note.com / Zenn 風）
BLUE  = "#0066cc"
LIGHT = "#e8f0fe"
GREEN = "#00aa66"
RED   = "#cc3333"
GRAY  = "#f5f5f5"
TEXT  = "#1a1a2e"


def save(fig, filename: str):
    path = os.path.join(OUT_DIR, filename)
    fig.savefig(path, dpi=150, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close(fig)
    print(f"  保存: {filename}")


# -----------------------------------------------
# 1. ML フィルター 勝率比較
# -----------------------------------------------
def chart_ml_winrate():
    fig, ax = plt.subplots(figsize=(8, 4.5))
    fig.patch.set_facecolor("white")

    labels = ["フィルターなし\n(5ペア)", "MLフィルターあり"]
    values = [40, 87.5]
    colors = [RED, GREEN]

    bars = ax.bar(labels, values, color=colors, width=0.45,
                  edgecolor="white", linewidth=2, zorder=3)

    # 値ラベル
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 1.5,
                f"{val}%", ha="center", va="bottom",
                fontsize=16, fontweight="bold", color=TEXT)

    # 基準線
    ax.axhline(50, color="#aaa", linestyle="--", linewidth=1, zorder=2)
    ax.text(1.28, 51, "勝率50%ライン", fontsize=9, color="#888")

    ax.set_ylim(0, 100)
    ax.set_ylabel("勝率 (%)", fontsize=11, color=TEXT)
    ax.set_title("LightGBMフィルター 勝率比較", fontsize=14,
                 fontweight="bold", color=TEXT, pad=14)
    ax.set_facecolor(GRAY)
    ax.grid(axis="y", color="white", linewidth=1.5, zorder=1)
    ax.spines[:].set_visible(False)
    ax.tick_params(colors=TEXT, labelsize=11)

    fig.tight_layout()
    save(fig, "ml-filter-winrate.png")


# -----------------------------------------------
# 2. ML フィルター 損益比較
# -----------------------------------------------
def chart_ml_pnl():
    fig, ax = plt.subplots(figsize=(8, 4.5))
    fig.patch.set_facecolor("white")

    labels = ["フィルターなし\n(5ペア)", "MLフィルターあり"]
    values = [-9053, 8276]
    colors = [RED, GREEN]

    bars = ax.bar(labels, values, color=colors, width=0.45,
                  edgecolor="white", linewidth=2, zorder=3)

    for bar, val in zip(bars, values):
        y = val + 200 if val >= 0 else val - 600
        label = f"+{val:,}円" if val >= 0 else f"{val:,}円"
        ax.text(bar.get_x() + bar.get_width() / 2, y,
                label, ha="center", va="bottom",
                fontsize=14, fontweight="bold", color=TEXT)

    ax.axhline(0, color=TEXT, linewidth=1, zorder=4)
    ax.set_ylabel("損益 (円)", fontsize=11, color=TEXT)
    ax.set_title("LightGBMフィルター 損益比較（初期資金10万円）",
                 fontsize=13, fontweight="bold", color=TEXT, pad=14)
    ax.set_facecolor(GRAY)
    ax.grid(axis="y", color="white", linewidth=1.5, zorder=1)
    ax.spines[:].set_visible(False)
    ax.tick_params(colors=TEXT, labelsize=11)

    fig.tight_layout()
    save(fig, "ml-filter-pnl.png")


# -----------------------------------------------
# 3. トレンドフィルター 足種比較（損益）
# -----------------------------------------------
def chart_trend_pnl():
    fig, ax = plt.subplots(figsize=(9, 5))
    fig.patch.set_facecolor("white")

    labels = ["フィルター\nなし", "4時間足\nEMA200", "2時間足\nEMA200", "1時間足\nEMA200"]
    values = [0, 15975, 41863, 41447]
    colors = [GRAY, "#4488cc", GREEN, "#66aadd"]
    edge   = [TEXT, BLUE, "#008855", "#4488cc"]

    bars = ax.bar(labels, values, color=colors, width=0.5,
                  edgecolor=edge, linewidth=2, zorder=3)

    for bar, val in zip(bars, values):
        label = f"+{val:,}円" if val > 0 else "—"
        ax.text(bar.get_x() + bar.get_width() / 2,
                val + 400, label,
                ha="center", va="bottom",
                fontsize=12, fontweight="bold", color=TEXT)

    ax.set_ylim(0, 48000)
    ax.set_ylabel("損益 (円)", fontsize=11, color=TEXT)
    ax.set_title("トレンドフィルター 足種別 損益比較（過去3ヶ月 BTC/JPY）",
                 fontsize=13, fontweight="bold", color=TEXT, pad=14)
    ax.set_facecolor(GRAY)
    ax.grid(axis="y", color="white", linewidth=1.5, zorder=1)
    ax.spines[:].set_visible(False)
    ax.tick_params(colors=TEXT, labelsize=11)

    # 最良マーク
    best_idx = values.index(max(values))
    ax.annotate("最良", xy=(best_idx, max(values) + 400),
                xytext=(best_idx + 0.5, max(values) + 4000),
                fontsize=10, color=GREEN, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=GREEN, lw=1.5))

    fig.tight_layout()
    save(fig, "trend-filter-pnl.png")


# -----------------------------------------------
# 4. ウォークフォワード検証（レーダーチャート的な比較）
# -----------------------------------------------
def chart_walkforward():
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
    fig.patch.set_facecolor("white")

    # 勝率
    ax1 = axes[0]
    ax1.bar(["フィルターなし", "MLフィルターあり"],
            [46.2, 72.5], color=[RED, GREEN], width=0.45,
            edgecolor="white", linewidth=2, zorder=3)
    ax1.set_title("勝率 (%)", fontsize=12, fontweight="bold", color=TEXT)
    ax1.set_ylim(0, 90)
    ax1.axhline(50, color="#aaa", linestyle="--", linewidth=1)
    for i, v in enumerate([46.2, 72.5]):
        ax1.text(i, v + 1.5, f"{v}%", ha="center", fontsize=13,
                 fontweight="bold", color=TEXT)
    ax1.set_facecolor(GRAY)
    ax1.grid(axis="y", color="white", linewidth=1.5, zorder=1)
    ax1.spines[:].set_visible(False)
    ax1.tick_params(colors=TEXT, labelsize=9)

    # PF
    ax2 = axes[1]
    ax2.bar(["フィルターなし", "MLフィルターあり"],
            [2.05, 4.95], color=[RED, GREEN], width=0.45,
            edgecolor="white", linewidth=2, zorder=3)
    ax2.set_title("プロフィットファクター", fontsize=12, fontweight="bold", color=TEXT)
    ax2.set_ylim(0, 6.5)
    ax2.axhline(1.0, color="#aaa", linestyle="--", linewidth=1)
    for i, v in enumerate([2.05, 4.95]):
        ax2.text(i, v + 0.08, f"{v}", ha="center", fontsize=13,
                 fontweight="bold", color=TEXT)
    ax2.set_facecolor(GRAY)
    ax2.grid(axis="y", color="white", linewidth=1.5, zorder=1)
    ax2.spines[:].set_visible(False)
    ax2.tick_params(colors=TEXT, labelsize=9)

    fig.suptitle("ウォークフォワード検証結果", fontsize=14,
                 fontweight="bold", color=TEXT, y=1.02)
    fig.tight_layout()
    save(fig, "walkforward-result.png")


if __name__ == "__main__":
    print("グラフ画像を生成中...")
    chart_ml_winrate()
    chart_ml_pnl()
    chart_trend_pnl()
    chart_walkforward()
    print(f"\n完了: {OUT_DIR} に4枚生成しました")
