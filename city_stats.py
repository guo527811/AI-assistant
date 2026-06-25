# -*- coding: utf-8 -*-
"""
city_stats.py — 读取 CSV 并生成城市频次柱状图

功能：
    1. 自动检测城市列（支持 "城市" / "city" / "City"）
    2. 统计各城市出现频次
    3. 生成中文柱状图并保存为 PNG
    4. 文件不存在、缺失列、空数据等场景均有友好提示

作者：10年Python数据处理工程师设计
日期：2026-06-24
"""

import csv
import os
import sys
from collections import Counter
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

# ============================================================
# 中文字体配置 — 解决 matplotlib 中文乱码问题
# ============================================================

def _configure_chinese_font() -> None:
    """
    自动检测并配置中文字体，覆盖常见操作系统。
    优先级：SimHei > Microsoft YaHei > WenQuanYi Micro Hei > Noto Sans CJK SC > sans-serif
    若全部缺失，回退到 sans-serif 并给出 warning，图表中文将显示为方框。
    """
    # Windows / macOS / Linux 常见中文字体候选
    candidate_fonts = [
        "SimHei",                    # Windows 黑体（最常用）
        "Microsoft YaHei",          # Windows 微软雅黑
        "PingFang SC",              # macOS 苹方
        "Heiti SC",                 # macOS 黑体
        "WenQuanYi Micro Hei",      # Linux 文泉驿微米黑
        "WenQuanYi Zen Hei",        # Linux 文泉驿正黑
        "Noto Sans CJK SC",         # Linux Google Noto 中文字体
        "Noto Sans SC",             # Linux Google Noto 简体
        "AR PL UMing CN",           # Linux AR PL 明体
    ]

    available = {f.name for f in matplotlib.font_manager.fontManager.ttflist}

    for font in candidate_fonts:
        if font in available:
            plt.rcParams["font.sans-serif"] = [font, "sans-serif"]
            plt.rcParams["axes.unicode_minus"] = False  # 避免负号显示为方块
            return

    # 回退：尝试无中文字体也能跑，但图表中文会显示异常
    print("⚠️  警告：未检测到中文字体，图表中的中文可能显示为方框。")
    print("   安装中文字体：apt install fonts-wqy-microhei (Linux)")
    print("               或 brew install font-noto-sans-cjk (macOS)")
    print("               Windows 通常已内置 SimHei，若缺失请安装。")
    plt.rcParams["font.sans-serif"] = ["sans-serif"]
    plt.rcParams["axes.unicode_minus"] = False


_configure_chinese_font()


# ============================================================
# 核心函数
# ============================================================

def detect_city_column(headers: list[str]) -> str | None:
    """
    从表头列表中自动检测城市列名。

    参数:
        headers: CSV 的第一行，列表形式

    返回:
        匹配到的列名；若未找到则返回 None

    示例:
        >>> detect_city_column(["姓名", "城市", "分数"])
        "城市"
        >>> detect_city_column(["Name", "City", "Score"])
        "City"
        >>> detect_city_column(["id", "name"])
        None
    """
    candidates = {"城市", "city", "City"}
    for h in headers:
        if h.strip() in candidates:
            return h.strip()
    return None


def read_cities(csv_path: str) -> list[str]:
    """
    读取 CSV 文件中的城市列，返回城市名列表。

    参数:
        csv_path: CSV 文件路径

    返回:
        城市名列表（已去除首尾空白）

    异常处理:
        - 文件不存在：打印提示并 sys.exit(1)
        - 无城市列：打印提示并 sys.exit(1)
        - CSV 解析错误：打印提示并 sys.exit(1)
        - 空文件：打印提示并返回空列表
    """
    if not os.path.exists(csv_path):
        print(f"❌ 错误：文件不存在 — \"{csv_path}\"")
        print("   请检查路径是否正确，然后重试。")
        sys.exit(1)

    cities: list[str] = []

    try:
        with open(csv_path, mode="r", encoding="utf-8-sig", newline="") as f:
            # sniff 前 2KB 自动检测分隔符（逗号/制表符等）
            sample = f.read(4096)
            f.seek(0)

            try:
                dialect = csv.Sniffer().sniff(sample)
            except csv.Error:
                # 如果嗅探失败（如单列），回退到默认逗号分隔
                dialect = "excel"

            reader = csv.reader(f, dialect)

            # 读表头
            try:
                raw_headers = next(reader)
            except StopIteration:
                print("⚠️  警告：CSV 文件为空（没有表头行）。")
                return []

            headers = [h.strip() for h in raw_headers]
            city_col = detect_city_column(headers)

            if city_col is None:
                print(f"❌ 错误：未找到城市列。")
                print(f"   当前列名：{headers}")
                print(f"   支持的城市列名：\"城市\" / \"city\" / \"City\"")
                print("   请检查列名或修改脚本中的 candidates。")
                sys.exit(1)

            col_index = headers.index(city_col)

            # 读数据行
            for row_num, row in enumerate(reader, start=2):  # 表头是第1行，数据从第2行开始
                if not row or all(cell.strip() == "" for cell in row):
                    continue  # 跳过空行
                if col_index >= len(row):
                    continue  # 该行不够长
                city = row[col_index].strip()
                if city:
                    cities.append(city)

    except UnicodeDecodeError:
        # 尝试 gbk 编码（Windows 下 Excel 导出的 CSV 常见）
        try:
            with open(csv_path, mode="r", encoding="gbk", newline="") as f:
                reader = csv.reader(f)
                try:
                    raw_headers = next(reader)
                except StopIteration:
                    print("⚠️  警告：CSV 文件为空（没有表头行）。")
                    return []
                headers = [h.strip() for h in raw_headers]
                city_col = detect_city_column(headers)
                if city_col is None:
                    print(f"❌ 错误：未找到城市列，当前列名：{headers}")
                    sys.exit(1)
                col_index = headers.index(city_col)
                for row in reader:
                    if not row or all(cell.strip() == "" for cell in row):
                        continue
                    if col_index >= len(row):
                        continue
                    city = row[col_index].strip()
                    if city:
                        cities.append(city)
        except Exception as e:
            print(f"❌ 读取 CSV 文件出错：{e}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ 读取 CSV 文件出错：{e}")
        sys.exit(1)

    return cities


def generate_bar_chart(
    cities: list[str],
    output_path: str = "city_frequency.png",
    top_n: int = 20,
    figsize: tuple[int, int] = (14, 7),
) -> None:
    """
    根据城市列表生成频次柱状图并保存。

    参数:
        cities:     城市名列表
        output_path: 输出图片路径，默认 city_frequency.png
        top_n:       只显示频次最高的前 N 个城市（默认 20）
        figsize:     图片尺寸 (宽, 高)，单位英寸

    异常处理:
        - cities 为空：打印提示，不生成图
    """
    if not cities:
        print("⚠️  警告：城市数据为空，不生成图表。")
        return

    counter = Counter(cities)
    # 取前 top_n
    most_common = counter.most_common(top_n)

    city_names = [item[0] for item in most_common]
    frequencies = [item[1] for item in most_common]

    # --- 颜色方案：渐变色，最高为暖色 ---
    colors = plt.cm.OrRd(np.linspace(0.4, 0.9, len(city_names)))[::-1]

    # --- 绘图 ---
    fig, ax = plt.subplots(figsize=figsize, constrained_layout=True)

    bars = ax.bar(city_names, frequencies, color=colors, edgecolor="#333333", linewidth=0.5)

    # 在柱顶标数值
    for bar, freq in zip(bars, frequencies):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(frequencies) * 0.01,
            str(freq),
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
        )

    # --- 标题与标签 ---
    ax.set_title(
        f"城市频次统计（总记录数：{len(cities)}，共 {len(counter)} 个城市）",
        fontsize=16,
        fontweight="bold",
        pad=15,
    )
    ax.set_xlabel("城市", fontsize=12, fontweight="bold")
    ax.set_ylabel("出现频次（次）", fontsize=12, fontweight="bold")

    # --- 刻度和网格 ---
    ax.tick_params(axis="x", rotation=30, labelsize=9)
    ax.tick_params(axis="y", labelsize=10)
    ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))  # y 轴刻度为整数
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)

    # --- 底部统计信息 ---
    others = len(counter) - top_n
    footer = f"显示前 {top_n} 个城市"
    if others > 0:
        footer += f"（还有 {others} 个城市未显示）"
    fig.text(0.5, 0.01, footer, ha="center", fontsize=9, color="#888888")

    # --- 保存 ---
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    print(f"✅ 图表已保存至：{os.path.abspath(output_path)}")
    print(f"   总记录 {len(cities)} 条，涉及 {len(counter)} 个城市，展示前 {top_n} 个。")


def print_summary(cities: list[str]) -> None:
    """
    在终端打印城市频次汇总表。

    参数:
        cities: 城市名列表
    """
    if not cities:
        print("   无数据。")
        return

    counter = Counter(cities)
    print(f"\n📊 城市频次汇总（总数 {len(cities)} 条，{len(counter)} 个城市）：")
    print("-" * 44)
    print(f"{'城市':<16s} {'频次':>6s}  {'占比':>8s}  {'柱状图':>s}")
    print("-" * 44)

    max_count = max(counter.values())
    bar_width = 12  # 柱状图最大宽度（字符数）

    for city, count in counter.most_common():
        pct = count / len(cities) * 100
        bar_len = int(count / max_count * bar_width)
        bar_str = "█" * bar_len + "░" * (bar_width - bar_len)
        print(f"{city:<16s} {count:>6d}  {pct:>7.1f}%  {bar_str}")
    print("-" * 44)


# ============================================================
# 主入口
# ============================================================

def main() -> None:
    """
    主函数：解析命令行参数 → 读取 CSV → 生成图表 → 打印汇总。

    用法：
        python city_stats.py data.csv
        python city_stats.py data.csv -o result.png
        python city_stats.py data.csv -o result.png -n 15
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="读取 CSV 中的城市列，生成频次柱状图。",
        epilog="示例：python city_stats.py data.csv -o chart.png -n 10",
    )
    parser.add_argument(
        "csv_file",
        help="输入的 CSV 文件路径",
    )
    parser.add_argument(
        "-o", "--output",
        default="city_frequency.png",
        help="输出图片路径（默认：city_frequency.png）",
    )
    parser.add_argument(
        "-n", "--top",
        type=int,
        default=20,
        help="显示频次最高的前 N 个城市（默认：20）",
    )
    parser.add_argument(
        "--no-chart",
        action="store_true",
        help="只打印终端汇总，不生成图片",
    )

    args = parser.parse_args()

    # 1. 读取城市数据
    print(f"📂 读取文件：{args.csv_file}")
    cities = read_cities(args.csv_file)

    if not cities:
        print("⚠️  没有读取到任何城市数据，程序退出。")
        sys.exit(0)

    # 2. 终端打印汇总
    print_summary(cities)

    # 3. 生成图表
    if not args.no_chart:
        generate_bar_chart(cities, output_path=args.output, top_n=args.top)

    print("\n🎉 完成！")


if __name__ == "__main__":
    main()
