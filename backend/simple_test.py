#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试修改后的表格处理功能
"""

import os
import sys
sys.path.append('/home/liziwei/Emergency-LLM/backend')

def test_table_processing():
    """测试表格处理功能"""

    print("测试修改后的generateData.py表格处理功能")

    # 导入修改后的generateData模块
    from generateData import process_docx_tables_as_documents

    # 测试文件路径
    test_file = "/home/liziwei/Emergency-LLM/testEme/resource/(2018年度)技术规格书（三）_救灾防寒服.doc"

    if not os.path.exists(test_file):
        print(f"测试文件不存在: {test_file}")
        return

    print(f"测试文件: {test_file}")

    # 先转换为DOCX
    import subprocess
    docx_file = test_file.replace('.doc', '.docx')

    if not os.path.exists(docx_file):
        print("转换DOC到DOCX...")
        try:
            subprocess.run([
                "libreoffice", "--headless", "--convert-to", "docx",
                "--outdir", os.path.dirname(test_file), test_file
            ], check=True)
            print("转换成功")
        except Exception as e:
            print(f"转换失败: {e}")
            return

    # 测试表格处理
    print("处理DOCX表格...")
    docs = process_docx_tables_as_documents(docx_file, "Technology")

    print(f"处理结果: 找到 {len(docs)} 个文档")

    # 分析结果
    table_docs = [doc for doc in docs if doc.metadata.get("content_type") == "structured_table"]
    text_docs = [doc for doc in docs if doc.metadata.get("content_type") != "structured_table"]

    print(f"表格文档: {len(table_docs)} 个")
    print(f"文本文档: {len(text_docs)} 个")

    # 检查25行防寒服表格
    for doc in table_docs:
        if doc.metadata.get('rows') == 25 and '防寒服' in doc.metadata.get('source', ''):
            print("找到25行防寒服规格表格!")
            print(f"行数: {doc.metadata.get('rows')}")
            print(f"内容长度: {len(doc.page_content)} 字符")
            lines = doc.page_content.split('\n')
            print(f"实际行数: {len(lines)}")
            print("前几行内容:")
            for i, line in enumerate(lines[:5]):
                print(f"  {line}")
            break

    print("测试完成")

if __name__ == '__main__':
    test_table_processing()
