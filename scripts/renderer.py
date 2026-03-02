"""RPG 战报渲染器"""
import io
import random
from datetime import date
from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Configure matplotlib to use CJK font
_CJK_FONT_PATHS = [
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
]
for _fp in _CJK_FONT_PATHS:
    if Path(_fp).exists():
        _cjk_font = fm.FontProperties(fname=_fp)
        plt.rcParams["font.family"] = _cjk_font.get_name()
        # Register for matplotlib
        fm.fontManager.addfont(_fp)
        plt.rcParams["font.sans-serif"] = [_cjk_font.get_name()] + plt.rcParams.get("font.sans-serif", [])
        break

plt.rcParams["axes.unicode_minus"] = False  # Fix minus sign display

from config import (
    IMAGE_WIDTH, IMAGE_HEIGHT,
    BG_COLOR_TOP, BG_COLOR_BOTTOM,
    COLOR_GOLD, COLOR_WHITE, COLOR_GREEN, COLOR_RED,
    COLOR_BAR_BG, COLOR_DIVIDER,
    CHART_COLORS, CHART_TEXT_COLOR, CHART_GRID_COLOR,
    LAYOUT, AVATARS, ENCOURAGEMENTS, DEFAULT_TEAM_NAME,
)


def _get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """获取支持中文的字体。优先系统字体，回退到默认。"""
    font_candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    ]
    for font_path in font_candidates:
        try:
            return ImageFont.truetype(font_path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def create_canvas() -> Image.Image:
    """创建带渐变背景的画布。"""
    img = Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT))
    draw = ImageDraw.Draw(img)

    for y in range(IMAGE_HEIGHT):
        ratio = y / IMAGE_HEIGHT
        r = int(BG_COLOR_TOP[0] + (BG_COLOR_BOTTOM[0] - BG_COLOR_TOP[0]) * ratio)
        g = int(BG_COLOR_TOP[1] + (BG_COLOR_BOTTOM[1] - BG_COLOR_TOP[1]) * ratio)
        b = int(BG_COLOR_TOP[2] + (BG_COLOR_BOTTOM[2] - BG_COLOR_TOP[2]) * ratio)
        draw.line([(0, y), (IMAGE_WIDTH, y)], fill=(r, g, b))

    return img


def render_title(img: Image.Image, team_name: str, day_number: int, days_remaining: int):
    """渲染顶部标题栏。"""
    draw = ImageDraw.Draw(img)
    layout = LAYOUT["title"]
    y_start = int(layout["y"] * IMAGE_HEIGHT)

    font_title = _get_font(32, bold=True)
    title_text = f"{team_name} · 第{day_number}天战报"
    bbox = draw.textbbox((0, 0), title_text, font=font_title)
    text_w = bbox[2] - bbox[0]
    x = (IMAGE_WIDTH - text_w) // 2
    draw.text((x, y_start + 20), title_text, fill=COLOR_GOLD, font=font_title)

    font_sub = _get_font(22)
    sub_text = f"距离决战还有 {days_remaining} 天"
    bbox = draw.textbbox((0, 0), sub_text, font=font_sub)
    text_w = bbox[2] - bbox[0]
    x = (IMAGE_WIDTH - text_w) // 2
    draw.text((x, y_start + 65), sub_text, fill=COLOR_WHITE, font=font_sub)

    line_y = y_start + int(layout["h"] * IMAGE_HEIGHT) - 5
    draw.line([(40, line_y), (IMAGE_WIDTH - 40, line_y)], fill=(255, 255, 255, 51), width=1)


def _draw_progress_bar(draw: ImageDraw.Draw, x: int, y: int, width: int, height: int,
                       progress: float, color: tuple):
    """绘制 HP 风格进度条。"""
    draw.rounded_rectangle([(x, y), (x + width, y + height)], radius=height // 2, fill=COLOR_BAR_BG)
    fill_width = max(int(width * min(progress, 1.0)), height)
    draw.rounded_rectangle([(x, y), (x + fill_width, y + height)], radius=height // 2, fill=color)


def render_character_status(img: Image.Image, stats_list: list[dict]):
    """渲染角色状态区：每人一行，HP 进度条 + 热量数据。"""
    draw = ImageDraw.Draw(img)
    layout = LAYOUT["status"]
    y_start = int(layout["y"] * IMAGE_HEIGHT)
    area_height = int(layout["h"] * IMAGE_HEIGHT)

    n = len(stats_list)
    person_height = area_height // max(n, 1)
    left_margin = 50
    bar_width = IMAGE_WIDTH - left_margin - 50 - 200

    font_name = _get_font(24, bold=True)
    font_data = _get_font(18)
    font_small = _get_font(15)

    for i, stats in enumerate(stats_list):
        y = y_start + i * person_height + 10
        avatar = AVATARS[i % len(AVATARS)]
        color = tuple(int(CHART_COLORS[i % len(CHART_COLORS)].lstrip("#")[j:j+2], 16) for j in (0, 2, 4))

        # 昵称 + 等级 + 经验值
        level = stats.get("level", 0)
        level_xp = stats.get("level_xp", 0)
        level_needed = stats.get("level_needed", 100)
        total_xp = stats.get("total_xp", 0)
        name_text = f"{avatar} {stats['name']}  LV.{level}  ({total_xp}XP)"
        draw.text((left_margin, y), name_text, fill=COLOR_GOLD, font=font_name)

        bar_y = y + 35
        _draw_progress_bar(draw, left_margin, bar_y, bar_width, 20, stats["progress"], color)

        weight_text = f"{stats['weight']}→{stats['target_weight']}kg"
        draw.text((left_margin + bar_width + 10, bar_y), weight_text, fill=COLOR_WHITE, font=font_data)

        pct = int(stats["progress"] * 100)
        change = stats["weight_change"]
        arrow = "↓" if change < 0 else "↑" if change > 0 else "→"
        change_color = COLOR_GREEN if change <= 0 else COLOR_RED
        progress_text = f"   进度: {pct}%  {arrow}{abs(change):.1f}kg(较昨日)"
        draw.text((left_margin, bar_y + 25), progress_text, fill=change_color, font=font_small)

        cal_y = bar_y + 50
        cal_text = f"消耗 {stats['calories_out']}kcal   摄入 {stats['calories_in']}kcal"
        draw.text((left_margin, cal_y), cal_text, fill=COLOR_WHITE, font=font_data)

        deficit = stats["calorie_deficit"]
        deficit_y = cal_y + 28
        if deficit <= 0:
            deficit_text = f"热量缺口 {deficit}kcal  达标！"
            draw.text((left_margin, deficit_y), deficit_text, fill=COLOR_GREEN, font=font_data)
        else:
            deficit_text = f"热量盈余 +{deficit}kcal  注意控制！"
            draw.text((left_margin, deficit_y), deficit_text, fill=COLOR_RED, font=font_data)

        if i < n - 1:
            line_y = y + person_height - 5
            draw.line([(40, line_y), (IMAGE_WIDTH - 40, line_y)], fill=(255, 255, 255, 40), width=1)


def render_weight_trend(img: Image.Image, stats_list: list[dict]):
    """渲染体重趋势折线图 (matplotlib → Pillow)。"""
    layout = LAYOUT["trend"]
    y_start = int(layout["y"] * IMAGE_HEIGHT)
    area_height = int(layout["h"] * IMAGE_HEIGHT)

    fig_w = IMAGE_WIDTH / 100
    fig_h = area_height / 100
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=100)
    fig.patch.set_alpha(0.0)
    ax.set_facecolor("none")

    for i, stats in enumerate(stats_list):
        color = CHART_COLORS[i % len(CHART_COLORS)]
        dates = stats["date_history"]
        weights = stats["weight_history"]
        ax.plot(dates, weights, color=color, linewidth=2, marker="o", markersize=4,
                label=f"{stats['name']}")
        if dates:
            ax.axhline(y=stats["target_weight"], color=color, linestyle="--",
                       alpha=0.5, linewidth=1, label=f"{stats['name']}目标")

    ax.set_ylabel("体重 (kg)", color=CHART_TEXT_COLOR, fontsize=10)
    ax.tick_params(colors=CHART_TEXT_COLOR, labelsize=8)
    ax.grid(True, color=CHART_GRID_COLOR, alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_color(CHART_GRID_COLOR)
    ax.spines["left"].set_color(CHART_GRID_COLOR)
    fig.autofmt_xdate(rotation=30)
    ax.legend(loc="upper right", fontsize=8, facecolor="none",
              edgecolor="none", labelcolor=CHART_TEXT_COLOR)
    ax.set_title("体重趋势", color=CHART_TEXT_COLOR, fontsize=14, pad=10)
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", transparent=True, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    chart_img = Image.open(buf).convert("RGBA")
    chart_img = chart_img.resize((IMAGE_WIDTH - 20, area_height), Image.LANCZOS)
    img.paste(chart_img, (10, y_start), chart_img)


def render_calorie_chart(img: Image.Image, stats_list: list[dict]):
    """渲染热量摄入 vs 消耗柱状图。"""
    layout = LAYOUT["calories"]
    y_start = int(layout["y"] * IMAGE_HEIGHT)
    area_height = int(layout["h"] * IMAGE_HEIGHT)

    fig_w = IMAGE_WIDTH / 100
    fig_h = area_height / 100
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=100)
    fig.patch.set_alpha(0.0)
    ax.set_facecolor("none")

    names = [s["name"] for s in stats_list]
    x = np.arange(len(names))
    bar_width = 0.35

    cal_in = [s["calories_in"] for s in stats_list]
    cal_out = [s["calories_out"] for s in stats_list]

    bars_in = ax.bar(x - bar_width / 2, cal_in, bar_width, label="摄入",
                     color="#ff6b9d", alpha=0.85)
    bars_out = ax.bar(x + bar_width / 2, cal_out, bar_width, label="消耗",
                      color="#00ff88", alpha=0.85)

    for bar in bars_in:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 20,
                f"{int(bar.get_height())}", ha="center", va="bottom",
                color=CHART_TEXT_COLOR, fontsize=9)
    for bar in bars_out:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 20,
                f"{int(bar.get_height())}", ha="center", va="bottom",
                color=CHART_TEXT_COLOR, fontsize=9)

    ax.set_xticks(x)
    ax.set_xticklabels(names, color=CHART_TEXT_COLOR, fontsize=10)
    ax.tick_params(colors=CHART_TEXT_COLOR, labelsize=8)
    ax.set_ylabel("热量 (kcal)", color=CHART_TEXT_COLOR, fontsize=10)
    ax.grid(True, axis="y", color=CHART_GRID_COLOR, alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_color(CHART_GRID_COLOR)
    ax.spines["left"].set_color(CHART_GRID_COLOR)
    ax.legend(loc="upper left", fontsize=9, facecolor="none",
              edgecolor="none", labelcolor=CHART_TEXT_COLOR)
    ax.set_title("今日热量对比", color=CHART_TEXT_COLOR, fontsize=14, pad=10)
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", transparent=True, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    chart_img = Image.open(buf).convert("RGBA")
    chart_img = chart_img.resize((IMAGE_WIDTH - 20, area_height), Image.LANCZOS)
    img.paste(chart_img, (10, y_start), chart_img)


def render_footer(img: Image.Image, mvp: dict, report_date: date):
    """渲染底部 MVP + 鼓励语 + 日期。"""
    draw = ImageDraw.Draw(img)
    layout = LAYOUT["footer"]
    y_start = int(layout["y"] * IMAGE_HEIGHT)

    font_mvp = _get_font(22, bold=True)
    font_quote = _get_font(18)
    font_date = _get_font(16)

    draw.line([(40, y_start), (IMAGE_WIDTH - 40, y_start)], fill=(255, 255, 255, 40), width=1)

    deficit = mvp["calorie_deficit"]
    mvp_text = f"★ 今日MVP: {mvp['name']} (热量缺口 {deficit}kcal！)"
    bbox = draw.textbbox((0, 0), mvp_text, font=font_mvp)
    text_w = bbox[2] - bbox[0]
    x = (IMAGE_WIDTH - text_w) // 2
    draw.text((x, y_start + 15), mvp_text, fill=COLOR_GOLD, font=font_mvp)

    quote = random.choice(ENCOURAGEMENTS)
    quote_text = f'"{quote}"'
    bbox = draw.textbbox((0, 0), quote_text, font=font_quote)
    text_w = bbox[2] - bbox[0]
    x = (IMAGE_WIDTH - text_w) // 2
    draw.text((x, y_start + 55), quote_text, fill=COLOR_WHITE, font=font_quote)

    date_text = f"{report_date.year}年{report_date.month}月{report_date.day}日"
    bbox = draw.textbbox((0, 0), date_text, font=font_date)
    text_w = bbox[2] - bbox[0]
    x = (IMAGE_WIDTH - text_w) // 2
    draw.text((x, y_start + 90), date_text, fill=(200, 200, 200), font=font_date)
