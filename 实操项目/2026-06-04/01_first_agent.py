"""
实操1：你的第一个 Claude Agent
功能：分析项目目录结构，输出架构摘要

使用方式：
  python 01_first_agent.py

前提：
  pip install claude-agent-sdk
"""

import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions


async def main():
    """第一个 Agent：分析当前项目的目录结构和架构"""

    prompt = """分析当前目录（E:/AI助手/）的目录结构：

1. 列出所有一级目录和文件
2. 识别每个目录的用途
3. 用一句话总结这个项目的架构设计
4. 输出格式要简洁，用中文
"""

    print("=" * 50)
    print("Agent 启动中...")
    print("任务：分析 E:/AI助手/ 项目架构")
    print("=" * 50)

    async for message in query(
        prompt=prompt,
        options=ClaudeAgentOptions(
            # 只给读权限，安全第一
            allowed_tools=["Read", "Glob", "Bash"],
            permission_mode="default",
            # 关键：加载项目配置
            setting_sources=["project"],
            cwd="E:/AI助手",
            system_prompt="你是一位软件架构分析师，擅长用中文简洁地总结项目结构。",
        ),
    ):
        # 流式打印 Agent 的每一步
        if hasattr(message, "type"):
            if message.type == "tool_use":
                print(f"\n[工具调用] {message.tool_name}: {message.tool_input}")
            elif message.type == "tool_result":
                preview = str(message.content)[:200]
                print(f"[工具结果] {preview}...")
        elif hasattr(message, "result"):
            print("\n" + "=" * 50)
            print("Agent 完成！输出：")
            print("=" * 50)
            print(message.result)


if __name__ == "__main__":
    asyncio.run(main())
