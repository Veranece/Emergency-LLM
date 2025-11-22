import os
from glob import glob #遍历文件夹下的所有文件
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import  PyMuPDFLoader , Docx2txtLoader ,TextLoader,JSONLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import ModelScopeEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain_text_splitters import SpacyTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter
os.environ["CUDA_VISIBLE_DEVICES"] = "2"
import os
import json
from pathlib import Path
from openai import OpenAI
from langchain.embeddings import HuggingFaceEmbeddings

from langchain_openai import ChatOpenAI
chat=ChatOpenAI(
        model="qwen",
        openai_api_key="EMPTY",
        openai_api_base='http://218.199.69.86:8000/v1',
        stop=['<|im_end|>'],
        temperature=0.2
    )
client = OpenAI(
    api_key="sk-0b64067618f049a8888ceea7e19015f9",  # 如果您没有配置环境变量，请在此处替换您的API-KEY
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 填写DashScope服务base_url
)
# local_model_path = "/home/jiaowu/model/maidalun/bce-embedding-base_v1"
# embeddings = ModelScopeEmbeddings(model_id='maidalun/bce-embedding-base_v1', local_model_dir=local_model_path)
embeddings=HuggingFaceEmbeddings(model_name='/home/jiaowu/model/maidalun/bce-embedding-base_v1')
# 定义文本分割器
# text_splitter = RecursiveCharacterTextSplitter(
#     chunk_size = 500, #块的大小
#     chunk_overlap = 150#重叠部分
# )
text_splitter = SpacyTextSplitter(chunk_size=500,
                                chunk_overlap=150,
                                pipeline="/home/jiaowu/model/zh_core_web_sm-3.8.0/zh_core_web_sm/zh_core_web_sm-3.8.0")
def doc2vec():
    
    # text_splitter = CharacterTextSplitter(
    #     separator="\n\n",
    #     chunk_size=200,
    #     chunk_overlap=50,
    #     length_function=len,
    #     is_separator_regex=False,
    # )
    # 语义分割
    # text_splitter = SpacyTextSplitter(chunk_size=500,
    #                                   chunk_overlap=150,
    #                                   pipeline="/home/jiaowu/model/zh_core_web_sm-3.8.0/zh_core_web_sm/zh_core_web_sm-3.8.0")
  
    # 读取并分割文件
    dir_path = '/home/jiaowu/model/规章制度分类文件' #目录的路径
    documents = []
    print(dir_path)
    
 
# # 遍历文件列表，输出文件名
    for foldername, subfolders, filenames in os.walk(dir_path):
        for filename in filenames:
            file = os.path.join(foldername, filename)
            
            loader = None
            if '.pdf' in file:
                print(file)
                loader = PyPDFLoader(file)
                
            if '.docx' in file:
                print(file)
                loader = Docx2txtLoader(file)
            if '.txt' in file:
                print(file)
                loader = TextLoader(file)
                
            if loader:
                documents += loader.load_and_split(text_splitter)
    # file_path = ("LLM.pdf")
    # loader = PyPDFLoader(file_path)
    # documents = loader.load_and_split(text_splitter)
  
   
    
    if documents:
        # i=0
        # for doc in documents:
            
        #     # if i > 0 and i < len(documents) - 1:
        #     #     doc_total=doc.page_content + " " + documents[i-1].page_content + " " + documents[i+1].page_content
        #     #     question_total = create_question(doc_total)
                
        #     #     doc.page_content += f"\n{question_total}"
        #     #     if i == 1:
        #     #         documents[i-1].page_content += f"\n{question_total}"
        #     #     if i == len(documents) - 2:
        #     #         documents[i+1].page_content += f"\n{question_total}"
        #     # import ipdb
        #     # ipdb.set_trace()
        #     question = create_question(doc.page_content)
        #     # description = create_description(doc.page_content)
        #     doc.metadata['query']=question
        #     # doc.metadata['document description']=description
        #     # doc.metadata['source']=''
        #     # doc.page_content += f"\n{question}"
        #     i += 1
        #     print(i)
        #     break
        vdb = Chroma(
            embedding_function=embeddings,
            # db_250_50_2:8_query query和文档向量2：8 
            # db_350_50_2:8_query query和文档向量2：8 llm-embedder
            # db_500_150_query 只有query
            persist_directory=os.path.join(os.path.dirname(__file__),'db_500_150_query')
        )
        vdb.add_documents(documents=documents)    
        vdb.persist()
        print(1)
# 去除多余的换行
def remove_excess_blank_lines(file_path):
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 去除所有空行
    filtered_lines = [line for line in lines if line.strip() != '']

    # 写入新内容到文件
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(filtered_lines)
def create_question(text):
    """
    文件上传并获取响应。
    :param file_path: 文件的路径
    :return: 模拟的响应（包含JSON格式的数据）
    """
    try:
        prompt = PromptTemplate.from_template('''
                    假如你是华中农业大学的学生或老师，
                    请你根据上传的文本内容帮我生成10个根据文本内容能够回答的教务相关的问题，
                    并使用字符串的方式输出,返回的只有10个问题：
                    文本内容:{text}
        ''')
        inputs = {
            'text':text
            }
        # print(inputs)
        formatted_prompt = prompt.format(text=inputs['text'])
        return chat.invoke(formatted_prompt).content
        
    except Exception as e:
        print(f"无法回答问题: {e}")
        return None
def add(path):
    document = Chroma(
            persist_directory="/home/jiaowu/model/db_500_150_emb",
            embedding_function=embeddings
        )
    documents = []
    for foldername, subfolders, filenames in os.walk(path):
        for filename in filenames:
            file = os.path.join(foldername, filename)
            
            loader = None
            if '.pdf' in file:
                print(file)
                loader = PyPDFLoader(file)
                
            if '.docx' in file:
                print(file)
                loader = Docx2txtLoader(file)
            if '.txt' in file:
                print(file)
                loader = TextLoader(file)
                
            if loader:
                documents += loader.load_and_split(text_splitter)
    document.add_documents(documents=documents) 
    document.persist()
if __name__ == '__main__':
    doc2vec()
    print('faiss saved!')
    
    # 处理文件
    # dir_path = '/home/jiaowu/model/规章制度分类文件/导师 手册' #目录的路径
    # add(dir_path)
    # print('faiss saved!')
    # documents = []
    # print(dir_path)
    
    # # # 遍历文件列表，输出文件名
    # for foldername, subfolders, filenames in os.walk(dir_path):
    #     for filename in filenames:
    #         file = os.path.join(foldername, filename)
    #         remove_excess_blank_lines(file)
