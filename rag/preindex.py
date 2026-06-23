#!/usr/bin/env python
"""
一次性批量索引：将所有已知文档索引到 4 个集合。
运行一次即可，后续通过 rag_cli.py index 增量添加。
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rag_service import RAGService
import config


def main():
    print("=" * 60)
    print("RAG 预索引 — 批量索引所有已知文档")
    print(f"向量库根目录：{config.CHROMA_DB_ROOT}")
    print(f"Embedding 模型：{config.EMBEDDING_MODEL}")
    print(f"LLM 模型：{config.MODEL}")
    print("=" * 60)
    print()

    total_files = 0
    total_chunks = 0

    for name, cfg in config.COLLECTIONS.items():
        print(f"[{name}] {cfg['description']}")
        print(f"  目录：{cfg['dir']}")
        print(f"  模式：{cfg['glob']}")

        svc = RAGService(name)
        result = svc.index_directory(cfg["dir"], cfg["glob"])

        files = result.get("files_indexed", 0)
        skipped = result.get("files_skipped", 0)
        chunks = result.get("chunks_added", 0)

        print(f"  结果：{files} 新增, {skipped} 跳过, {chunks} 块")
        print()

        total_files += files + skipped
        total_chunks += chunks

    print("=" * 60)
    print(f"总计：{total_files} 文件, {total_chunks} 块")
    print("=" * 60)

    # 显示各集合统计
    print()
    print("各集合统计：")
    for name in config.COLLECTIONS:
        svc = RAGService(name)
        stats = svc.get_stats()
        print(f"  [{name}] {stats['chunk_count']} 块, {stats['source_count']} 源文件")


if __name__ == "__main__":
    main()
