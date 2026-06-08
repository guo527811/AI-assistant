"""
RAG 文档问答系统 — 面试作品 #2
技术栈：LangChain + Chroma + Claude API

使用方式：
  1. pip install langchain langchain-community langchain-anthropic langchain-openai chromadb
  2. 设置环境变量 ANTHROPIC_API_KEY 和 OPENAI_API_KEY
  3. python rag_demo.py <文档路径>

示例：
  python rag_demo.py E:/AI助手/构想.md
"""

import sys
import os
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


# ============================================
# Step 1: 加载文档
# ============================================
def load_documents(file_path: str):
    """加载 PDF 或文本文件"""
    print(f"📂 加载文档：{file_path}")
    if file_path.endswith('.pdf'):
        loader = PyPDFLoader(file_path)
    else:
        loader = TextLoader(file_path, encoding='utf-8')
    docs = loader.load()
    print(f"   文档加载完成，共 {len(docs)} 页/段")
    return docs


# ============================================
# Step 2: 分块
# ============================================
def split_documents(docs, chunk_size=500, chunk_overlap=50):
    """将长文档切成小块"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", "。", "！", "？", ".", " ", ""]
    )
    chunks = text_splitter.split_documents(docs)
    print(f"✂️  文档分块完成：{len(chunks)} 个块（chunk_size={chunk_size}, overlap={chunk_overlap}）")
    return chunks


# ============================================
# Step 3: 向量化 + 存储
# ============================================
def create_vectorstore(chunks, persist_dir="./chroma_db"):
    """将文本块转为向量并存入 Chroma"""
    print("🧮 向量化中（调用 OpenAI Embedding API）...")
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_dir
    )
    print(f"   向量库创建完成，持久化目录：{persist_dir}")
    return vectorstore


# ============================================
# Step 4: 构建 RAG Chain
# ============================================
def build_rag_chain(vectorstore, k=4):
    """构建 RAG 问答链"""
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    llm = ChatAnthropic(model="claude-sonnet-4-6", temperature=0.3)

    template = """你是一个文档问答助手。根据以下上下文回答问题。
如果上下文中没有答案，请如实说「文档中未找到相关信息」。

上下文：
{context}

问题：{question}

回答："""

    prompt = ChatPromptTemplate.from_template(template)

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    print(f"🔗 RAG Chain 构建完成（检索 Top-{k}）")
    return chain


# ============================================
# Step 5: 交互问答
# ============================================
def interactive_qa(chain):
    """交互式问答循环"""
    print("\n" + "=" * 60)
    print("💬 RAG 问答系统已就绪！输入问题开始（输入 'quit' 退出）")
    print("=" * 60 + "\n")

    while True:
        try:
            question = input("❓ 你的问题：").strip()
            if question.lower() in ('quit', 'exit', 'q'):
                print("👋 再见！")
                break
            if not question:
                continue

            answer = chain.invoke(question)
            print(f"\n💬 回答：{answer}\n")
            print("-" * 60 + "\n")

        except KeyboardInterrupt:
            print("\n👋 再见！")
            break


# ============================================
# Main
# ============================================
if __name__ == "__main__":
    # 检查环境变量
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("⚠️  请设置环境变量 ANTHROPIC_API_KEY")
        sys.exit(1)
    if not os.environ.get("OPENAI_API_KEY"):
        print("⚠️  请设置环境变量 OPENAI_API_KEY")
        sys.exit(1)

    # 获取文档路径
    if len(sys.argv) < 2:
        print("用法：python rag_demo.py <文档路径>")
        print("示例：python rag_demo.py E:/AI助手/构想.md")
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在：{file_path}")
        sys.exit(1)

    # 构建 RAG 流水线
    print("\n🚀 RAG 文档问答系统启动")
    print("=" * 60)

    docs = load_documents(file_path)
    chunks = split_documents(docs)
    vectorstore = create_vectorstore(chunks)
    chain = build_rag_chain(vectorstore)

    # 进入交互问答
    interactive_qa(chain)
