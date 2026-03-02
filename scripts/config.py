"""RPG 战报配置常量"""
from pathlib import Path

# === 路径 ===
SKILL_DIR = Path(__file__).parent.parent  # weight-tracker/ 根目录
DATA_DIR = SKILL_DIR / "data"
REPORTS_DIR = SKILL_DIR / "reports"
DEFAULT_CSV = DATA_DIR / "sample.csv"

# === 图片尺寸 ===
IMAGE_WIDTH = 800
IMAGE_HEIGHT = 1200

# === 配色方案 (RGB tuples) ===
BG_COLOR_TOP = (26, 26, 46)       # #1a1a2e
BG_COLOR_BOTTOM = (22, 33, 62)    # #16213e
COLOR_GOLD = (255, 215, 0)        # #ffd700 标题
COLOR_WHITE = (255, 255, 255)     # #ffffff 正文
COLOR_GREEN = (0, 255, 136)       # #00ff88 达标
COLOR_RED = (255, 71, 87)         # #ff4757 超标
COLOR_BAR_BG = (51, 51, 85)      # #333355 进度条背景
COLOR_DIVIDER = (255, 255, 255, 51)  # 半透明白 分割线

# matplotlib 颜色 (hex)
CHART_BG = "none"
CHART_COLORS = ["#00ff88", "#ff6b9d", "#00d4ff"]  # 每人一个颜色
CHART_TEXT_COLOR = "#ffffff"
CHART_GRID_COLOR = "#333355"

# === 布局 (y坐标, 高度占比) ===
LAYOUT = {
    "title":    {"y": 0,    "h": 0.10},  # 顶部标题栏
    "status":   {"y": 0.10, "h": 0.38},  # 角色状态区
    "trend":    {"y": 0.48, "h": 0.24},  # 体重趋势图
    "calories": {"y": 0.72, "h": 0.16},  # 热量对比柱状图
    "footer":   {"y": 0.88, "h": 0.12},  # 底部彩蛋区
}

# === 角色标记 (按顺序分配) ===
AVATARS = ["[壹]", "[贰]", "[叁]"]

# === 鼓励语列表 ===
ENCOURAGEMENTS = [
    "每一次忍住不吃夜宵，都是一次胜利！",
    "今天的汗水，是明天的轻盈！",
    "管住嘴迈开腿，明天更美！",
    "坚持就是胜利，你们是最棒的！",
    "减肥不是目的，健康才是终点！",
    "每一步都算数，继续加油！",
    "你的身体正在悄悄变好！",
    "自律给我自由！",
    "夏天的衣服已经在等你了！",
    "比昨天好一点点，就够了！",
]

# === 团队默认名称 ===
DEFAULT_TEAM_NAME = "减肥勇士团"
