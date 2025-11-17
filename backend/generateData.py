import os
import subprocess
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import Docx2txtLoader, TextLoader, PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from processImg import process

# 设置 HuggingFace 镜像
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

# 向量模型
embedding_model = HuggingFaceEmbeddings(
    model_name="/New_Disk/liziwei/maidalun1020/bce-embedding-base_v1",
    model_kwargs={"device": "cuda"},
    encode_kwargs={"normalize_embeddings": True}
)

# 文本切分器
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=50,
    length_function=len,
    separators=["\n\n", "\n", ".", "!", "?"]
)

# 目标文件夹
dir_path = '/home/liziwei/Emergency-LLM/backend/resource/data'

all_documents = []

# 遍历目录及子目录
for foldername, subfolders, filenames in os.walk(dir_path):
    for filename in filenames:
        file_path = os.path.join(foldername, filename)
        loader = None

        if filename.endswith(".pdf"):
            print("加载 PDF:", file_path)
            loader = PyPDFLoader(file_path)
        elif filename.endswith(".docx"):
            print("加载 DOCX:", file_path)
            loader = Docx2txtLoader(file_path)
        elif filename.endswith(".txt"):
            print("加载 TXT:", file_path)
            loader = TextLoader(file_path)
        elif filename.endswith(".wps") or filename.endswith(".doc"):
            # 转换成 docx
            out_file = os.path.splitext(file_path)[0] + ".docx"
            print(f"转换 {file_path} -> {out_file}")
            try:
                subprocess.run(
                    ["libreoffice", "--headless", "--convert-to", "docx", "--outdir", foldername, file_path],
                    check=True
                )
                loader = Docx2txtLoader(out_file)
                # 删除原始文件
                os.remove(file_path)
                print(f"已删除原文件: {file_path}")
            except subprocess.CalledProcessError:
                print(f"文件转换失败: {file_path}, 已跳过")
                continue
            except Exception as e:
                print(f"删除原文件失败: {file_path}, 原因: {e}")
                continue
        else:
            print("未知格式文件，跳过:", file_path)
            continue

        if loader:
            try:
                docs = loader.load_and_split(text_splitter)
                for doc in docs:
                    doc.metadata["source"] = file_path
                all_documents.extend(docs)
            except Exception as e:
                print(f"加载失败: {file_path}, 原因: {e}")

# 创建向量数据库
if all_documents:
    vdb = Chroma.from_documents(
        documents=all_documents,
        embedding=embedding_model,
        persist_directory="/home/liziwei/Emergency-LLM/backend/vdb"
    )
    vdb.persist()
    print("向量数据库创建成功！")
else:
    print("没有找到任何可处理的文件。")
