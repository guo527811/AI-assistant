"""作业2：微调三方法对比图 → JPG 保存到桌面"""
from PIL import Image, ImageDraw, ImageFont

# ── 配置 ──────────────────────────────────────
WIDTH = 1100
FONT_PATH = "C:/Windows/Fonts/msyh.ttc"
FONT_BOLD_PATH = "C:/Windows/Fonts/msyhbd.ttc"
OUTPUT = "C:/Users/lenovo/Desktop/微调三方法对比-全量vsLoRAvsQLoRA.jpg"

# 配色 — 三种方法分别用三色
BG = "#0d1117"
CARD_BG = "#161b22"
FULL_COLOR = "#f78166"    # 橙红 — 全量微调（昂贵）
LORA_COLOR = "#58a6ff"    # 蓝   — LoRA（平衡）
QLORA_COLOR = "#3fb950"   # 绿   — QLoRA（最省）
ACCENT = "#bc8cff"        # 紫色强调
TEXT_W = "#e6edf3"
TEXT_G = "#8b949e"

# ── 数据 ──────────────────────────────────────
TITLE = "大模型微调三方法对比"
SUBTITLE = "全量微调 vs LoRA vs QLoRA — 一张图看懂该选哪个"

# 三个方法的数据
METHODS = [
    {
        "name": "全量微调",
        "ename": "Full Fine-tuning",
        "color": FULL_COLOR,
        "icon": "🏗️",
        "principle": "更新模型全部参数",
        "principle_detail": "W_new = 训练所有 W",
        "vram": "7B 需 ~112GB\n(8×A100)",
        "time": "数天 ~ 数周",
        "cost": "极高（GPU 租赁\n~数千元/次）",
        "params_trained": "100%（70亿参数）",
        "scenario": "大公司/研究院\n有充足 GPU 预算",
        "pros": "效果最好",
        "cons": "个人开发者玩不起",
        "analogy": "把整栋楼拆了重建"
    },
    {
        "name": "LoRA",
        "ename": "Low-Rank Adaptation",
        "color": LORA_COLOR,
        "icon": "🔧",
        "principle": "冻结原模型，旁路训练\n两个低秩矩阵 A×B",
        "principle_detail": "W_new = W + B×A\n只训练 A 和 B",
        "vram": "7B 需 ~16GB\n(一张 3090/4090)",
        "time": "数小时",
        "cost": "低（Colab 免费 GPU\n即可跑）",
        "params_trained": "<1%（~400万参数）",
        "scenario": "个人开发者\n中小团队",
        "pros": "消费级显卡可跑\n性价比最高",
        "cons": "效果略低于全量微调",
        "analogy": "在楼旁边加个电梯\n不动原有结构"
    },
    {
        "name": "QLoRA",
        "ename": "Quantized LoRA",
        "color": QLORA_COLOR,
        "icon": "⚡",
        "principle": "LoRA + 4-bit 量化\n原模型压缩后再训练",
        "principle_detail": "W(4bit) + B×A\n双量化再省 0.4bit",
        "vram": "7B 需 ~8GB\n65B 需 ~24GB",
        "time": "数小时（略慢于 LoRA）",
        "cost": "最低（消费显卡\n甚至笔记本可跑）",
        "params_trained": "<1% + 原模型压缩 75%",
        "scenario": "个人开发者\n硬件有限的场景",
        "pros": "单卡玩 65B 大模型\n最省钱方案",
        "cons": "训练比 LoRA 略慢",
        "analogy": "用图纸（压缩版）\n规划电梯安装，更省空间"
    }
]

# ── 布局计算 ──────────────────────────────────
HEADER_H = 100
METHOD_TOP = HEADER_H + 20
METHOD_H = 620
FOOTER_H = 160
PADDING = 16
CARD_WIDTH = 330
CARD_GAP = 20
LEFT_MARGIN = (WIDTH - (CARD_WIDTH * 3 + CARD_GAP * 2)) // 2
HEIGHT = METHOD_TOP + METHOD_H + FOOTER_H

# ── 创建画布 ──────────────────────────────────
img = Image.new("RGB", (WIDTH, HEIGHT), BG)
draw = ImageDraw.Draw(img)

try:
    font_title = ImageFont.truetype(FONT_BOLD_PATH, 30)
    font_sub = ImageFont.truetype(FONT_PATH, 15)
    font_method = ImageFont.truetype(FONT_BOLD_PATH, 22)
    font_ename = ImageFont.truetype(FONT_PATH, 12)
    font_label = ImageFont.truetype(FONT_BOLD_PATH, 14)
    font_value = ImageFont.truetype(FONT_PATH, 13)
    font_tag = ImageFont.truetype(FONT_BOLD_PATH, 12)
    font_small = ImageFont.truetype(FONT_PATH, 11)
    font_footer = ImageFont.truetype(FONT_BOLD_PATH, 16)
except:
    font_title = font_sub = font_method = font_ename = font_label = font_value = font_tag = font_small = font_footer = ImageFont.load_default()

# ── 辅助 ──────────────────────────────────────
def rounded_rect(draw, xy, r, fill, outline=None):
    draw.rounded_rectangle(xy, radius=r, fill=fill, outline=outline)

def center_text(draw, y, text, font, fill, width=None):
    """居中绘制文字"""
    if width is None:
        width = WIDTH
    tw = draw.textlength(text, font=font)
    x = (width - tw) // 2
    draw.text((x, y), text, font=font, fill=fill)
    return y

def draw_row(draw, x, y, label, value, color, card_w):
    """绘制一行：标签 + 值"""
    # 标签
    draw.text((x + 14, y), label, font=font_label, fill=color)
    # 值（支持多行）
    for i, line in enumerate(value.split('\n')):
        draw.text((x + 14, y + 20 + i * 18), line, font=font_value, fill=TEXT_W)

# ═══════════════════════════════════════════════
# 绘制
# ═══════════════════════════════════════════════

# ── 标题 ──────────────────────────────────────
y = 18
draw.text((LEFT_MARGIN, y), TITLE, font=font_title, fill=TEXT_W)
draw.text((LEFT_MARGIN, y + 44), SUBTITLE, font=font_sub, fill=TEXT_G)
# 分隔线
draw.line([(LEFT_MARGIN, y + 72), (WIDTH - LEFT_MARGIN, y + 72)], fill="#30363d", width=1)

# ── 三列卡片 ──────────────────────────────────
for i, m in enumerate(METHODS):
    cx = LEFT_MARGIN + i * (CARD_WIDTH + CARD_GAP)
    cy = METHOD_TOP

    # 卡片背景
    rounded_rect(draw, [cx, cy, cx + CARD_WIDTH, cy + METHOD_H], 12, CARD_BG)
    # 顶部色条
    draw.rectangle([cx, cy, cx + CARD_WIDTH, cy + 5], fill=m["color"])

    # 方法名 + 图标
    draw.text((cx + 18, cy + 18), f"{m['icon']} {m['name']}", font=font_method, fill=m["color"])
    draw.text((cx + 18, cy + 46), m['ename'], font=font_ename, fill=TEXT_G)

    # 分隔线
    draw.line([(cx + 14, cy + 70), (cx + CARD_WIDTH - 14, cy + 70)], fill="#30363d", width=1)

    # ── 核心原理 ──
    ry = cy + 82
    draw.text((cx + 14, ry), "💡 一句话核心原理", font=font_label, fill=ACCENT)
    draw.text((cx + 14, ry + 24), m['principle_detail'], font=font_value, fill=TEXT_W)
    # 类比
    draw.text((cx + 14, ry + 65), f"🔑 {m['analogy']}", font=font_tag, fill=TEXT_G)

    # ── 分隔 ──
    draw.line([(cx + 14, ry + 95), (cx + CARD_WIDTH - 14, ry + 95)], fill="#30363d", width=1)

    # ── 资源需求 ──
    ry2 = ry + 108
    draw.text((cx + 14, ry2), "📊 资源需求", font=font_label, fill=m["color"])

    # 显存
    draw.text((cx + 14, ry2 + 24), "显存需求", font=font_tag, fill=TEXT_G)
    for j, line in enumerate(m["vram"].split('\n')):
        draw.text((cx + 14, ry2 + 43 + j * 18), line, font=font_value, fill=TEXT_W)

    # 时间
    vram_lines = len(m["vram"].split('\n'))
    time_y = ry2 + 43 + vram_lines * 18 + 8
    draw.text((cx + 14, time_y), "训练时间", font=font_tag, fill=TEXT_G)
    draw.text((cx + 14, time_y + 19), m["time"], font=font_value, fill=TEXT_W)

    # 成本
    draw.text((cx + 14, time_y + 48), "成本", font=font_tag, fill=TEXT_G)
    for j, line in enumerate(m["cost"].split('\n')):
        draw.text((cx + 14, time_y + 67 + j * 18), line, font=font_value, fill=TEXT_W)

    # ── 可训练参数 ──
    cost_lines = len(m["cost"].split('\n'))
    param_y = time_y + 67 + cost_lines * 18 + 10
    draw.line([(cx + 14, param_y), (cx + CARD_WIDTH - 14, param_y)], fill="#30363d", width=1)
    draw.text((cx + 14, param_y + 10), "可训练参数量", font=font_tag, fill=TEXT_G)
    draw.text((cx + 14, param_y + 29), m["params_trained"], font=font_value, fill=m["color"])

    # ── 适用场景 ──
    scene_y = param_y + 58
    draw.line([(cx + 14, scene_y), (cx + CARD_WIDTH - 14, scene_y)], fill="#30363d", width=1)
    draw.text((cx + 14, scene_y + 10), "🎯 适用场景", font=font_label, fill=ACCENT)
    for j, line in enumerate(m["scenario"].split('\n')):
        draw.text((cx + 14, scene_y + 32 + j * 18), line, font=font_value, fill=TEXT_W)

    # ── 优缺点 ──
    pros_y = scene_y + 32 + len(m["scenario"].split('\n')) * 18 + 10
    draw.line([(cx + 14, pros_y), (cx + CARD_WIDTH - 14, pros_y)], fill="#30363d", width=1)
    draw.text((cx + 14, pros_y + 10), "✅ " + m["pros"], font=font_tag, fill=QLORA_COLOR)
    draw.text((cx + 14, pros_y + 35), "⚠️ " + m["cons"], font=font_tag, fill=FULL_COLOR)

# ── 底部：选择建议 ─────────────────────────────
fy = METHOD_TOP + METHOD_H + 24
rounded_rect(draw, [LEFT_MARGIN, fy, WIDTH - LEFT_MARGIN, fy + 120], 10, CARD_BG)
draw.rectangle([LEFT_MARGIN, fy, LEFT_MARGIN + 4, fy + 120], fill=ACCENT)

fx = LEFT_MARGIN + 24
draw.text((fx, fy + 14), "🎯 一句话选择指南", font=font_footer, fill=ACCENT)
advice = [
    "有 8×A100 预算？→ 全量微调，效果拉满    只有一张消费显卡？→ QLoRA，单卡玩转 65B    入门学习？→ LoRA，最简单直接",
]
for i, line in enumerate(advice):
    draw.text((fx, fy + 44 + i * 22), line, font=font_value, fill=TEXT_W)

# 关键数据
draw.text((fx, fy + 74), "显存对比：全量 112GB  vs  LoRA 16GB  vs  QLoRA 8GB    参数训练量：100%  vs  <1%  vs  <1%    个人开发者推荐：QLoRA > LoRA >>> 全量微调", font=font_small, fill=TEXT_G)

# ── 保存 ──────────────────────────────────────
img.save(OUTPUT, "JPEG", quality=95)
png_path = OUTPUT.replace(".jpg", ".png")
img.save(png_path, "PNG")
print(f"[OK] JPG: {OUTPUT}")
print(f"[OK] PNG: {png_path}")
print(f"     Size: {WIDTH} x {HEIGHT}")
