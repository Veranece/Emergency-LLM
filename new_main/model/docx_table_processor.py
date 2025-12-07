#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DOCX表格处理器：识别DOCX文件中的表格，并将其作为整体存入向量数据库
"""

from docx import Document
from docx.shared import Inches
from docx.oxml.ns import nsdecls, qn
from docx.oxml import parse_xml
import os
import json
from typing import List, Dict, Any
from chromadb.api.types import EmbeddingFunction
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import numpy as np

class DocxTableProcessor:
    """DOCX表格处理器"""

    def __init__(self, vector_db_path="/home/liziwei/Emergency-LLM/backend/vdb"):
        """
        初始化DOCX表格处理器

        Args:
            vector_db_path: 向量数据库路径
        """
        # 初始化嵌入模型
        embed_model = HuggingFaceEmbeddings(
            model_name="/New_Disk/liziwei/maidalun1020/bce-embedding-base_v1",
            model_kwargs={"device": "cuda"},
            encode_kwargs={"normalize_embeddings": True}
        )

        # 创建Chroma向量数据库实例
        self.vector_db = Chroma(
            persist_directory=vector_db_path,
            embedding_function=self._create_embedding_function(embed_model)
        )

    def _create_embedding_function(self, embed_model):
        """创建适配Chroma的嵌入函数"""
        class LCEmbedding(EmbeddingFunction):
            def __init__(self, embed_model):
                self.embed_model = embed_model

            def embed_query(self, text: str) -> list[float]:
                result = self.__call__([text])
                return result[0] if result else []

            def embed_documents(self, texts: list[str]) -> list[list[float]]:
                return self.__call__(texts)

            def __call__(self, input: list[str]) -> list[list[float]]:
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
                            result.append(self._convert_to_list(emb))
                    else:
                        result.append(self._convert_to_list(emb))
                return result

            def _convert_to_list(self, obj):
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

        return LCEmbedding(embed_model)

    def extract_tables_from_docx(self, docx_path: str) -> List[Dict[str, Any]]:
        """
        从DOCX文件中提取所有表格

        Args:
            docx_path: DOCX文件路径

        Returns:
            表格列表，每个表格包含元数据和内容
        """
        if not os.path.exists(docx_path):
            raise FileNotFoundError(f"文件不存在: {docx_path}")

        try:
            doc = Document(docx_path)
        except Exception as e:
            raise Exception(f"无法打开DOCX文件: {e}")

        tables_data = []

        for table_idx, table in enumerate(doc.tables):
            # 提取表格内容
            table_content = self._extract_table_content(table)

            # 创建表格元数据
            table_metadata = {
                'file_name': os.path.basename(docx_path),
                'file_path': docx_path,
                'table_index': table_idx,
                'type': 'table',  # 特殊类型标识这是表格
                'rows': len(table.rows),
                'cols': len(table.columns) if table.columns else 0,
                'content_type': 'structured_table'  # 标识这是结构化表格数据
            }

            # 创建表格数据字典
            table_data = {
                'content': table_content,
                'metadata': table_metadata,
                'table_structure': self._get_table_structure(table)
            }

            tables_data.append(table_data)

        return tables_data

    def _extract_table_content(self, table) -> str:
        """
        提取表格内容为字符串格式

        Args:
            table: docx表格对象

        Returns:
            表格内容的字符串表示
        """
        content_lines = []

        # 添加表头（如果有）
        if len(table.rows) > 0:
            header_row = table.rows[0]
            header_text = " | ".join([cell.text.strip() for cell in header_row.cells])
            content_lines.append(f"表头: {header_text}")

        # 添加表格数据
        for row_idx, row in enumerate(table.rows):
            row_data = []
            for cell in row.cells:
                # 处理单元格内容，保留换行符
                cell_text = cell.text.strip()
                if not cell_text:
                    cell_text = "[空]"
                row_data.append(cell_text)

            content_lines.append(f"行{row_idx + 1}: {' | '.join(row_data)}")

        # 返回完整的表格内容
        return "\n".join(content_lines)

    def _get_table_structure(self, table) -> Dict[str, Any]:
        """
        获取表格的结构信息

        Args:
            table: docx表格对象

        Returns:
            表格结构字典
        """
        structure = {
            'rows_count': len(table.rows),
            'columns_count': len(table.columns) if hasattr(table, 'columns') and table.columns else len(table.rows[0].cells) if table.rows else 0,
            'has_headers': len(table.rows) > 0,
            'cell_contents': []
        }

        # 收集所有单元格内容
        for row_idx, row in enumerate(table.rows):
            row_contents = []
            for col_idx, cell in enumerate(row.cells):
                row_contents.append({
                    'row': row_idx,
                    'col': col_idx,
                    'content': cell.text.strip()
                })
            structure['cell_contents'].append(row_contents)

        return structure

    def store_table_in_vector_db(self, table_data: Dict[str, Any]) -> bool:
        """
        将表格数据存入向量数据库，作为一个整体

        Args:
            table_data: 表格数据字典

        Returns:
            是否成功存储
        """
        try:
            # 使用表格内容作为文档内容
            content = table_data['content']

            # 使用表格元数据
            metadata = table_data['metadata']

            # 创建唯一的ID
            table_id = f"table_{metadata['file_name']}_{metadata['table_index']}"

            # 将表格作为单个文档存入向量数据库
            # 注意：这里我们不进行分块，直接将整个表格作为一整个文档
            self.vector_db.add_texts(
                texts=[content],
                metadatas=[metadata],
                ids=[table_id]
            )

            print(f"表格已存入向量数据库: {table_id}")
            return True

        except Exception as e:
            print(f"存储表格失败: {e}")
            return False

    def process_docx_tables(self, docx_path: str) -> List[bool]:
        """
        处理DOCX文件中的所有表格，将它们作为整体存入向量数据库

        Args:
            docx_path: DOCX文件路径

        Returns:
            每个表格的存储结果列表
        """
        # 提取所有表格
        tables_data = self.extract_tables_from_docx(docx_path)

        if not tables_data:
            print(f"在 {docx_path} 中未找到表格")
            return []

        print(f"在 {docx_path} 中找到 {len(tables_data)} 个表格")

        # 存储每个表格
        results = []
        for table_data in tables_data:
            success = self.store_table_in_vector_db(table_data)
            results.append(success)

        return results

    def test_table_retrieval(self, query: str, table_metadata_filter: Dict = None) -> List[Dict]:
        """
        测试表格检索功能

        Args:
            query: 查询字符串
            table_metadata_filter: 元数据过滤条件

        Returns:
            检索结果
        """
        try:
            # 设置默认过滤条件，只检索表格类型的内容
            filter_conditions = {"type": "table"}
            if table_metadata_filter:
                filter_conditions.update(table_metadata_filter)

            # 进行相似性搜索
            results = self.vector_db.similarity_search_with_relevance_scores(
                query=query,
                k=5,
                filter=filter_conditions
            )

            # 格式化结果
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'score': score
                })

            return formatted_results

        except Exception as e:
            print(f"检索测试失败: {e}")
            return []


def test_docx_table_processor():
    """测试DOCX表格处理器"""
    processor = DocxTableProcessor()

    # 测试文件路径
    test_file = "/home/liziwei/Emergency-LLM/new_main/resources/files/test_emergency_table.docx"

    # 处理DOCX表格
    print("正在处理DOCX表格...")
    results = processor.process_docx_tables(test_file)

    if results:
        print(f"成功处理了 {len(results)} 个表格")
        print(f"存储结果: {results}")

        # 测试检索
        print("\n测试表格检索...")
        test_queries = [
            "应急管理表格",
            "火灾响应",
            "洪水应对",
            "地震救援"
        ]

        for query in test_queries:
            print(f"\n查询: '{query}'")
            search_results = processor.test_table_retrieval(query)

            if search_results:
                print(f"找到 {len(search_results)} 个相关表格:")
                for i, result in enumerate(search_results[:2]):  # 只显示前2个结果
                    print(f"  结果{i+1}:")
                    print(f"    内容: {result['content'][:200]}...")
                    print(f"    元数据: {result['metadata']}")
                    print(f"    相似度分数: {result['score']:.4f}")
            else:
                print("  未找到相关结果")
    else:
        print("未找到或处理表格")


if __name__ == '__main__':
    test_docx_table_processor()
