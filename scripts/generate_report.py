#!/usr/bin/env python3
"""减肥勇士团 · RPG 战报生成器

Usage (由 openclaw 触发或手动运行):
    python3 scripts/generate_report.py                         # 今天的战报
    python3 scripts/generate_report.py 2026-03-02              # 指定日期
    python3 scripts/generate_report.py 2026-03-02 data.csv     # 指定日期+数据文件
"""
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Optional

# 确保能 import 同目录下的模块
sys.path.insert(0, str(Path(__file__).parent))

from config import DEFAULT_TEAM_NAME, DEFAULT_CSV, REPORTS_DIR
from data_loader import load_data, compute_person_stats, find_mvp
from renderer import (
    create_canvas,
    render_title,
    render_character_status,
    render_weight_trend,
    render_calorie_chart,
    render_footer,
)

import pandas as pd


def generate_report(
    csv_path: Optional[str] = None,
    target_date: Optional[date] = None,
    output_path: Optional[str] = None,
    team_name: str = DEFAULT_TEAM_NAME,
) -> Optional[str]:
    """生成 RPG 战报图片。返回输出文件路径。"""
    if csv_path is None:
        csv_path = str(DEFAULT_CSV)

    if target_date is None:
        target_date = date.today()

    if output_path is None:
        REPORTS_DIR.mkdir(exist_ok=True)
        output_path = str(REPORTS_DIR / f"report_{target_date.isoformat()}.png")

    # 1. 加载数据
    df = load_data(csv_path)
    names = df[df["date"] == pd.Timestamp(target_date)]["name"].unique().tolist()

    if not names:
        print(f"⚠️ 没有找到 {target_date} 的数据！")
        return None

    # 2. 计算每人统计数据
    stats_list = [compute_person_stats(df, name, target_date) for name in names]
    mvp = find_mvp(stats_list)

    # 3. 渲染
    img = create_canvas()
    render_title(img, team_name, stats_list[0]["day_number"], stats_list[0]["days_remaining"])
    render_character_status(img, stats_list)
    render_weight_trend(img, stats_list)
    render_calorie_chart(img, stats_list)
    render_footer(img, mvp, target_date)

    # 4. 保存
    img.save(output_path, "PNG", quality=95)
    print(f"✅ 战报已生成: {output_path}")
    return output_path


if __name__ == "__main__":
    target = None
    csv = None

    if len(sys.argv) >= 2:
        target = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
    if len(sys.argv) >= 3:
        csv = sys.argv[2]

    result = generate_report(csv_path=csv, target_date=target)
    if result:
        print(f"📂 文件位置: {result}")
