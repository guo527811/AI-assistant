"""作业1：导出 4 周知识体系图为 JPG，保存到桌面"""
from PIL import Image, ImageDraw, ImageFont
import textwrap

# ── 配置 ──────────────────────────────────────
WIDTH = 1200
FONT_PATH = "C:/Windows/Fonts/msyh.ttc"
FONT_BOLD_PATH = "C:/Windows/Fonts/msyhbd.ttc"
OUTPUT = "C:/Users/lenovo/Desktop/知识体系图-4周学习路线.jpg"

# 配色
BG = "#0d1117"          # GitHub 暗色背景
CARD_BG = "#161b22"     # 卡片背景
ACCENT1 = "#58a6ff"     # 蓝（第1周）
ACCENT2 = "#3fb950"     # 绿（第2周）
ACCENT3 = "#d2991d"     # 黄（第3周）
ACCENT4 = "#f78166"     # 橙（第4周）
ACCENT_BOTTOM = "#bc8cff"  # 紫（串联线）
TEXT_WHITE = "#e6edf3"
TEXT_GRAY = "#8b949e"
TEXT_DIM = "#6e7681"

# ── 内容数据 ──────────────────────────────────
WEEKS = [
    {
        "title": "第1周 · 地基（6/3~6/8）",
        "color": ACCENT1,
        "items": [
            ("🔰 Claude Code 是什么", "不是\"聊天工具\"，是\"Agent 运行环境\""),
            ("🔰 Agent 是什么", "Agent = LLM + Planning + Memory + ToolUse + Feedback"),
            ("🔰 三秘书系统 = Multi-Agent 实战", "新闻秘书 → 搜索·简报·邮件 / 学习秘书 → 教程·笔记 / 找工作秘书 → 岗位·JD"),
            ("🔰 三大扩展体系", "Hooks（自动化触发器）+ Skills（可复用模块）+ Workflows（多步骤编排）"),
            ("🔰 MCP 协议初识", "MCP = AI 调用外部工具的\"USB 接口标准\""),
        ]
    },
    {
        "title": "第2周 · 深入（6/18）",
        "color": ACCENT2,
        "items": [
            ("🔧 MCP Server 开发实操", "从\"知道 MCP\"到\"自己写 MCP Server\" — FastMCP 5 行代码起服务"),
            ("🔧 Dynamic Workflows", "pipeline() / parallel() / 循环搜索模式"),
            ("⚠️ 发现能力缺口", "FastAPI（60%岗位要求）| Dify（越来越多 JD 中出现）"),
        ]
    },
    {
        "title": "第3周 · 核心能力爆发（6/22~6/26）",
        "color": ACCENT3,
        "items": [
            ("📝 提示工程五件套", "Role → Task → Constraints → Format → Examples — 让 AI 输出稳定可控"),
            ("📝 Loop Engineering", "从\"一次写对\"到\"写→检查→修正→再写\"循环 — 2026 最热方向"),
            ("🧠 AI Agent 五组件逐拆", "LLM（大脑）| Planning（规划）| Memory（记忆）| ToolUse（手脚）| Feedback（反馈）"),
            ("🛠️ Claude Code 五大核心原语", "Subagents · Commands · Skills · Hooks · Memory — 打通才敢说\"会用\""),
            ("📐 CLAUDE.md 优化", "从 27 行 → 90 行：加 IMPORTANT + 示例 + 踩坑记录 + 命令速查"),
            ("🌐 FastAPI + RAG API", "RAG 管道封装为 REST API → 简历从\"会用\"升级为\"独立开发\""),
        ]
    },
    {
        "title": "第4周 · 面试整合（6/29）",
        "color": ACCENT4,
        "items": [
            ("🎯 Agent SDK 六月新变化", "Managed Agents 托管范式 · SDK 从 CLI 升级为可编程框架"),
            ("🚀 MCP 生产部署", "STDIO → Streamable HTTP + Docker + Bearer Token · \"从玩具到生产\""),
            ("🎤 面试知识体系", "叙事公式：身份 + 核心能力 + 代表项目 + 学习路径 · TOP 5 必答题"),
        ]
    },
]

# 串联线内容
THREAD_LINE = [
    "第1步 → 发现 Claude Code 可以当 Agent 用 → 做三秘书系统 → 发现就是 Multi-Agent！",
    "第2步 → 想让 Agent 更好 → 学 Hooks/Skills/Workflows → 想调外部工具 → 学 MCP",
    "第3步 → 想输出更稳定 → 学提示工程五件套 → 想自动纠错 → 学 Loop Engineering",
    "第4步 → 想系统理解 → 拆五组件架构 → 想产品化 → 封装 RAG API → 找工作了！",
]

SKILLS = [
    ("LLM 基础", "🟢 80%", ACCENT1),
    ("提示工程", "🟢 85%", ACCENT1),
    ("Agent 架构", "🟢 85%", ACCENT1),
    ("MCP 工具系统", "🟡 70%", ACCENT3),
    ("RAG 知识库", "🟡 70%", ACCENT3),
    ("Claude Code 配置", "🟢 80%", ACCENT1),
    ("部署运维", "🟡 50%", ACCENT4),
    ("面试叙事", "🟢 80%", ACCENT1),
]

NEXT_STEPS = [
    "P0 急需：FastAPI 实战项目（覆盖 60% 岗位 Web 要求）",
    "P1 本周：Dify 平台实操（越来越硬性要求）",
    "P2 持续：用三秘书经验刷新简历",
    "P3 准备：把知识体系转化为面试回答",
]

# ── 计算总高度 ─────────────────────────────────
HEADER_H = 90
WEEK_HEADER_H = 44
ITEM_H = 32
SECTION_GAP = 20
PADDING = 24
# 每个 Week 卡片高度
week_heights = [WEEK_HEADER_H + len(w["items"]) * ITEM_H + PADDING * 2 for w in WEEKS]
thread_h = 44 * len(THREAD_LINE) + 80   # 串联线区域
skill_h = 44 * len(SKILLS) + 80         # 掌握度区域
next_h = 44 * len(NEXT_STEPS) + 80      # 下一步区域
HEIGHT = HEADER_H + sum(week_heights) + SECTION_GAP * 3 + thread_h + skill_h + next_h + 60

# ── 创建画布 ──────────────────────────────────
img = Image.new("RGB", (WIDTH, HEIGHT), BG)
draw = ImageDraw.Draw(img)

# 加载字体
try:
    font_title = ImageFont.truetype(FONT_BOLD_PATH, 32)
    font_subtitle = ImageFont.truetype(FONT_PATH, 16)
    font_week = ImageFont.truetype(FONT_BOLD_PATH, 20)
    font_item_title = ImageFont.truetype(FONT_BOLD_PATH, 15)
    font_item = ImageFont.truetype(FONT_PATH, 14)
    font_small = ImageFont.truetype(FONT_PATH, 13)
    font_skill_title = ImageFont.truetype(FONT_BOLD_PATH, 18)
except:
    font_title = ImageFont.load_default()
    font_subtitle = font_week = font_item_title = font_item = font_small = font_title

# ── 辅助函数 ──────────────────────────────────
def draw_rounded_rect(draw, xy, radius, fill, outline=None):
    """画圆角矩形"""
    from PIL import ImageDraw as ID
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline)

def draw_text_with_shadow(draw, xy, text, font, fill):
    """带阴影的文字"""
    x, y = xy
    draw.text((x+1, y+1), text, font=font, fill="#00000044")
    draw.text((x, y), text, font=font, fill=fill)

def draw_left_accent(draw, x, y, h, color):
    """画左侧色条"""
    draw.rectangle([x, y, x + 4, y + h], fill=color)

# ═══════════════════════════════════════════════
# 绘制阶段
# ═══════════════════════════════════════════════

y = 20

# ── 顶部标题 ──────────────────────────────────
draw_text_with_shadow(draw, (40, y), "📚 我的 AI Agent 知识体系图", font_title, TEXT_WHITE)
y += 45
draw.text((44, y), "4 周学习路线  ·  从零到能面试  ·  2026年6月", font=font_subtitle, fill=TEXT_GRAY)
y = HEADER_H
x_left = 40
card_width = WIDTH - 80

# ── 4 周卡片 ──────────────────────────────────
for week in WEEKS:
    card_h = week_heights[WEEKS.index(week)]

    # 卡片背景
    draw_rounded_rect(draw, [x_left, y, x_left + card_width, y + card_h],
                      radius=12, fill=CARD_BG)
    # 左侧色条
    draw.rectangle([x_left, y + 16, x_left + 4, y + card_h - 16], fill=week["color"])

    # 周标题
    inner_x = x_left + 24
    draw.text((inner_x, y + 14), week["title"], font=font_week, fill=week["color"])

    # 分隔线
    line_y = y + WEEK_HEADER_H
    draw.line([(inner_x, line_y), (x_left + card_width - 24, line_y)],
              fill="#30363d", width=1)

    # 知识点
    item_y = line_y + 14
    for item_title, item_desc in week["items"]:
        # 圆点
        draw.ellipse([inner_x + 2, item_y + 6, inner_x + 8, item_y + 12], fill=week["color"])
        # 标题
        draw.text((inner_x + 18, item_y + 1), item_title, font=font_item_title, fill=TEXT_WHITE)
        # 描述（灰色，在标题后面）
        desc_x = inner_x + 18 + draw.textlength(item_title, font=font_item_title) + 12
        draw.text((desc_x, item_y + 2), item_desc, font=font_item, fill=TEXT_GRAY)
        item_y += ITEM_H

    y += card_h + SECTION_GAP

# ── 串联线区域 ────────────────────────────────
y += 4
draw_rounded_rect(draw, [x_left, y, x_left + card_width, y + thread_h],
                  radius=12, fill=CARD_BG)
draw.rectangle([x_left, y + 16, x_left + 4, y + thread_h - 16], fill=ACCENT_BOTTOM)
inner_x = x_left + 24
draw.text((inner_x, y + 14), "🧭 把它们串成一条线（面试叙事版）", font=font_week, fill=ACCENT_BOTTOM)
line_y = y + WEEK_HEADER_H
draw.line([(inner_x, line_y), (x_left + card_width - 24, line_y)], fill="#30363d", width=1)

item_y = line_y + 14
for i, step in enumerate(THREAD_LINE):
    # 步骤编号
    step_num = f"{i+1}"
    # 小圆
    draw.ellipse([inner_x + 2, item_y + 5, inner_x + 20, item_y + 23], fill=ACCENT_BOTTOM)
    draw.text((inner_x + 7, item_y + 5), step_num, font=font_item_title, fill="#ffffff")
    draw.text((inner_x + 30, item_y + 2), step, font=font_item, fill=TEXT_WHITE)
    # 箭头（除了最后一条）
    if i < len(THREAD_LINE) - 1:
        arrow_y = item_y + 26
        draw.line([(inner_x + 11, arrow_y), (inner_x + 11, arrow_y + 16)], fill=ACCENT_BOTTOM, width=2)
        # 箭头尖
        draw.polygon([(inner_x + 6, arrow_y + 11), (inner_x + 11, arrow_y + 17),
                      (inner_x + 16, arrow_y + 11)], fill=ACCENT_BOTTOM)
    item_y += 44

y += thread_h + SECTION_GAP

# ── 掌握度自评 ───────────────────────────────
draw_rounded_rect(draw, [x_left, y, x_left + card_width, y + skill_h],
                  radius=12, fill=CARD_BG)
draw.rectangle([x_left, y + 16, x_left + 4, y + skill_h - 16], fill="#58a6ff")
draw.text((inner_x, y + 14), "📊 我的掌握度自评", font=font_week, fill="#58a6ff")
line_y = y + WEEK_HEADER_H
draw.line([(inner_x, line_y), (x_left + card_width - 24, line_y)], fill="#30363d", width=1)

item_y = line_y + 14
col_w = (card_width - 48) // 2
for i, (skill_name, skill_level, skill_color) in enumerate(SKILLS):
    col = i % 2
    row = i // 2
    sx = inner_x + col * col_w
    sy = item_y + row * 44
    # 左边小色块
    draw.rectangle([sx, sy + 5, sx + 3, sy + 25], fill=skill_color)
    draw.text((sx + 10, sy + 2), f"{skill_name}  {skill_level}", font=font_item_title, fill=TEXT_WHITE)

y += skill_h + SECTION_GAP

# ── 下一步行动 ───────────────────────────────
next_h_actual = 44 * len(NEXT_STEPS) + 80
draw_rounded_rect(draw, [x_left, y, x_left + card_width, y + next_h_actual],
                  radius=12, fill=CARD_BG)
draw.rectangle([x_left, y + 16, x_left + 4, y + next_h_actual - 16], fill="#f78166")
draw.text((inner_x, y + 14), "🎯 下一步行动", font=font_week, fill="#f78166")
line_y = y + WEEK_HEADER_H
draw.line([(inner_x, line_y), (x_left + card_width - 24, line_y)], fill="#30363d", width=1)

item_y = line_y + 14
for step in NEXT_STEPS:
    draw.ellipse([inner_x + 2, item_y + 5, inner_x + 8, item_y + 11], fill="#f78166")
    draw.text((inner_x + 18, item_y + 1), step, font=font_item_title, fill=TEXT_WHITE)
    item_y += 44

# ── 底部水印 ──────────────────────────────────
y = HEIGHT - 30
draw.text((WIDTH // 2 - 80, y), "三秘书系统 · 学习秘书自动生成", font=font_small, fill=TEXT_DIM)

# ── 保存 ──────────────────────────────────────
img.save(OUTPUT, "JPEG", quality=95)
# 同时保存 PNG 以获得清晰文字
png_path = OUTPUT.replace(".jpg", ".png")
img.save(png_path, "PNG")
print(f"[OK] JPG saved: {OUTPUT}")
print(f"[OK] PNG saved: {png_path}")
print(f"     Size: {WIDTH} x {HEIGHT}")
