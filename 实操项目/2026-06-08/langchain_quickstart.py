"""
LangChain 核心概念速成 — Chain + Agent + Tool
学习目标：理解 LangChain 三大核心概念，为 RAG 实战打基础

使用方式：
  python langchain_quickstart.py
"""

import os
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# ============================================================
# API 配置（从环境变量读取）
# ============================================================
API_KEY = os.environ.get("ANTHROPIC_AUTH_TOKEN", "")
BASE_URL = os.environ.get("ANTHROPIC_BASE_URL", "https://api.deepseek.com/anthropic")
MODEL = "deepseek-v4-pro"


def create_llm(temperature=0.7):
    """创建 LLM 实例，使用 DeepSeek 的 Anthropic 兼容接口"""
    return ChatAnthropic(
        model=MODEL,
        api_key=API_KEY,
        base_url=BASE_URL,
        temperature=temperature,
    )


# ============================================================
# 概念 1：Chain — 串联 LLM 调用
# ============================================================
def demo_chain():
    """演示 LCEL Chain：Prompt → LLM → Parser"""
    print("\n" + "=" * 60)
    print("🔗 概念 1：Chain（链）")
    print("=" * 60)

    llm = create_llm(temperature=0.7)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个{role}，擅长用{style}风格回答。"),
        ("user", "{question}")
    ])

    chain = prompt | llm | StrOutputParser()

    # 测试：不同 role 不同输出
    result = chain.invoke({
        "role": "Python 面试官",
        "style": "简洁",
        "question": "用一句话解释什么是装饰器"
    })
    print(f"\n📝 Chain 输出：\n{result}")


# ============================================================
# 概念 2：Tool — 定义外部能力
# ============================================================
from langchain_core.tools import tool

@tool
def search_knowledge_base(query: str) -> str:
    """搜索内部知识库，返回相关文档内容。用于查询公司内部文档、技术规范等。

    Args:
        query: 搜索关键词
    """
    # 模拟知识库
    kb = {
        "python": "Python 3.13 新增了更好的错误提示和 JIT 编译器实验性支持。",
        "langchain": "LangChain 是一个 LLM 应用框架。2026 年推荐使用 LCEL 和 LangGraph。",
        "claude": "Claude Code 是 Anthropic 的 AI 编程助手，支持 Agent SDK 和 MCP 协议。",
    }
    for key, value in kb.items():
        if key in query.lower():
            return value
    return "未找到相关文档。"


def demo_tool():
    """演示 Tool 的定义和使用"""
    print("\n" + "=" * 60)
    print("🔧 概念 2：Tool（工具）")
    print("=" * 60)

    # 直接调用工具
    result = search_knowledge_base.invoke({"query": "langchain"})
    print(f"📝 工具调用结果：{result}")

    print(f"\n   工具名称：{search_knowledge_base.name}")
    print(f"   工具描述：{search_knowledge_base.description[:80]}...")


# ============================================================
# 概念 3：Agent — LLM + 工具 + 决策
# ============================================================
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage


def demo_agent():
    """演示 Agent：LLM 自主决定何时调用工具"""
    print("\n" + "=" * 60)
    print("🤖 概念 3：Agent（智能体）")
    print("=" * 60)

    llm = create_llm(temperature=0.3)

    agent = create_react_agent(
        model=llm,
        tools=[search_knowledge_base],
    )

    questions = [
        "搜索知识库中关于 Claude 的信息，然后告诉我 Claude Code 支持什么协议。",
    ]

    for q in questions:
        print(f"\n❓ 用户：{q}")
        result = agent.invoke({"messages": [HumanMessage(content=q)]})

        # 获取最终回答
        final_msg = result["messages"][-1]
        print(f"💬 Agent：{final_msg.content[:300]}...")


# ============================================================
# Main
# ============================================================
if __name__ == "__main__":
    print(f"🔑 API: {MODEL} @ {BASE_URL}")
    print("🚀 LangChain 核心概念速成")
    print("今天学习：Chain → Tool → Agent")

    # 1. Chain
    demo_chain()

    # 2. Tool
    demo_tool()

    # 3. Agent
    demo_agent()

    print("\n" + "=" * 60)
    print("✅ 三个核心概念练习完成！")
    print("=" * 60)
    print("""
📝 今日要点：
  - Chain = 把 Prompt + LLM + Parser 串起来
  - Tool  = 用 @tool 装饰器定义外部能力
  - Agent = LLM 自主决定何时调用哪个 Tool

🔜 下一步：用这三个概念搭建 RAG 文档问答系统（rag_demo.py）
""")
