from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_deepseek import ChatDeepSeek
embeddings = HuggingFaceEmbeddings(
    model_name="/New_Disk/liziwei/maidalun1020/bce-embedding-base_v1",
    model_kwargs={"device": "cuda"},
    encode_kwargs={"normalize_embeddings": True}
)

documents = Chroma(
            persist_directory="/home/liziwei/Emergency-LLM/backend/vdb",
            embedding_function=embeddings)

chat = ChatDeepSeek(
    model="DeepSeek-R1-32B",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key="sk-Fv82iZRBXfcO0w20C2Ff952c7a4e4bB2B953C19161A31061",
    api_base="http://chat.hzau.edu.cn:3000/v1",
    streaming=True, 
)

query = "省应急厅、省粮储局按各自职责做好什么工作？"
docs = documents.similarity_search(query,k=1)
print(docs[0].page_content)
prompt = f"""请根据以下文档内容，总结关于'{query}'的信息：

文档内容：
{docs[0].page_content}

请用简洁明了的语言进行总结。"""

print(chat.invoke(prompt).content)