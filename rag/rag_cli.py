#!/usr/bin/env python
"""
RAG CLI — 供三秘书 Cron 任务通过 Bash 调用

用法：
  python rag_cli.py index --collection news --dir E:/AI助手/新闻简报/
  python rag_cli.py query --collection news --question "最近Claude有什么更新？"
  python rag_cli.py stats --collection news
  python rag_cli.py list --collection news
  python rag_cli.py preindex

所有命令输出单行 JSON 到 stdout。错误输出 JSON 到 stdout 并 exit 1。
"""

import sys
import os
import json
import argparse

# 确保能找到同目录的模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rag_service import RAGService
import config


def cmd_index(args):
    """索引文档"""
    svc = RAGService(args.collection)

    if args.dir:
        result = svc.index_directory(
            args.dir,
            glob_pattern=args.glob,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
        )
    elif args.file:
        result = svc.index_file(
            args.file,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
        )
    else:
        result = {"status": "error", "message": "需要 --dir 或 --file 参数"}
        print(json.dumps(result, ensure_ascii=False))
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False))
    if result["status"] == "error":
        sys.exit(1)


def cmd_query(args):
    """查询"""
    svc = RAGService(args.collection)

    if args.raw:
        result = svc.similarity_search(args.question, k=args.k)
    else:
        result = svc.query(args.question, k=args.k, temperature=args.temperature)

    print(json.dumps(result, ensure_ascii=False))
    if result["status"] == "error":
        sys.exit(1)


def cmd_stats(args):
    """统计"""
    svc = RAGService(args.collection)
    result = svc.get_stats()
    print(json.dumps(result, ensure_ascii=False))


def cmd_list(args):
    """列出源文件"""
    svc = RAGService(args.collection)
    result = svc.list_sources()
    print(json.dumps(result, ensure_ascii=False))


def cmd_preindex(_args):
    """批量索引所有已知文档"""
    results = {}
    for name, cfg in config.COLLECTIONS.items():
        print(f"正在索引 {name}...", file=sys.stderr)
        svc = RAGService(name)
        result = svc.index_directory(cfg["dir"], cfg["glob"])
        results[name] = result
        status = result["status"]
        files = result.get("files_indexed", 0)
        skipped = result.get("files_skipped", 0)
        chunks = result.get("chunks_added", 0)
        print(f"  [{name}] {status}: {files} 新文件, {skipped} 跳过, {chunks} 块",
              file=sys.stderr)

    summary = {
        "status": "ok",
        "collections": results,
        "total_files": sum(
            r.get("files_indexed", 0) + r.get("files_skipped", 0)
            for r in results.values()
        ),
        "total_chunks": sum(r.get("chunks_added", 0) for r in results.values()),
    }
    print(json.dumps(summary, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(
        description="RAG CLI — 文档检索增强生成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python rag_cli.py preindex
  python rag_cli.py stats --collection news
  python rag_cli.py query --collection news --question "最近Claude有什么更新？"
  python rag_cli.py index --collection learning --file E:/AI助手/学习资料/学习路线.md
  python rag_cli.py index --collection news --dir E:/AI助手/新闻简报/
        """,
    )
    sub = parser.add_subparsers(dest="command", help="子命令")

    # --- index ---
    p_index = sub.add_parser("index", help="索引文档")
    p_index.add_argument("--collection", "-c", required=True,
                         choices=list(config.COLLECTIONS.keys()),
                         help="集合名称")
    p_index.add_argument("--dir", "-d", help="要索引的目录（递归）")
    p_index.add_argument("--file", "-f", help="要索引的单个文件")
    p_index.add_argument("--glob", default=None,
                         help="文件匹配模式（如 **/*.md）")
    p_index.add_argument("--chunk-size", type=int, default=config.DEFAULT_CHUNK_SIZE)
    p_index.add_argument("--chunk-overlap", type=int, default=config.DEFAULT_CHUNK_OVERLAP)

    # --- query ---
    p_query = sub.add_parser("query", help="RAG 问答")
    p_query.add_argument("--collection", "-c", required=True,
                         choices=list(config.COLLECTIONS.keys()))
    p_query.add_argument("--question", "-q", required=True, help="问题")
    p_query.add_argument("--k", type=int, default=config.DEFAULT_K,
                         help="检索片段数（默认 4）")
    p_query.add_argument("--temperature", type=float, default=config.DEFAULT_TEMPERATURE)
    p_query.add_argument("--raw", action="store_true",
                         help="仅检索不生成（不用 LLM）")

    # --- stats ---
    p_stats = sub.add_parser("stats", help="集合统计")
    p_stats.add_argument("--collection", "-c", required=True,
                         choices=list(config.COLLECTIONS.keys()))

    # --- list ---
    p_list = sub.add_parser("list", help="列出所有源文件")
    p_list.add_argument("--collection", "-c", required=True,
                        choices=list(config.COLLECTIONS.keys()))

    # --- preindex ---
    sub.add_parser("preindex", help="批量索引全部已知文档")

    args = parser.parse_args()

    if args.command == "index":
        if not args.dir and not args.file:
            print(json.dumps({"status": "error", "message": "需要 --dir 或 --file 参数"},
                             ensure_ascii=False))
            sys.exit(1)
        cmd_index(args)
    elif args.command == "query":
        cmd_query(args)
    elif args.command == "stats":
        cmd_stats(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "preindex":
        cmd_preindex(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
