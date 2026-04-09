import logging
from pathlib import Path
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from utils.config import GLOBAL_CONFIG

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FAISS_INDEX_PATH=PROJECT_ROOT / "data/faiss_index"
TEXT_PATH=PROJECT_ROOT/ "data/knowledge.txt"

MODEL=None

def create_embaddings_model():
    """
    创建并返回embaddings实例，使用全局变量缓存模型以避免重复加载
    """
    global MODEL
    if MODEL is None:
        MODEL = HuggingFaceEmbeddings(
            model_name=GLOBAL_CONFIG.get("rag", {}).get("model_name")
        )
        logging.info("embaddings模型下载完成")
    return MODEL


def build_vector_store():
    """
    将知识库存入向量数据库
    :return:
    """
    logging.info("进入rag模块")
    #加载文档

    loader = TextLoader(TEXT_PATH,autodetect_encoding=True)

    documents=loader.load()

    #文本切分
    text_splitter=RecursiveCharacterTextSplitter(
        chunk_size=GLOBAL_CONFIG.get("rag",{}).get("chunk_size"),
        chunk_overlap=GLOBAL_CONFIG.get("rag",{}).get("chunk_overlap"),
    )

    chunks = text_splitter.split_documents(documents)
    logging.info("切分完成，得到%d个文本块", len(chunks))

    #TODO：改成本地部署
    embaddings = create_embaddings_model()

    #存入FAISS
    vector_store=FAISS.from_documents(chunks,embaddings)
    vector_store.save_local(str(FAISS_INDEX_PATH))
    logging.info("向量索引已保存至 %s 目录",FAISS_INDEX_PATH)

    return vector_store


def load_vector_store():
    """
    加载已保存的向量数据库
    """
    # 使用相同的embedding模型
    embeddings = create_embaddings_model()

    # 加载FAISS索引
    vector_store = FAISS.load_local(
        str(FAISS_INDEX_PATH),
        embeddings,
        allow_dangerous_deserialization=True  # FAISS需要这个参数
    )
    return vector_store


def retrieve_relevant_docs(query, vector_store, k=3):
    """
    检索相关文档
    :param query: 用户问题
    :param vector_store: 向量数据库
    :param k: 返回最相关的k个文档块
    """
    # 相似度检索
    docs = vector_store.similarity_search(query, k=k)

    # 简单打印来源
    logging.info(f"\n📚 参考来源（共{len(docs)}条）：")
    for i, doc in enumerate(docs, 1):
        # 获取来源文件名
        source = doc.metadata.get('source', '未知')
        source_name = Path(source).name if source != '未知' else 'knowledge.txt'
        # 打印前100个字符作为预览
        preview = doc.page_content[:100].replace('\n', ' ')
        logging.info(f"{i}. [{source_name}] {preview}...")

    return docs


def build_rag_prompt(query, retrieved_docs):
    """
    构建RAG提示词
    """
    # 提取文档内容
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])

    # 构建提示词
    prompt =GLOBAL_CONFIG.get("prompt",{}).get("kurisu")+ f"""基于以下已知信息，回答问题。如果无法从已知信息中找到答案，请诚实地说"根据现有知识无法回答该问题"。

            已知信息：
            {context}

            问题：{query}"""

    logging.info(f"rag检索后的提示词为{prompt}")

    return prompt





