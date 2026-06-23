"""
RAG 服务模块
提供文档索引、检索增强生成、跨集合查询能力。
"""

from .config import COLLECTIONS, CHROMA_DB_ROOT, API_KEY, BASE_URL, MODEL
from .rag_service import RAGService
