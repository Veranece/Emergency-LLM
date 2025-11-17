import os
import subprocess
import pandas as pd
from paddleocr import PaddleOCR
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import Docx2txtLoader, TextLoader, PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# =======================
# OCR 初始化
# =======================
ocr = PaddleOCR(use_angle_cls=True, lang='ch', use_gpu=True)

def ocr_image_to_txt(img_path):
    """对图片执行 OCR 并生成同名 TXT 文件"""
    txt_file = os.path.splitext(img_path)[0] + ".txt"
    if os.path.exists(txt_file):
        return txt_file

    result = ocr.ocr(img_path, cls=True)
    with open(txt_file, "w", encoding="utf-8") as f:
        if result:
            for line in result[0]:
                f.write(line[1][0] + "\n")
    return txt_file

def excel_to_txt(file_path):
    """将 Excel 文件转换为 TXT，每行拼接单元格"""
    try:
        xls = pd.ExcelFile(file_path)
        texts = []
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
            for row in df.itertuples(index=False):
                row_text = "\t".join([str(cell) for cell in row if pd.notna(cell)])
                if row_text.strip():
                    texts.append(row_text)
        txt_file = os.path.splitext(file_path)[0] + ".txt"
        with open(txt_file, "w", encoding="utf-8") as f:
            f.write("\n".join(texts))
        return txt_file
    except Exception as e:
        print(f"Excel 处理失败: {file_path}, 原因: {e}")
        return None

def csv_to_txt(file_path):
    encodings = ['utf-8', 'gbk', 'gb2312', 'latin1']
    
    # 检测编码
    try:
        import chardet
        with open(file_path, 'rb') as f:
            encodings.insert(0, chardet.detect(f.read())['encoding'])
    except: pass
    
    # 尝试读取
    for enc in encodings:
        try:
            # 检测标题
            with open(file_path, 'r', encoding=enc, errors='replace') as f:
                has_header = ',' in f.readline()
            
            # 读取转换
            df = pd.read_csv(file_path, header=(0 if has_header else None), encoding=enc, on_bad_lines='skip')
            texts = []
            
            # 处理数据
            if has_header and len(df.columns) > 0:
                texts.append("\t".join(str(col) for col in df.columns))
            
            for row in df.itertuples(index=False):
                text = "\t".join(str(cell) for cell in row if pd.notna(cell))
                if text: texts.append(text)
            
            # 保存
            txt_file = os.path.splitext(file_path)[0] + ".txt"
            with open(txt_file, "w", encoding="utf-8") as f:
                f.write("\n".join(texts))
            return txt_file
        except Exception:
            continue
    
    return None


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=50,
    length_function=len,
    separators=["\n\n", "\n", ".", "!", "?"]
)

os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
embedding_model = HuggingFaceEmbeddings(
    model_name="/New_Disk/liziwei/maidalun1020/bce-embedding-base_v1",
    model_kwargs={"device": "cuda"},
    encode_kwargs={"normalize_embeddings": True}
)

# =======================
# 遍历目录处理文件
# =======================
dir_path = '/home/liziwei/Emergency-LLM/backend/resource/data'
all_documents = []

for foldername, subfolders, filenames in os.walk(dir_path):
    for filename in filenames:
        file_path = os.path.join(foldername, filename)
        loader = None
        lower_name = filename.lower()

        if lower_name.endswith((".png", ".jpg", ".jpeg", ".bmp")):
            txt_file = ocr_image_to_txt(file_path)
            loader = TextLoader(txt_file)
        elif lower_name.endswith((".xls", ".xlsx")):
            txt_file = excel_to_txt(file_path)
            loader = TextLoader(txt_file)
        elif lower_name.endswith(".csv"):
            txt_file = csv_to_txt(file_path)
            if txt_file:
                loader = TextLoader(txt_file)
            else:
                continue
        elif lower_name.endswith(".pdf"):
            print("加载 PDF:", file_path)
            loader = PyPDFLoader(file_path)
        elif lower_name.endswith(".docx"):
            print("加载 DOCX:", file_path)
            loader = Docx2txtLoader(file_path)
        elif lower_name.endswith(".txt"):
            loader = TextLoader(file_path)
        elif lower_name.endswith((".wps", ".doc")):
            out_file = os.path.splitext(file_path)[0] + ".docx"
            try:
                subprocess.run(
                    ["libreoffice", "--headless", "--convert-to", "docx", "--outdir", foldername, file_path],
                    check=True
                )
                loader = Docx2txtLoader(out_file)
                os.remove(file_path)
            except Exception as e:
                print(f"文件处理失败: {file_path}, 原因: {e}")
                continue
        else:
            print("未知格式文件，跳过:", file_path)
            continue

        # 文档切分 & 添加 source 元数据
        if loader:
            try:
                docs = loader.load_and_split(text_splitter)
                for doc in docs:
                    doc.metadata["source"] = file_path
                all_documents.extend(docs)
            except Exception as e:
                print(f"加载失败: {file_path}, 原因: {e}")

# =======================
# 创建向量数据库
# =======================
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
