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
    try:
        embaddings = HuggingFaceEmbeddings(
            model_name=GLOBAL_CONFIG.get("rag", {}).get("model_name")
        )
    except Exception as err:
        logging.error(err.with_traceback(err.__traceback__))
    logging.info("embaddings模型下载完成")

    #存入FAISS
    vector_store=FAISS.from_documents(chunks,embaddings)
    vector_store.save_local(str(FAISS_INDEX_PATH))
    logging.info("向量索引已保存至 %s 目录",FAISS_INDEX_PATH)

    return vector_store


