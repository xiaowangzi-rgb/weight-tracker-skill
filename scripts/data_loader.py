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
