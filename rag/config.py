"""
RAG 服务配置模块
- API 密钥和端点
- 跨平台路径
- 集合定义
"""

import os

# ============================================================
# API 配置（从环境变量读取）
# ============================================================
API_KEY = os.environ.get("ANTHROPIC_AUTH_TOKEN", "")
BASE_URL = os.environ.get("ANTHROPIC_BASE_URL", "https://api.deepseek.com/anthropic")
MODEL = "deepseek-v4-pro"

if not API_KEY:
    raise RuntimeError(
        "未设置 ANTHROPIC_AUTH_TOKEN 环境变量。"
        "请在 Claude Code settings.json 的 env 段中配置，或手动设置环境变量。"
    )

# ============================================================
# Embedding 模型配置
# ============================================================
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# ============================================================
# 默认参数
# ============================================================
DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 50
DEFAULT_K = 4
DEFAULT_TEMPERATURE = 0.3

# ============================================================
# 平台检测 & 路径
# ============================================================
# AI_HOME 优先从环境变量读取，未设置则自动检测（取 config.py 上两级目录）
IS_WINDOWS = os.name == "nt"

AI_HOME = os.environ.get("AI_HOME", "")
if not AI_HOME:
    # 自动检测：config.py 位于 <AI_HOME>/rag/config.py
    AI_HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RAG_HOME = os.path.join(AI_HOME, "rag")
CHROMA_DB_ROOT = os.environ.get(
    "CHROMA_DB_ROOT",
    os.path.join(RAG_HOME, "chroma_db"),
)

# ============================================================
# 集合定义
# ============================================================
COLLECTIONS = {
    "news": {
        "dir": os.environ.get(
            "NEWS_DIR",
            os.path.join(AI_HOME, "新闻简报"),
        ),
        "glob": "**/*.md",
        "description": "AI 新闻简报",
    },
    "learning": {
        "dir": os.environ.get(
            "LEARNING_DIR",
            os.path.join(AI_HOME, "学习资料"),
        ),
        "glob": "**/*.md",
        "description": "学习笔记和进度",
    },
    "jobs": {
        "dir": os.environ.get(
            "JOBS_DIR",
            os.path.join(AI_HOME, "求职"),
        ),
        "glob": "**/*.{md,txt}",
        "description": "岗位追踪、简历、差距分析",
    },
    "projects": {
        "dir": os.environ.get(
            "PROJECTS_DIR",
            os.path.join(AI_HOME, "实操项目"),
        ),
        "glob": "**/*.{py,js,md}",
        "description": "实操项目代码",
    },
}
