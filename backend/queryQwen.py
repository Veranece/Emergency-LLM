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


# query = "四不放过”原则是什么"
query = "篷体面料（PU涂层布）需要满足哪些关键性能指标"

docs = documents.similarity_search(query, k=1)
print(docs[0].page_content)
print("---------------------------------------------")
print("问题：",query)
print("来源：", docs[0].metadata.get("source").split('/')[-1])

system_prompt = "你是应急管理领域的专业顾问，请根据用户提供的上下文回答问题，回答要专业、条理清晰。"
prompt_normal = f"问题: {query}\n\n背景知识:\n{docs[0].page_content}"
prompt_case = f"""
请结合以下背景知识，针对给定情景输出所需装备参数、操作流程及注意事项，要求专业、条理清晰,返回使用markdown语法，主要参考背景知识，不要使用其他来源的知识。：

背景知识:
{docs[0].page_content}

情景描述:
{query}
"""
# 让大模型生成回答
chat_response = client.chat.completions.create(
    model="/New_Disk/liuyingchang/model/models/Qwen/Qwen3-32B-AWQ",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt_case}
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
