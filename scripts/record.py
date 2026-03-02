#!/usr/bin/env python3
"""数据录入工具

Usage:
    # 录入一条记录（所有字段）
    python3 scripts/record.py add 2026-03-03 小王子 72.5 1450 1800 70 75 2026-02-15 2026-04-01

    # 简化录入（自动从历史记录补全 target_weight, start_weight, start_date, end_date）
    python3 scripts/record.py quick 小王子 72.5 1450 1800
    python3 scripts/record.py quick 小王子 72.5 1450 1800 2026-03-03  # 指定日期

    # 初始化新成员（设置目标信息）
    python3 scripts/record.py init 小王子 75 70 2026-02-15 2026-04-01

    # 查看当前所有成员
    python3 scripts/record.py members

    # 查看某人最近的记录
    python3 scripts/record.py history 小王子
"""
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import DEFAULT_CSV, CSV_HEADER, DATA_DIR


def _ensure_csv():
    """确保 records.csv 存在且有表头。"""
    DATA_DIR.mkdir(exist_ok=True)
    if not DEFAULT_CSV.exists() or DEFAULT_CSV.stat().st_size == 0:
        DEFAULT_CSV.write_text(CSV_HEADER + "\n", encoding="utf-8")
        print(f"✅ 已创建数据文件: {DEFAULT_CSV}")


def _read_lines() -> list[str]:
    """读取 CSV 所有行（去掉表头）。"""
    _ensure_csv()
    lines = DEFAULT_CSV.read_text(encoding="utf-8").strip().split("\n")
    return lines[1:] if len(lines) > 1 else []


def _get_person_latest(name: str) -> dict | None:
    """获取某人最近一条记录的元数据字段。"""
    lines = _read_lines()
    for line in reversed(lines):
        parts = line.split(",")
        if len(parts) >= 9 and parts[1] == name:
            return {
                "target_weight": parts[5],
                "start_weight": parts[6],
                "start_date": parts[7],
                "end_date": parts[8],
            }
    return None


def cmd_add(args: list[str]):
    """完整录入: date name weight cal_in cal_out target start start_date end_date"""
    if len(args) < 9:
        print("❌ 参数不足！需要: date name weight cal_in cal_out target_weight start_weight start_date end_date")
        return
    _ensure_csv()
    row = ",".join(args[:9])
    with open(DEFAULT_CSV, "a", encoding="utf-8") as f:
        f.write(row + "\n")
    print(f"✅ 已录入: {args[1]} {args[0]} 体重{args[2]}kg 摄入{args[3]}kcal 消耗{args[4]}kcal")


def cmd_quick(args: list[str]):
    """简化录入: name weight cal_in cal_out [date]"""
    if len(args) < 4:
        print("❌ 参数不足！需要: name weight cal_in cal_out [date]")
        return

    name, weight, cal_in, cal_out = args[0], args[1], args[2], args[3]
    record_date = args[4] if len(args) >= 5 else date.today().isoformat()

    latest = _get_person_latest(name)
    if latest is None:
        print(f"❌ 找不到 {name} 的历史记录！请先用 init 命令初始化：")
        print(f"   python3 scripts/record.py init {name} <起始体重> <目标体重> <开始日期> <截止日期>")
        return

    _ensure_csv()
    row = f"{record_date},{name},{weight},{cal_in},{cal_out},{latest['target_weight']},{latest['start_weight']},{latest['start_date']},{latest['end_date']}"
    with open(DEFAULT_CSV, "a", encoding="utf-8") as f:
        f.write(row + "\n")
    print(f"✅ 已录入: {name} {record_date} 体重{weight}kg 摄入{cal_in}kcal 消耗{cal_out}kcal")


def cmd_init(args: list[str]):
    """初始化新成员: name start_weight target_weight start_date end_date"""
    if len(args) < 5:
        print("❌ 参数不足！需要: name start_weight target_weight start_date end_date")
        return

    name, start_weight, target_weight, start_date, end_date = args[:5]
    _ensure_csv()

    # 写一条初始记录（当天，体重=起始体重，热量为0）
    row = f"{start_date},{name},{start_weight},0,0,{target_weight},{start_weight},{start_date},{end_date}"
    with open(DEFAULT_CSV, "a", encoding="utf-8") as f:
        f.write(row + "\n")
    print(f"✅ 已初始化成员: {name} (起始{start_weight}kg → 目标{target_weight}kg, {start_date}~{end_date})")


def cmd_members(args: list[str]):
    """列出所有成员和最近记录。"""
    lines = _read_lines()
    if not lines:
        print("📭 还没有任何记录。")
        return

    members = {}
    for line in lines:
        parts = line.split(",")
        if len(parts) >= 9:
            name = parts[1]
            members[name] = {
                "date": parts[0],
                "weight": parts[2],
                "target": parts[5],
                "start": parts[6],
            }

    print("👥 当前成员：")
    for name, info in members.items():
        print(f"   {name}: 最近 {info['date']} 体重 {info['weight']}kg ({info['start']}→{info['target']}kg)")


def cmd_history(args: list[str]):
    """查看某人的记录历史。"""
    if len(args) < 1:
        print("❌ 请指定姓名！")
        return

    name = args[0]
    lines = _read_lines()
    records = [l for l in lines if l.split(",")[1] == name]

    if not records:
        print(f"📭 没有找到 {name} 的记录。")
        return

    print(f"📋 {name} 的记录 ({len(records)}条)：")
    print(f"   {'日期':<12} {'体重':>6} {'摄入':>6} {'消耗':>6} {'缺口':>6}")
    for line in records:
        p = line.split(",")
        deficit = int(p[3]) - int(p[4]) if int(p[3]) > 0 else "—"
        print(f"   {p[0]:<12} {p[2]:>5}kg {p[3]:>5} {p[4]:>5} {str(deficit):>5}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    command = sys.argv[1]
    rest = sys.argv[2:]

    commands = {
        "add": cmd_add,
        "quick": cmd_quick,
        "init": cmd_init,
        "members": cmd_members,
        "history": cmd_history,
    }

    if command in commands:
        commands[command](rest)
    else:
        print(f"❌ 未知命令: {command}")
        print(f"可用命令: {', '.join(commands.keys())}")
