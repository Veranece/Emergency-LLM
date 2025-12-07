#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试DOCX表格处理API端点
"""

import requests
import json
import time

def test_docx_table_api():
    """测试DOCX表格处理API"""

    print("=" * 60)
    print("测试DOCX表格处理API")
    print("=" * 60)

    # Flask应用URL
    base_url = "http://127.0.0.1:5888"

    # 测试文件名
    test_filename = "test_emergency_table.docx"

    # API端点
    api_url = f"{base_url}/api/process-docx-table"

    # 请求数据
    request_data = {
        "filename": test_filename
    }

    print(f"API端点: {api_url}")
    print(f"请求数据: {json.dumps(request_data, ensure_ascii=False, indent=2)}")

    try:
        # 发送POST请求
        print("\n发送请求...")
        response = requests.post(api_url, json=request_data, timeout=30)

        print(f"响应状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("响应内容:")
            print(json.dumps(result, ensure_ascii=False, indent=2))

            if result.get('code') == 200:
                data = result.get('data', {})
                print("
✅ API调用成功!"                print(f"处理了 {data.get('processed_tables', 0)} 个表格")
                print(f"成功存储了 {data.get('success_count', 0)} 个表格")

                # 验证表格是否真的存入了向量数据库
                print("\n验证向量数据库存储...")
                from model.docx_table_processor import DocxTableProcessor

                processor = DocxTableProcessor()

                # 检查向量数据库中的表格数量
                all_docs = processor.vector_db.get()
                table_docs = [doc for doc, meta in zip(all_docs['documents'], all_docs['metadatas'])
                            if meta.get('type') == 'table']

                print(f"向量数据库中的表格文档数量: {len(table_docs)}")

                if table_docs:
                    print("最新存储的表格内容预览:")
                    latest_table = table_docs[-1]  # 取最后一个（最新）
                    preview = latest_table[:300] + "..." if len(latest_table) > 300 else latest_table
                    print(preview)

            else:
                print(f"❌ API调用失败: {result.get('message', '未知错误')}")

        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ 连接失败：Flask应用可能未启动")
        print("请先启动Flask应用：python app.py")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def check_flask_app_status():
    """检查Flask应用状态"""

    print("\n检查Flask应用状态...")

    try:
        response = requests.get("http://127.0.0.1:5888/", timeout=5)
        if response.status_code == 200:
            print("✅ Flask应用正在运行")
            return True
        else:
            print(f"❌ Flask应用响应异常: {response.status_code}")
            return False
    except:
        print("❌ Flask应用未运行")
        return False

if __name__ == '__main__':
    # 检查Flask应用状态
    if check_flask_app_status():
        # 运行API测试
        test_docx_table_api()
    else:
        print("\n请先启动Flask应用：")
        print("cd /home/liziwei/Emergency-LLM/new_main && python app.py")

    print("\n" + "=" * 60)
    print("API测试完成")
    print("=" * 60)
