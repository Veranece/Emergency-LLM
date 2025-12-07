#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修改后的generateData.py中的表格处理功能
"""

import os
import sys
sys.path.append('/home/liziwei/Emergency-LLM/backend')

def test_docx_table_processing():
    """测试DOCX表格处理功能"""

    print("=" * 80)
    print("测试修改后的generateData.py表格处理功能")
    print("=" * 80)

    # 导入修改后的generateData模块
    from generateData import process_docx_tables_as_documents

    # 测试文件路径
    test_file = "/home/liziwei/Emergency-LLM/testEme/resource/(2018年度)技术规格书（三）_救灾防寒服.doc"

    if not os.path.exists(test_file):
        print(f"❌ 测试文件不存在: {test_file}")
        return

    print(f"测试文件: {test_file}")

    # 先转换为DOCX（如果还没有转换）
    import subprocess
    docx_file = test_file.replace('.doc', '.docx')

    if not os.path.exists(docx_file):
        print("转换DOC到DOCX...")
        try:
            subprocess.run([
                "libreoffice", "--headless", "--convert-to", "docx",
                "--outdir", os.path.dirname(test_file), test_file
            ], check=True)
            print("✅ 转换成功")
        except Exception as e:
            print(f"❌ 转换失败: {e}")
            return

    # 测试表格处理
    print("\n处理DOCX表格..."    docs = process_docx_tables_as_documents(docx_file, "Technology")

    print(f"处理结果: 找到 {len(docs)} 个文档")

    # 分析结果
    table_docs = []
    text_docs = []

    for doc in docs:
        if doc.metadata.get("content_type") == "structured_table":
            table_docs.append(doc)
        else:
            text_docs.append(doc)

    print(f"表格文档: {len(table_docs)} 个")
    print(f"文本文档: {len(text_docs)} 个")

    # 检查表格文档
    if table_docs:
        print("
表格文档详情:"        for i, doc in enumerate(table_docs, 1):
            print(f"\n表格 {i}:")
            print(f"  行数: {doc.metadata.get('rows', 'N/A')}")
            print(f"  列数: {doc.metadata.get('cols', 'N/A')}")
            print(f"  内容长度: {len(doc.page_content)} 字符")
            print(f"  内容预览: {doc.page_content[:200]}...")

            # 特别检查25行防寒服表格
            if doc.metadata.get('rows') == 25 and '防寒服' in doc.metadata.get('source', ''):
                print("  🎯 找到25行防寒服规格表格！")
                lines = doc.page_content.split('\n')
                print(f"  实际行数: {len(lines)}")

                # 检查是否包含完整的规格项目
                if '前衣长' in doc.page_content and '胸围' in doc.page_content:
                    print("  ✅ 包含完整规格项目")
                else:
                    print("  ❌ 规格项目不完整")

    # 验证表格不被分块
    print("
分块验证:"    for doc in table_docs:
        content_length = len(doc.page_content)
        print(f"  表格内容长度: {content_length} 字符")

        # 检查内容是否包含完整的表格结构
        lines = doc.page_content.split('\n')
        has_table_structure = any(' | ' in line for line in lines)
        if has_table_structure:
            print("  ✅ 保持表格结构")
        else:
            print("  ❌ 表格结构丢失")

    print("
" + "=" * 80)
    print("测试完成")
    print("=" * 80)

    # 清理临时文件
    if os.path.exists(docx_file) and docx_file != test_file:
        try:
            os.remove(docx_file)
            print(f"清理临时文件: {docx_file}")
        except:
            pass

if __name__ == '__main__':
    test_docx_table_processing()
