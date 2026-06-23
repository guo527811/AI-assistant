"""
RAG 服务核心引擎
- 支持多集合（news/learning/jobs/projects）
- 持久化向量库（不复建）
- 增量索引（自动跳过已索引文件）
- 所有方法返回 JSON dict
"""

import os
import sys
import json
import glob as glob_mod

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# 从同目录导入配置
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config


class RAGService:
    """
    RAG 服务类

    用法：
        svc = RAGService("news")
        svc.index_directory("E:/AI助手/新闻简报/")
        result = svc.query("最近Claude有什么更新？")
    """

    def __init__(self, collection_name: str, persist_root: str = None):
        """
        Args:
            collection_name: 集合名（news/learning/jobs/projects）
            persist_root:    向量库根目录，默认 config.CHROMA_DB_ROOT
        """
        if collection_name not in config.COLLECTIONS:
            raise ValueError(
                f"未知集合 '{collection_name}'，可选：{list(config.COLLECTIONS.keys())}"
            )

        self.collection_name = collection_name
        self.persist_dir = os.path.join(
            persist_root or config.CHROMA_DB_ROOT, collection_name
        )
        self._embeddings = None
        self._llm = None
        self._vectorstore = None

        # 确保目录存在
        os.makedirs(self.persist_dir, exist_ok=True)

        # 加载或创建向量库
        self._load_vectorstore()

    # ============================================================
    # 索引
    # ============================================================

    def index_directory(
        self,
        directory: str,
        glob_pattern: str = None,
        chunk_size: int = config.DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = config.DEFAULT_CHUNK_OVERLAP,
    ) -> dict:
        """
        递归索引目录下所有匹配的文件。

        Args:
            directory:    目录路径
            glob_pattern: 文件匹配模式（默认从集合配置读取）
            chunk_size:   分块大小
            chunk_overlap: 分块重叠

        Returns:
            {"status": "ok", "files_indexed": N, "files_skipped": M,
             "chunks_added": C, "collection": name}
        """
        if glob_pattern is None:
            glob_pattern = config.COLLECTIONS[self.collection_name]["glob"]

        # 递归查找文件（支持 **/*.{ext1,ext2} 花括号扩展）
        import pathlib
        all_files = []

        # 解析花括号模式
        if "{" in glob_pattern and "}" in glob_pattern:
            # 提取扩展名列表：**/*.{md,txt} → extensions = [".md", ".txt"]
            brace_content = glob_pattern[glob_pattern.index("{")+1:glob_pattern.index("}")]
            extensions = [f".{e.strip()}" for e in brace_content.split(",")]

            # 用 pathlib 递归匹配
            base_dir = pathlib.Path(directory)
            for ext in extensions:
                if glob_pattern.startswith("**"):
                    all_files.extend(str(p) for p in base_dir.rglob(f"*{ext}"))
                else:
                    all_files.extend(str(p) for p in base_dir.glob(f"*{ext}"))
        else:
            all_files = glob_mod.glob(os.path.join(directory, glob_pattern), recursive=True)

        all_files = sorted(set(all_files))

        if not all_files:
            return {
                "status": "ok",
                "files_indexed": 0,
                "files_skipped": 0,
                "chunks_added": 0,
                "collection": self.collection_name,
                "message": f"目录 {directory} 中没有匹配 {glob_pattern} 的文件",
            }

        # 获取已索引的文件列表（用于去重）
        indexed_sources = set(self.list_sources()["sources"])

        files_indexed = 0
        files_skipped = 0
        total_chunks = 0

        for file_path in all_files:
            abs_path = os.path.abspath(file_path)

            # 去重：跳过已索引的文件
            if abs_path in indexed_sources:
                files_skipped += 1
                continue

            try:
                result = self.index_file(
                    file_path, chunk_size, chunk_overlap, skip_source_check=True
                )
                if result["status"] == "ok":
                    files_indexed += 1
                    total_chunks += result.get("chunks_added", 0)
            except Exception as e:
                print(f"警告：索引 {file_path} 失败：{e}", file=sys.stderr)

        return {
            "status": "ok",
            "files_indexed": files_indexed,
            "files_skipped": files_skipped,
            "chunks_added": total_chunks,
            "collection": self.collection_name,
        }

    def index_file(
        self,
        file_path: str,
        chunk_size: int = config.DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = config.DEFAULT_CHUNK_OVERLAP,
        skip_source_check: bool = False,
    ) -> dict:
        """
        索引单个文件。

        Args:
            file_path:         文件绝对路径
            chunk_size:        分块大小
            chunk_overlap:     分块重叠
            skip_source_check: 跳过去重检查（index_directory 内部使用）

        Returns:
            {"status": "ok", "file": "...", "chunks_added": N}
            或 {"status": "skipped", "reason": "already_indexed"}
        """
        abs_path = os.path.abspath(file_path)

        if not os.path.exists(abs_path):
            return {"status": "error", "message": f"文件不存在：{abs_path}"}

        # 去重检查
        if not skip_source_check:
            indexed_sources = set(self.list_sources()["sources"])
            if abs_path in indexed_sources:
                return {"status": "skipped", "reason": "already_indexed", "file": abs_path}

        # 加载文档
        try:
            loader = TextLoader(abs_path, encoding="utf-8")
            docs = loader.load()
        except Exception as e:
            return {"status": "error", "message": f"加载文件失败：{e}", "file": abs_path}

        if not docs:
            return {"status": "ok", "file": abs_path, "chunks_added": 0, "message": "空文件"}

        # 分块
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", "！", "？", ".", " ", ""],
        )
        chunks = text_splitter.split_documents(docs)

        if not chunks:
            return {"status": "ok", "file": abs_path, "chunks_added": 0, "message": "分块后为空"}

        # 加入向量库
        self._vectorstore.add_documents(chunks)

        return {
            "status": "ok",
            "file": abs_path,
            "chunks_added": len(chunks),
        }

    # ============================================================
    # 查询
    # ============================================================

    def query(
        self,
        question: str,
        k: int = config.DEFAULT_K,
        temperature: float = config.DEFAULT_TEMPERATURE,
    ) -> dict:
        """
        RAG 问答：检索 + LLM 生成。

        Returns:
            {"status": "ok", "question": "...", "answer": "...",
             "sources": ["path1", ...]}
        """
        stats = self.get_stats()
        if stats["chunk_count"] == 0:
            return {
                "status": "empty",
                "message": f"集合 '{self.collection_name}' 中没有文档。请先运行 index。",
            }

        chain = self._build_chain(k, temperature)

        try:
            answer = chain.invoke(question)
        except Exception as e:
            return {"status": "error", "message": f"LLM 调用失败：{e}"}

        # 获取来源文档（通过相似度搜索拿到原始 source）
        raw_docs = self._vectorstore.similarity_search(question, k=k)
        sources = []
        seen = set()
        for doc in raw_docs:
            src = doc.metadata.get("source", "unknown")
            if src not in seen:
                sources.append(src)
                seen.add(src)

        return {
            "status": "ok",
            "question": question,
            "answer": answer,
            "sources": sources,
        }

    def similarity_search(
        self,
        query_text: str,
        k: int = config.DEFAULT_K,
    ) -> dict:
        """
        纯检索（不用 LLM），返回最相关的文档片段。

        Returns:
            {"status": "ok", "results": [
                {"content": "...", "source": "...", "score": 0.92}, ...
            ]}
        """
        stats = self.get_stats()
        if stats["chunk_count"] == 0:
            return {
                "status": "empty",
                "message": f"集合 '{self.collection_name}' 中没有文档。",
            }

        docs_with_scores = self._vectorstore.similarity_search_with_score(
            query_text, k=k
        )

        results = []
        for doc, score in docs_with_scores:
            results.append({
                "content": doc.page_content[:500],
                "source": doc.metadata.get("source", "unknown"),
                "score": round(float(score), 4),
            })

        return {"status": "ok", "results": results}

    # ============================================================
    # 管理
    # ============================================================

    def get_stats(self) -> dict:
        """返回集合统计信息"""
        sources = self.list_sources()["sources"]
        try:
            chunk_count = self._vectorstore._collection.count()
        except Exception:
            chunk_count = 0

        return {
            "status": "ok",
            "collection": self.collection_name,
            "chunk_count": chunk_count,
            "source_count": len(sources),
            "persist_dir": self.persist_dir,
        }

    def list_sources(self) -> dict:
        """返回集合中所有已索引的源文件路径"""
        try:
            data = self._vectorstore.get(include=["metadatas"])
            metadatas = data.get("metadatas", []) or []
            sources = sorted(set(
                m.get("source", "") for m in metadatas if m and m.get("source")
            ))
        except Exception:
            sources = []

        return {"status": "ok", "sources": sources}

    # ============================================================
    # 内部方法
    # ============================================================

    def _load_vectorstore(self):
        """加载或创建 Chroma 向量库"""
        chroma_sqlite = os.path.join(self.persist_dir, "chroma.sqlite3")

        if os.path.exists(chroma_sqlite):
            # 从磁盘加载已有向量库
            self._vectorstore = Chroma(
                persist_directory=self.persist_dir,
                embedding_function=self._get_embeddings(),
            )
        else:
            # 创建空向量库
            self._vectorstore = Chroma(
                persist_directory=self.persist_dir,
                embedding_function=self._get_embeddings(),
            )

    def _get_embeddings(self):
        """懒加载 Embedding 模型（首次调用时才下载 ~80MB）"""
        if self._embeddings is None:
            self._embeddings = HuggingFaceEmbeddings(
                model_name=config.EMBEDDING_MODEL,
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )
        return self._embeddings

    def _get_llm(self, temperature: float = config.DEFAULT_TEMPERATURE):
        """懒加载 LLM"""
        if self._llm is None:
            self._llm = ChatAnthropic(
                model=config.MODEL,
                api_key=config.API_KEY,
                base_url=config.BASE_URL,
                temperature=temperature,
            )
        return self._llm

    def _build_chain(self, k: int, temperature: float):
        """构建 LCEL RAG Chain"""
        retriever = self._vectorstore.as_retriever(search_kwargs={"k": k})
        llm = self._get_llm(temperature)

        template = """你是一个文档问答助手。根据以下上下文回答问题。
如果上下文中没有答案，请如实说「文档中未找到相关信息」。

上下文：
{context}

问题：{question}

回答："""

        prompt = ChatPromptTemplate.from_template(template)

        def format_docs(docs):
            parts = []
            for doc in docs:
                src = doc.metadata.get("source", "unknown")
                parts.append(f"【来源：{src}】\n{doc.page_content}")
            return "\n\n".join(parts)

        chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        return chain
