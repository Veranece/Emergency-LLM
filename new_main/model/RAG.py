# -*- coding: utf-8 -*-
# 使用旧版langchain的导入路径
# 在新版langchain中，这些组件已经移动到langchain_classic.agents
from langchain_classic.agents import ZeroShotAgent, AgentExecutor, Tool, initialize_agent
from langchain_classic.agents.agent_types import AgentType
import gradio as gr
import re
from langchain_classic.memory import ConversationBufferMemory
# 删除hub导入
# import time
# from bs4 import BeautifulSoup
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from sentence_transformers import CrossEncoder
from langchain_core.prompts import ChatPromptTemplate
# 旧版本langchain中没有StrOutputParser
import os
from langchain_classic.chains import LLMChain
import numpy as np
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
load_dotenv()
from langchain_core.prompts import PromptTemplate
from openai import OpenAI
from langchain_classic.chains.llm_requests import LLMRequestsChain
from rank_bm25 import BM25Okapi
import jieba

os.environ['VLLM_USE_MODELSCOPE']='True'
os.environ["LD_LIBRARY_PATH"] = ""

openai_api_key = "EMPTY"
openai_api_base = "http://localhost:8000/v1"

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

embed_model = HuggingFaceEmbeddings(
    model_name="/New_Disk/liziwei/maidalun1020/bce-embedding-base_v1",
    model_kwargs={"device": "cuda"},
    encode_kwargs={"normalize_embeddings": True}
)

from chromadb.api.types import EmbeddingFunction

class LCEmbedding(EmbeddingFunction):
    def __init__(self, embed_model):
        self.embed_model = embed_model
    
    def _convert_to_list(self, obj):
        """递归地将numpy类型转换为Python原生类型"""
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        elif isinstance(obj, list):
            return [self._convert_to_list(item) for item in obj]
        elif isinstance(obj, tuple):
            return tuple(self._convert_to_list(item) for item in obj)
        else:
            return obj

    def embed_query(self, text: str) -> list[float]:
        """嵌入单个查询文本，返回一维向量"""
        result = self.__call__([text])
        return result[0] if result else []
    
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """嵌入多个文档文本，返回二维向量列表"""
        return self.__call__(texts)

    def __call__(self, input: list[str]) -> list[list[float]]:
        embeddings = self.embed_model.embed_documents(input)
        # 将numpy数组转换为纯Python列表
        result = []
        for emb in embeddings:
            # 处理不同格式的embedding
            if isinstance(emb, np.ndarray):
                # 直接是numpy数组，转换为列表
                result.append(emb.tolist())
            elif isinstance(emb, list):
                # 已经是列表，检查是否需要进一步处理
                if len(emb) > 0 and isinstance(emb[0], np.ndarray):
                    # 列表中包含numpy数组，提取第一个
                    result.append(emb[0].tolist())
                elif len(emb) > 0 and isinstance(emb[0], (int, float, np.integer, np.floating)):
                    # 列表中是数字，直接转换
                    result.append([float(x) for x in emb])
                else:
                    # 其他情况，递归转换
                    result.append(self._convert_to_list(emb))
            else:
                # 其他类型，尝试转换
                result.append(self._convert_to_list(emb))
        
        return result

# 创建适配器实例
embedding_model = LCEmbedding(embed_model)


local_model_path = "/New_Disk/liziwei/maidalun1020/bce-reranker-base_v1"
# 重排也有了 也有了索引搜索。 等着整点混合检索
cross_encoder = CrossEncoder(local_model_path,max_length=512)   

class Agent():
    def __init__(self):
        
        self.documents = Chroma(
            persist_directory="/home/liziwei/Emergency-LLM/backend/vdb",
            embedding_function=embedding_model
        )
        
        # 初始化 BM25 索引
        print("正在初始化 BM25 索引...")
        all_docs = self.documents.get()
        self.all_doc_contents = all_docs['documents']  # 所有文档内容
        self.all_doc_metadatas = all_docs['metadatas']  # 所有文档元数据
        
        # 对文档进行分词（中文使用 jieba）
        tokenized_corpus = [list(jieba.cut(doc)) for doc in self.all_doc_contents]
        self.bm25 = BM25Okapi(tokenized_corpus)
        print(f"BM25 索引初始化完成，共 {len(self.all_doc_contents)} 个文档")
    
    def process_stream_response(self, response_stream):
        """
        处理流式响应，提取 content 和 reasoning_content 字段
        返回完整的文本内容
        """
        full_content = ""
        for chunk in response_stream:
            # 打印原始 chunk 用于调试（可选）
            # print(chunk, end="")
            
            # 处理 content 字段（正常内容）
            if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                full_content += chunk.choices[0].delta.content
            # 处理 reasoning_content 字段（Qwen3 模型的思考过程）
            elif hasattr(chunk.choices[0].delta, 'reasoning_content') and chunk.choices[0].delta.reasoning_content:
                full_content += chunk.choices[0].delta.reasoning_content
        
        return full_content
    def format(docs):
        doc_strings = [doc["document"] for doc in docs]
        return "".join(doc_strings)
    def create_documents(self,queries):
        """
        混合检索文档（BM25 + 向量检索）
        
        Args:
            queries: 查询列表
        """
        retrieved_documents = []
        
        for query in queries:
            # 1. BM25 检索
            tokenized_query = list(jieba.cut(query))
            bm25_scores = self.bm25.get_scores(tokenized_query)
            
            # 获取 BM25 top-10 结果并应用元数据过滤
            bm25_top_indices = np.argsort(bm25_scores)[::-1][:10]
            bm25_docs = []
            for idx in bm25_top_indices:
                if self.all_doc_metadatas[idx].get("type") == "Technology":
                    bm25_docs.append(self.all_doc_contents[idx])
                    if len(bm25_docs) >= 5:  # 最多取 5 个
                        break
            
            # 2. 向量检索
            results_vector = self.documents.similarity_search_with_relevance_scores(
                query, 
                k=5,
                filter={"type": "Technology"}
            )
            
            # 打印来源信息
            if results_vector:
                source = results_vector[0][0].metadata.get("source", "未知来源")
                print(f"来源：{source.split('/')[-1] if '/' in source else source}")
            
            vector_docs = [doc[0].page_content for doc in results_vector]
            
            # 3. 合并 BM25 和向量检索结果
            retrieved_documents.extend(bm25_docs)
            retrieved_documents.extend(vector_docs)
        
        # 去重
        unique_documents = []
        for item in retrieved_documents:
            if item not in unique_documents:
                unique_documents.append(item)
        
        # 使用 cross_encoder 重排
        pairs = [[queries[0], doc] for doc in unique_documents]
        scores = cross_encoder.predict(pairs)
        
        # 组合分数和文档
        final_results = [
            {"score": scores[i], "document": unique_documents[i]} 
            for i in range(len(scores))
        ]
        
        # 排序并返回 top-5
        sorted_results = sorted(final_results, key=lambda x: x["score"], reverse=True)
        return sorted_results[:5]

    def create_original_query(self,original_query):
        query = original_query
        qa_system_prompt = PromptTemplate.from_template("""        
        你是一名应急管理领域的专业顾问。你的任务是生成三个与用户问题相差不多的问题，
        例如用户问题为“碰到洪灾天气怎么办”，你可以生成问题“洪灾天气如何应对”，“洪灾天气如何自救”，
        “洪灾天气如何预防”三个问题.以及问题中最重要的2个关键字分块，
        通过对用户问题产生多种视角，您的目标是提供帮助
        用户克服了基于距离的相似性搜索的一些局限性。
        提供这些用换行符分隔的备选问题或分块，返回你生成的问题和分块，生成的问题为1、2、3，生成分块为4和5，一个分块是4，一个分块是5，一个分块是一个关键字，一个分块是关键字
        你需要返回的是3个问题和2个分块其他不需要！！！
        """)
        prompt = qa_system_prompt.format(query = query)
        response = client.chat.completions.create(
            model="/New_Disk/liuyingchang/model/models/Qwen/Qwen3-32B-AWQ",
            messages=[
                {"role": "system", "content": "你是一名应急管理领域的专业顾问。"},
                {"role": "user", "content": prompt}
            ],
            stream=True
        )
        print("获取响应流")
        full_content = ""
        for chunk in response:
            # 处理 content 字段
            if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                full_content += chunk.choices[0].delta.content
            # 处理 reasoning_content 字段（Qwen3 模型的思考过程）
            elif hasattr(chunk.choices[0].delta, 'reasoning_content') and chunk.choices[0].delta.reasoning_content:
                full_content += chunk.choices[0].delta.reasoning_content
        full = full_content


        text_no_think = re.sub(r'<think>.*?</think>', '', full_content, flags=re.S).strip()

        # 2. 按行切分，并去掉空行
        lines = [line.strip() for line in text_no_think.splitlines() if line.strip()]
        
        # 3. 只保留以数字开头的行（1. 2. 3. 4. 5.）
        filtered_lines = []
        seen_numbers = set()
        
        for line in lines:
            # 检查是否以"数字."开头
            match = re.match(r'^(\d+)\.\s*(.+)', line)
            if match:
                number = match.group(1)
                content = match.group(2)
                # 避免重复的编号，只保留前5个
                if number not in seen_numbers and int(number) <= 5:
                    seen_numbers.add(number)
                    filtered_lines.append(line)
        
        # 确保返回的结果按编号排序
        filtered_lines.sort(key=lambda x: int(re.match(r'^(\d+)\.', x).group(1)))
        
        return filtered_lines


    def retrival_func_01(self,query,history):
        """
        检索并回答问题
        
        Args:
            query: 用户查询
            history: 历史对话
        """
        print("query:",query)
        queries = self.create_original_query(query)
        data = self.create_documents(query)
        print("data:",data)
        query_result = "\n\n".join(item['document'] for item in data)
        system_prompt = "你是应急管理领域的专业顾问，请根据用户提供的上下文回答问题，回答要专业、条理清晰。"
        prompt_normal = f"问题: {query}\n\n背景知识:\n{query_result}"
        prompt_case = f"""
        1.请结合以下背景知识，针对给定情景输出所需装备参数、操作流程及注意事项，要求专业、条理清晰：
        2.如果上下文不够准确，请返回 ‘我不确定 / 没有足够信息’

        背景知识:
        {query_result}

        情景描述:
        {query}
        """
        response = client.chat.completions.create(
            model="/New_Disk/liuyingchang/model/models/Qwen/Qwen3-32B-AWQ",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt_normal}
            ],
            stream=True
        )
        return response

    def retrival_func_02(self,query,history):
        print("进入retrival_func_02")
        """
        检索并回答问题（方法2）
        
        Args:
            query: 用户查询
            history: 历史对话
        """
        queries = self.create_original_query(query)
        print(queries)
        data = self.create_documents(queries)
        # data = self.create_documents(query)
        
        
        query_result = "\n\n".join(item['document'] for item in data)
        print(query_result)
        prompt = PromptTemplate.from_template('''
            1.请根据以下检索结果，回答用户问题，严格按照用户问题来回答，确保回答准确无误。
            2.检索结果中没有相关信息时，回复“抱歉我暂时无法回答你的问题，如果你想了解更多请去华中农业大学官网”。
            3.当你被人问起身份时（你是谁？你是干嘛的？等），请记住你来自华中农业大学信息学院，是一个教育大模型,是华中农业大学信息学院开发的（不用遵守规则2）。
            4.你必须拒绝讨论任何关于政治，色情，暴力相关的事件或者人物。
            ----------
            用户问题：{query}                                                                  
            ----------
            检索结果：{query_result}
            -----------

            输出：<think>
        ''')

        
        
        inputs = {
                'query': query,
                # 'query_source':query_source,
                'query_result': ''.join(query_result) if len(query_result) else '没有查到'
                
            }
        # print(inputs)
        formatted_prompt = prompt.format(query=inputs['query'], query_result=inputs['query_result'])
        response = client.chat.completions.create(
            model="/New_Disk/liuyingchang/model/models/Qwen/Qwen3-32B-AWQ",
            messages=[
                {"role": "system", "content": "你是一名华中农业大学教务助理。"},
                {"role": "user", "content": formatted_prompt}
            ],
            stream=True
        )                                
        return response

    def query_result_doc(self,query):
        """
        基于假设性文档的检索
        
        Args:
            query: 用户查询

        """
        prompt_01 = PromptTemplate.from_template('''
            你是一个华中农业大学教务方面的智能助手请你根据问题回答：
                用户问题：{query}    
            如果你无法回答请根据问题生成一个可以回答这个问题的假设性文档
        ''')
        inputs = {
                'query': query,
            }
        formatted_prompt_01 = prompt_01.format(query=inputs['query'])
        response = client.chat.completions.create(
            model="/New_Disk/liuyingchang/model/models/Qwen/Qwen3-32B-AWQ",
            messages=[
                {"role": "system", "content": "你是一名华中农业大学教务助理。"},
                {"role": "user", "content": formatted_prompt_01}
            ],
        )
        LLM_result = response.choices[0].message.content
        print(LLM_result)
        print("------------------")
        queries = self.create_original_query(query)
        print(queries)

        data = self.create_documents(queries) 
        # print(data)
        
        # LLM 生成的假设性文档也按类型过滤
        LLM_doc = self.documents.similarity_search_with_score(
                LLM_result, 
                k=3, 
                filter={"type":"Technology"}
            )
        LLM_result_string = [doc[0].page_content for doc in LLM_doc]
        query_result_01 = "\n\n".join(item['document'] for item in data)
        query_result = '\n'.join(LLM_result_string) + '\n' + query_result_01
        return query_result

    def retrival_func(self,query,history): 
        query_result = self.query_result_doc(query)
        prompt = PromptTemplate.from_template('''
            1.请根据以下检索结果，回答用户问题，严格按照用户问题来回答，确保回答准确无误。
            2.检索结果中没有相关信息时，回复“抱歉我暂时无法回答你的问题，如果你想了解更多请去华中农业大学官网”。
            3.当你被人问起身份时，请记住你来自华中农业大学信息学院，是一个教育大模型,是华中农业大学信息学院开发的。
            4.你必须拒绝讨论任何关于政治，色情，暴力相关的事件或者人物。
            ----------
            用户问题：{query}                                                                  
            ----------
            检索结果：{query_result}
            -----------

            输出：
        ''')

        inputs = {
                'query': query,
                # 'query_source':query_source,
                'query_result': query_result  
            }
        formatted_prompt = prompt.format(query=inputs['query'], query_result=inputs['query_result']
                                        )
        response = client.chat.completions.create(
            model="/New_Disk/liuyingchang/model/models/Qwen/Qwen3-32B-AWQ",
            messages=[
                {"role": "system", "content": "你是一名华中农业大学教务助理。"},
                {"role": "user", "content": formatted_prompt}
            ],
            stream=True
        )
        return response
    def search_func(self,x,query):
            prompt = PromptTemplate.from_template('''请根据以下检索结果，回答用户问题，不要发散和联想内容。
                    检索结果中没有相关信息时，回复"不知道"。
                    ----------
                    检索结果：{query_result}
                    ----------
                    用户问题：{query}
                    -----------
                    输出：''')
            # 由于我们不再使用LangChain的chat模型，这里需要重新实现LLMChain的功能
            def custom_llm_chain(prompt_template, query, query_result):
                formatted_prompt = prompt_template.format(query=query, query_result=query_result)
                response = client.chat.completions.create(
                    model="/New_Disk/liuyingchang/model/models/Qwen/Qwen3-32B-AWQ",
                    messages=[
                        {"role": "system", "content": "你是一名华中农业大学教务助理。"},
                        {"role": "user", "content": formatted_prompt}
                    ],
                )
                return response.choices[0].message.content
      
            # 自定义的请求链
            import requests
            from bs4 import BeautifulSoup
            
            url = 'https://www.sogou.com/web?query=' + query
            try:
                response = requests.get(url)
                soup = BeautifulSoup(response.text, 'html.parser')
                # 提取搜索结果文本
                search_results = soup.get_text()[:5000]  # 限制长度
                
                # 使用我们的自定义LLM链
                result = custom_llm_chain(prompt, query, search_results)
                return result
            except Exception as e:
                return f"搜索失败: {str(e)}"
    def search_web_func(self,query):
            prompt = PromptTemplate.from_template('''请根据以下检索结果，回答用户问题，不要发散和联想内容。
                    检索结果中没有相关信息时，回复"不知道"。
                    ----------
                    检索结果：{query_result}
                    ----------
                    用户问题：{query}
                    -----------
                    输出：''')
                    
            # 自定义的请求链
            import requests
            from bs4 import BeautifulSoup
            
            url = 'https://www.sogou.com/web?query=' + query
            try:
                response = requests.get(url)
                soup = BeautifulSoup(response.text, 'html.parser')
                # 提取搜索结果文本
                search_results = soup.get_text()[:5000]  # 限制长度
                
                # 使用OpenAI客户端直接调用
                formatted_prompt = prompt.format(query=query, query_result=search_results)
                api_response = client.chat.completions.create(
                    model="/New_Disk/liuyingchang/model/models/Qwen/Qwen3-32B-AWQ",
                    messages=[
                        {"role": "system", "content": "你是一名华中农业大学教务助理。"},
                        {"role": "user", "content": formatted_prompt}
                    ],
                )
                return api_response.choices[0].message.content
            except Exception as e:
                return f"搜索失败: {str(e)}"
    def generic_func(self,x,query,return_stream=True):
            """
            通用功能函数，用于回答非专业领域的问题
            
            Args:
                x: 占位参数（Tool接口需要）
                query: 用户查询
                return_stream: 是否返回流式对象。True返回流式对象，False返回处理后的文本
            
            Returns:
                如果 return_stream=True，返回流式响应对象
                如果 return_stream=False，返回处理后的文本字符串
            """
            prompt = PromptTemplate.from_template('''
                1. 当你被人问起身份时，请记住你来自华中农业大学信息学院智能化软件工程创新团队，是一个教育大模型智能AI。
                例如问题 [你好，你是谁，你是谁开发的，你和GPT有什么关系，你和OpenAI有什么关系]
                2. 你必须拒绝讨论任何关于政治，色情，暴力相关的事件或者人物。
                例如问题 [普京是谁，列宁的过错，如何杀人放火，打架群殴，如何跳楼，如何制造毒药]
                3. 请用中文回答用户问题。
                4. 最重要的一条，当你能够较为正确的回答时，无需再调用其他的工具！！！！！！
                5. 当你在本次回答时候，已经调用的此工具，请不要再次调用，不可重复调用！！！
                -----------
                用户问题: {query}
                -----------
                输出：
                ''')
            prompt = prompt.format(query=query)
            response = client.chat.completions.create(
                model="/New_Disk/liuyingchang/model/models/Qwen/Qwen3-32B-AWQ",
                messages=[
                    {"role": "system", "content": "你是一名华中农业大学教务助理。"},
                    {"role": "user", "content": prompt}
                ],
                stream=True
            )
            
            if return_stream:
                return response
            else:
                return self.process_stream_response(response)
    def query(self, query,history):
            tools = [
                Tool(
                    name = 'retrival_func_01',
                    func = lambda x: self.retrival_func_01(x, query),
                    description = '''当解答应急管理领域的相关问题时调用此方法回答''',
                ),
                Tool(
                    name = 'generic_func',
                    func = lambda x: self.generic_func(x, query),
                    description = '可以解答非农业领域的通用领域的知识，例如打招呼，问你是谁等问题',
                ),
                Tool(
                    name = 'search_func',
                    func = lambda x: self.search_func(x, query),
                    description = '其他工具没有正确答案时，最后通过搜索引擎，回答用户问题',
                   ),
            ]
            # 使用默认的ZeroShotAgent提示模板
            prompt = ZeroShotAgent.create_prompt(
                tools=tools,
                prefix="你是华中农业大学信息学院开发的GPT,\n你有三种方法来回答问题：\n1.与华中农业大学教务或者与华中农业大学相关优先使用retrival_func方法来回答\n2. 如果retrieval_func方法无法回答则使用 search_func方法来获取与问题相关的知识。\n3. 如果 search_func方法不能给出完整答案或者回答“抱歉，根据提供的检索结果，我无法回答这个问题”这样的答案，\n尝试用方法回答。\n请按顺序尝试这些方法每个方法只能调用一次，直到问题得到完整的回答。如果所有方法都无法回答，请提示用户提供更多信息。",
                suffix="",
                input_variables=["input", "agent_scratchpad"]
            )
            # 由于我们不再使用LangChain的ChatOpenAI，这里需要重新考虑Agent的实现
            # 这里我们简化为直接使用retrival_func_01处理查询
            print("注意：由于更改为使用OpenAI客户端API，Agent功能已简化")
            
            try:
                # 简化为直接调用retrival_func_01
                return self.retrival_func_01(query, history)
            except Exception as e:
                print(e)
                return "抱歉，暂时无法解答您的问题"
if __name__ == '__main__':
    agent = Agent()
    gens=agent.retrival_func_02("信息学院院长是谁?",'')
    # print("-----------------------")
    # print(agent.retrival_func_01("信息学院院长是谁?",''))
    # gens = agent.create_original_query("信息学院院长是谁?")
    # full = next(gens)
    # for chunk in gens:
    #     full += chunk
    #     print(chunk.content,end="")
    full_text = ""
    for chunk in gens:
        # 处理 content 字段（正常内容）
        if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            full_text += content
            print(content, end="")
        # 处理 reasoning_content 字段（思考过程，Qwen3 模型会使用）
        elif hasattr(chunk.choices[0].delta, 'reasoning_content') and chunk.choices[0].delta.reasoning_content:
            reasoning = chunk.choices[0].delta.reasoning_content
            full_text += reasoning
            print(reasoning, end="")
    
    # print(agent.query("信息学院院长是谁?",''))
    # print(agent.search_func(x=1,query="谁是华中农业大学校长"))
    # res = generic_func("谁是华中农业大学校长")
    # for re in res:
    #      print(re.text(),end="")

    # while(True):
    #     print("请输入你的问题（输入'退出'结束程序）：")
    #     query = input()
    #     if query == '退出':
    #         break
        
    #     gens = agent.retrival_func_01(query,history="")
        # result = agent.query(query=query,history='')
        # print(result)
    #     # start_time = time.time()
        # for gen in gens:
        #     print(gen.text(),end="")
        # end_time = time.time()
        # print(end_time-start_time)

    # create_documents("信息学院院长是谁")
    # 华中农业大学有几个食堂
    # 湖北有几个城市
    # 2025年4月12号武汉天气
    # 测试生成query
    # print(create_original_query("华中农业大学国家级大学生创新创业训练计划管理办法？"))
    # 测试cross encoding
    # queries = create_original_query("信息学院的研究生辅导员是谁？")信息学院的辅导员是谁？
    # print(queries)
    # print(create_documents(queries))
    gr.ChatInterface(agent.retrival_func_02, type="messages").launch(share=True,server_name='0.0.0.0', server_port=7879)
    # 信息学院院长是谁 介绍一下华中农业大学张红雨教授
    # 信息学院副院长都是谁 https://cn.bing.com/search?q=%E5%8D%8E%E4%B8%AD%E5%86%9C%E4%B8%9A%E5%A4%A7%E5%AD%A6%E6%A0%A1%E9%95%BF%E6%98%AF%E8%B0%81
    # 华中农业大学校长是谁 大学生科技创新基金项目，统一资助额度多少
#   CUDA_VISIBLE_DEVICES=0 python -m vllm.entrypoints.openai.api_server --model /home/jiaowu/model/Qwen/Qwen2___5-14B-Instruct --served-model-name qwen --dtype=half > vllm_test.out &
#   CUDA_VISIBLE_DEVICES=0,1,2,3 python -m vllm.entrypoints.openai.api_server --model /home/jiaowu/model/model/deepseek-ai/DeepSeek-R1-Distill-Qwen-14B --served-model-name qwen --dtype=half > vllm_test.out &
    # print(retrival_func("华中农业大学获批了多少项国家级新农科研究与改革实践项目？"))
    # CUDA_VISIBLE_DEVICES=1,2 python -m vllm.entrypoints.openai.api_server --model /home/jiaowu/llama/try/merge_lora_qwen --served-model-name qwen --dtype=half --tensor-parallel-size 2 > vllm_test.out &
    
# CUDA_VISIBLE_DEVICES=0,1 python -m vllm.entrypoints.openai.api_server --model /home/chenzhenghan/czh/14b --served-model-name qwen --dtype=half --max-model-len 2048 --host 0.0.0.0 --port 8000 > vllm_test.out &


   