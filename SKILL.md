---
name: weight-tracker
description: "生成 RPG 风格的减肥战报图片。用于：记录每日体重和热量数据、生成减肥战报、查看减肥进度、对比减肥成绩。触发词：减肥战报、体重记录、生成战报、减肥进度、热量统计、weight report、diet tracker。"
metadata:
  emoji: "⚔️"
  version: "1.0.0"
  requires:
    bins: ["python3"]
    pip: ["matplotlib", "Pillow", "pandas"]
allowed-tools: Bash(python3 *)
---

# 减肥勇士团 · RPG 战报生成器

生成可爱的 RPG 风格减肥战报图片，支持 2-3 人对比，方便在微信群分享。

## 快速开始

### 生成今日战报

```bash
cd ~/.clawdbot/workspace/.agents/skills/weight-tracker
python3 scripts/generate_report.py
```

### 生成指定日期战报

```bash
cd ~/.clawdbot/workspace/.agents/skills/weight-tracker
python3 scripts/generate_report.py 2026-03-02
```

### 使用自定义数据文件

```bash
cd ~/.clawdbot/workspace/.agents/skills/weight-tracker
python3 scripts/generate_report.py 2026-03-02 data/my_data.csv
```

输出路径: `reports/report_YYYY-MM-DD.png`

## 数据格式

数据存储在 `data/` 目录下的 CSV 文件中，默认文件为 `data/sample.csv`。

### CSV 字段

| 字段 | 含义 | 示例 |
|------|------|------|
| date | 记录日期 | 2026-03-02 |
| name | 昵称 | 小王子 |
| weight | 当日体重(kg) | 73.2 |
| calories_in | 当日摄入热量(kcal) | 1480 |
| calories_out | 当日消耗热量(kcal)，含基础代谢+运动 | 1800 |
| target_weight | 目标体重(kg) | 70 |
| start_weight | 起始体重(kg) | 75 |
| start_date | 开始日期 | 2026-02-15 |
| end_date | 截止日期 | 2026-04-01 |

### 示例 CSV

```csv
date,name,weight,calories_in,calories_out,target_weight,start_weight,start_date,end_date
2026-03-01,小王子,73.5,1480,1800,70,75,2026-02-15,2026-04-01
2026-03-01,小红,65.3,1200,1500,63,67,2026-02-15,2026-04-01
```

## 录入数据

帮用户在 CSV 文件末尾追加一行新记录。用户提供: 日期(默认今天)、姓名、体重、摄入热量、消耗热量。其余字段(target_weight, start_weight, start_date, end_date)从该用户之前的记录复制。

追加方式:
```bash
echo "2026-03-03,小王子,72.5,1450,1800,70,75,2026-02-15,2026-04-01" >> data/sample.csv
```

## 战报内容

生成的 PNG 图片 (800×1200) 包含:

1. **顶部标题栏** - 团队名 + 第N天 + 倒计时
2. **角色状态区** - 每人一行: 昵称、等级(=天数)、HP体重进度条、热量数据
3. **体重趋势图** - 多人折线对比 + 目标虚线
4. **热量对比柱状图** - 每人摄入 vs 消耗
5. **底部彩蛋区** - 今日MVP + 随机鼓励语

## 常见对话触发

- "帮我记录今天的体重和热量" → 追加 CSV 数据
- "生成今天的减肥战报" → 运行 generate_report.py
- "看看我们的减肥进度" → 生成战报并打开
- "小王子今天73kg，吃了1500卡，消耗1800卡" → 解析并追加数据，然后生成战报
