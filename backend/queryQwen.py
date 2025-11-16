from openai import OpenAI
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_deepseek import ChatDeepSeek

openai_api_key = "EMPTY"
openai_api_base = "http://localhost:8000/v1"

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

embeddings = HuggingFaceEmbeddings(
    model_name="/New_Disk/liziwei/maidalun1020/bce-embedding-base_v1",
    model_kwargs={"device": "cuda"},
    encode_kwargs={"normalize_embeddings": True}
)

documents = Chroma(
            persist_directory="/home/liziwei/Emergency-LLM/backend/vdb",
            embedding_function=embeddings)


query = "省应急厅、省粮储局按各自职责做好什么工作？"

docs = documents.similarity_search(query, k=1)

print("来源：", docs[0].metadata.get("source").split('/')[-1])


# 让大模型生成回答
chat_response = client.chat.completions.create(
     model="/New_Disk/liuyingchang/model/models/Qwen/Qwen3-32B-AWQ",
    messages=[
        {"role": "system", "content": "你是一个专业的问答助手，请根据用户提供的上下文回答问题。"},
        {"role": "user", "content": f"问题: {query}\n\n背景知识:\n{docs[0].page_content}\n\n来源: {docs[0].metadata.get('source')}"}
    ],
    max_tokens=8192,
    temperature=0.7,
    top_p=0.8,
    presence_penalty=1.5,
    extra_body={
        "top_k": 20, 
        "chat_template_kwargs": {"enable_thinking": False},
    },
)

print("-------------------------------------------------------------")
generated_text = chat_response.choices[0].message.reasoning_content
print(generated_text)
