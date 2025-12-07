#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试表格完整性：验证表格是否作为整体存入向量数据库
"""

from model.docx_table_processor import DocxTableProcessor
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import numpy as np

def test_table_integrity():
    """测试表格是否作为整体存入向量数据库"""

    print("=" * 60)
    print("测试表格完整性验证")
    print("=" * 60)

    # 创建处理器实例
    processor = DocxTableProcessor()

    # 测试文件路径
    test_file = "/home/liziwei/Emergency-LLM/new_main/resources/files/test_emergency_table.docx"

    print(f"测试文件: {test_file}")

    # 1. 重新提取表格内容（原始内容）
    print("\n1. 提取原始表格内容:")
    try:
        tables_data = processor.extract_tables_from_docx(test_file)
        if tables_data:
            original_content = tables_data[0]['content']
            print("原始表格内容:")
            print(original_content)
            print(f"\n原始内容长度: {len(original_content)} 字符")
        else:
            print("未找到表格内容")
            return
    except Exception as e:
        print(f"提取表格失败: {e}")
        return

    # 2. 从向量数据库检索内容
    print("\n2. 从向量数据库检索内容:")
    try:
        # 直接查询向量数据库
        results = processor.vector_db.get(
            filter={"type": "table", "file_name": "test_emergency_table.docx"}
        )

        if results['documents']:
            retrieved_content = results['documents'][0]
            retrieved_metadata = results['metadatas'][0]

            print("检索到的表格内容:")
            print(retrieved_content)
            print(f"\n检索内容长度: {len(retrieved_content)} 字符")
            print(f"元数据: {retrieved_metadata}")
        else:
            print("向量数据库中未找到表格内容")
            return

    except Exception as e:
        print(f"检索失败: {e}")
        return

    # 3. 比较内容是否完全一致
    print("\n3. 完整性验证:")

    if original_content == retrieved_content:
        print("✅ 成功！表格内容完全一致")
        print("✅ 表格确实作为整体存入了向量数据库，没有被分块")
    else:
        print("❌ 失败！表格内容不一致")
        print("原始内容:")
        print(repr(original_content))
        print("检索内容:")
        print(repr(retrieved_content))

    # 4. 验证元数据
    print("\n4. 元数据验证:")
    expected_metadata_keys = ['type', 'content_type', 'file_name', 'table_index', 'rows', 'cols']
    for key in expected_metadata_keys:
        if key in retrieved_metadata:
            print(f"✅ 元数据包含 {key}: {retrieved_metadata[key]}")
        else:
            print(f"❌ 元数据缺少 {key}")

    # 5. 测试查询功能
    print("\n5. 查询功能测试:")
    test_queries = [
        "应急管理表格中包含哪些灾害类型",
        "火灾的响应等级和所需装备",
        "洪水应对措施",
        "地震救援装备"
    ]

    for query in test_queries:
        print(f"\n查询: '{query}'")
        search_results = processor.test_table_retrieval(query)

        if search_results:
            result = search_results[0]  # 取第一个结果
            content_preview = result['content'][:300] + "..." if len(result['content']) > 300 else result['content']
            print(f"  找到表格，相似度: {result['score']:.4f}")
            print(f"  内容预览: {content_preview}")
        else:
            print("  未找到相关表格")

    print("\n" + "=" * 60)
    print("表格完整性测试完成")
    print("=" * 60)

def check_vector_db_structure():
    """检查向量数据库的结构和内容"""

    print("\n" + "=" * 60)
    print("检查向量数据库结构")
    print("=" * 60)

    try:
        # 直接访问向量数据库
        embed_model = HuggingFaceEmbeddings(
            model_name="/New_Disk/liziwei/maidalun1020/bce-embedding-base_v1",
            model_kwargs={"device": "cuda"},
            encode_kwargs={"normalize_embeddings": True}
        )

        class LCEmbedding:
            def __init__(self, embed_model):
                self.embed_model = embed_model

            def embed_query(self, text: str):
                result = self.__call__([text])
                return result[0] if result else []

            def embed_documents(self, texts):
                return self.__call__(texts)

            def __call__(self, input):
                embeddings = self.embed_model.embed_documents(input)
                result = []
                for emb in embeddings:
                    if isinstance(emb, np.ndarray):
                        result.append(emb.tolist())
                    elif isinstance(emb, list):
                        if len(emb) > 0 and isinstance(emb[0], np.ndarray):
                            result.append(emb[0].tolist())
                        elif len(emb) > 0 and isinstance(emb[0], (int, float, np.integer, np.floating)):
                            result.append([float(x) for x in emb])
                        else:
                            result.append(emb)
                    else:
                        result.append(emb)
                return result

        embedding_func = LCEmbedding(embed_model)

        vector_db = Chroma(
            persist_directory="/home/liziwei/Emergency-LLM/backend/vdb",
            embedding_function=embedding_func
        )

        # 获取所有文档
        all_docs = vector_db.get()

        print(f"向量数据库总文档数: {len(all_docs['documents'])}")

        # 统计表格类型文档
        table_docs = []
        other_docs = []

        for i, metadata in enumerate(all_docs['metadatas']):
            if metadata.get('type') == 'table':
                table_docs.append({
                    'id': all_docs['ids'][i],
                    'content': all_docs['documents'][i],
                    'metadata': metadata
                })
            else:
                other_docs.append({
                    'id': all_docs['ids'][i],
                    'metadata': metadata
                })

        print(f"表格类型文档数: {len(table_docs)}")
        print(f"其他类型文档数: {len(other_docs)}")

        if table_docs:
            print("\n表格文档详情:")
            for i, doc in enumerate(table_docs, 1):
                print(f"\n表格文档 {i}:")
                print(f"  ID: {doc['id']}")
                print(f"  文件名: {doc['metadata'].get('file_name', 'N/A')}")
                print(f"  表格索引: {doc['metadata'].get('table_index', 'N/A')}")
                print(f"  行数: {doc['metadata'].get('rows', 'N/A')}")
                print(f"  列数: {doc['metadata'].get('cols', 'N/A')}")
                print(f"  内容长度: {len(doc['content'])} 字符")
                print(f"  内容预览: {doc['content'][:200]}...")

    except Exception as e:
        print(f"检查向量数据库结构失败: {e}")

if __name__ == '__main__':
    test_table_integrity()
    check_vector_db_structure()
