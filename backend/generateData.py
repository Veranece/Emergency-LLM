import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com' 

from langchain_community.vectorstores import Chroma
# from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import SpacyTextSplitter


# loader = Docx2txtLoader()
loader = PyPDFLoader("/home/liziwei/Emergency-LLM/backend/resource/省十四届人大三次会议《关于加快应急预案体系建设的建议》（第1431408号）答复.pdf")
documents = loader.load()


model = HuggingFaceEmbeddings(
    model_name="/New_Disk/liziwei/maidalun1020/bce-embedding-base_v1",
    model_kwargs={"device": "cuda"},
    encode_kwargs={"normalize_embeddings": True}
)

text_splitter = SpacyTextSplitter(
    chunk_size=200,
    chunk_overlap=50,
    pipeline="zh_core_web_sm"
)


# 3. 创建向量数据库
vdb = Chroma.from_documents(
    documents=text_splitter.split_documents(documents),
    embedding=model,
    persist_directory="/home/liziwei/Emergency-LLM/backend/vdb"
)

# vdb.persist()
print("向量数据库创建成功！")
