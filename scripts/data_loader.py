"""数据加载与统计计算模块"""
from datetime import date
from typing import Optional

import pandas as pd


def load_data(csv_path: str, target_date: Optional[date] = None) -> pd.DataFrame:
    """加载 CSV 数据，解析日期列。"""
    df = pd.read_csv(csv_path, encoding="utf-8")
    df["date"] = pd.to_datetime(df["date"])
    df["start_date"] = pd.to_datetime(df["start_date"])
    df["end_date"] = pd.to_datetime(df["end_date"])
    return df


def compute_person_stats(df: pd.DataFrame, name: str, target_date: date) -> dict:
    """计算指定日期某人的所有统计数据。"""
    target_ts = pd.Timestamp(target_date)
    person_df = df[df["name"] == name].sort_values("date")
    today_row = person_df[person_df["date"] == target_ts].iloc[0]

    weight = today_row["weight"]
    target_weight = today_row["target_weight"]
    start_weight = today_row["start_weight"]
    calories_in = int(today_row["calories_in"])
    calories_out = int(today_row["calories_out"])
    start_date = today_row["start_date"].date()
    end_date = today_row["end_date"].date()

    calorie_deficit = calories_in - calories_out

    yesterday = target_ts - pd.Timedelta(days=1)
    yesterday_rows = person_df[person_df["date"] == yesterday]
    if len(yesterday_rows) > 0:
        weight_change = round(weight - yesterday_rows.iloc[0]["weight"], 2)
    else:
        weight_change = 0.0

    total_to_lose = start_weight - target_weight
    lost_so_far = start_weight - weight
    progress = round(lost_so_far / total_to_lose, 4) if total_to_lose > 0 else 0.0

    day_number = (target_date - start_date).days
    days_remaining = (end_date - target_date).days

    history_df = person_df[person_df["date"] <= target_ts]
    weight_history = history_df["weight"].tolist()
    date_history = [d.date() for d in history_df["date"]]

    return {
        "name": name,
        "weight": weight,
        "target_weight": target_weight,
        "start_weight": start_weight,
        "calories_in": calories_in,
        "calories_out": calories_out,
        "calorie_deficit": calorie_deficit,
        "weight_change": weight_change,
        "progress": progress,
        "day_number": day_number,
        "days_remaining": days_remaining,
        "is_on_track": calorie_deficit <= 0,
        "weight_history": weight_history,
        "date_history": date_history,
        "start_date": start_date,
        "end_date": end_date,
    }


def find_mvp(stats_list: list[dict]) -> dict:
    """找到当日热量缺口最大（最负）的人。"""
    return min(stats_list, key=lambda s: s["calorie_deficit"])


def xp_for_level(level: int) -> int:
    """计算升到指定等级所需的经验值。LV.1=100, LV.2=150, 每级+50。"""
    return 100 + 50 * (level - 1)


def total_xp_for_level(level: int) -> int:
    """计算达到指定等级所需的累计总经验值。"""
    # sum of (100 + 50*(i-1)) for i=1..level
    return sum(xp_for_level(i) for i in range(1, level + 1))


def level_from_xp(xp: int) -> tuple[int, int, int]:
    """根据累计经验值计算等级。返回 (等级, 当前级已获得经验, 当前级所需经验)。"""
    level = 0
    remaining = xp
    while True:
        needed = xp_for_level(level + 1)
        if remaining < needed:
            return level, remaining, needed
        remaining -= needed
        level += 1


def compute_xp(df: pd.DataFrame, name: str, target_date: date) -> dict:
    """回溯历史数据，计算某人截至 target_date 的累计经验值和等级。

    规则:
    - 当天达标(消耗 > 摄入): +50 XP
    - 当天 MVP(缺口最大):    额外 +100 XP
    """
    target_ts = pd.Timestamp(target_date)
    all_names = df["name"].unique().tolist()
    person_df = df[df["name"] == name].sort_values("date")
    dates_up_to = person_df[person_df["date"] <= target_ts]["date"].unique()

    total_xp = 0
    for day_ts in sorted(dates_up_to):
        day = pd.Timestamp(day_ts)
        # 这一天此人的数据
        row = df[(df["name"] == name) & (df["date"] == day)]
        if row.empty:
            continue
        row = row.iloc[0]
        deficit = int(row["calories_in"]) - int(row["calories_out"])

        # 达标奖励
        if deficit <= 0:
            total_xp += 50

        # MVP 奖励: 比较这一天所有人的缺口
        day_deficits = {}
        for n in all_names:
            r = df[(df["name"] == n) & (df["date"] == day)]
            if not r.empty:
                r = r.iloc[0]
                day_deficits[n] = int(r["calories_in"]) - int(r["calories_out"])

        if day_deficits:
            mvp_name = min(day_deficits, key=day_deficits.get)
            if mvp_name == name:
                total_xp += 100

    level, level_xp, level_needed = level_from_xp(total_xp)
    return {
        "total_xp": total_xp,
        "level": level,
        "level_xp": level_xp,       # 当前级已获得
        "level_needed": level_needed,  # 当前级总共需要
    }
