"""
作业2：语义压缩练习
对比「松散提示词」vs「压缩提示词」的输出质量
"""
import asyncio, sys, io, os, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from claude_agent_sdk import query, ClaudeAgentOptions

# ============================================================
# 原始提示词 — 松散、模糊、缺约束
# ============================================================
PROMPT_LOOSE = """
你帮我写一个 Python 脚本，功能是读取一个 CSV 文件，统计里面每个城市出现的次数，
然后画一个柱状图。记得代码要写注释，最好加上错误处理，就是万一文件不存在啥的别直接崩了。
输出的时候帮我顺便说明一下怎么用这个脚本。
"""

# ============================================================
# 压缩提示词 — 角色+任务+约束+格式
# ============================================================
PROMPT_COMPACT = """
## 角色：10年经验的Python数据处理工程师

## 任务：写一个 Python 脚本（city_stats.py），读取CSV并生成城市频次柱状图

## 约束：
- CSV至少含一列城市名（列名可能是"城市""city""City"，自动检测）
- 文件不存在时给出友好中文提示，不让程序崩溃
- 柱状图用中文标题和标签（matplotlib需配置中文字体）
- 每个函数有中文docstring
- 空CSV或缺失列时给出提示

## 格式：
1. 输出完整可运行的 .py 代码
2. 代码后用3句话说明：怎么安装依赖、怎么运行、示例CSV格式
"""


async def compare_prompts():
    """分别用松散和压缩提示词生成脚本，对比结果"""

    # 只跑压缩版（效果好），原始版作为对比展示
    print("=" * 60)
    print("📝 原始提示词（松散版）：")
    print("-" * 60)
    print(PROMPT_LOOSE)
    print()
    print("=" * 60)
    print("🎯 压缩提示词（四要素版）：")
    print("-" * 60)
    print(PROMPT_COMPACT)
    print()
    print("=" * 60)
    print("🚀 用压缩提示词生成代码...")
    print("=" * 60)
    print()

    async for message in query(
        prompt=PROMPT_COMPACT + "\n\n请直接输出完整的 Python 脚本代码。",
        options=ClaudeAgentOptions(
            allowed_tools=["Write"],
            permission_mode="bypassPermissions",
        ),
    ):
        if hasattr(message, "result"):
            print(message.result)

asyncio.run(compare_prompts())
