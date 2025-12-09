#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time

def test_server_connection(base_url):
    """测试服务器连接"""
    try:
        response = requests.get(base_url, timeout=10)
        print(f"✅ 服务器连接成功: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ 服务器连接失败: {e}")
        return False

def test_markdown_test_page(base_url):
    """测试markdown测试页面"""
    try:
        response = requests.get(f"{base_url}/markdown-test", timeout=10)
        if response.status_code == 200:
            print(f"✅ Markdown测试页面可访问: {base_url}/markdown-test")
            return True
        else:
            print(f"❌ Markdown测试页面访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Markdown测试页面访问出错: {e}")
        return False

def test_ai_response_with_table(base_url):
    """测试AI响应中的表格渲染"""
    test_message = """请生成一个应急管理的表格，包含以下信息：

| 应急等级 | 响应时间 | 疏散范围 | 联系电话 |
|----------|----------|----------|----------|
| 一级     | 15分钟   | 3公里    | 119      |
| 二级     | 30分钟   | 2公里    | 110      |
| 三级     | 60分钟   | 1公里    | 120      |

请确保这个表格能够正确显示。"""

    try:
        print("\n🔄 测试AI响应中的表格渲染...")
        
        response = requests.post(
            f"{base_url}/getMessageWeb",
            json={
                "userMessage": test_message,
                "history": []
            },
            headers={"Content-Type": "application/json"},
            timeout=30,
            stream=True
        )
        
        if response.status_code == 200:
            print("✅ AI接口响应成功")
            
            # 收集流式响应
            full_response = ""
            for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
                if chunk:
                    full_response += chunk
                    print(".", end="", flush=True)
            
            print(f"\n📝 AI完整响应长度: {len(full_response)} 字符")
            
            # 检查响应中的markdown特征
            markdown_features = {
                '包含表格分隔符': '|' in full_response,
                '包含表格标题行': '|-------' in full_response or '|-----' in full_response,
                '包含换行符': '\n' in full_response,
                '包含应急等级': '应急等级' in full_response or '一级' in full_response,
                '包含响应时间': '响应时间' in full_response or '15分钟' in full_response,
            }
            
            print("\n📊 Markdown特征检测:")
            for feature, present in markdown_features.items():
                status = "✅" if present else "❌"
                print(f"  {status} {feature}: {present}")
            
            # 显示响应的前500个字符作为预览
            print(f"\n📄 响应内容预览:")
            print("=" * 50)
            print(repr(full_response[:500]))
            if len(full_response) > 500:
                print("... (内容被截断)")
            print("=" * 50)
            
            return full_response
            
        else:
            print(f"❌ AI接口响应失败: {response.status_code}")
            print(f"错误内容: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ AI接口测试出错: {e}")
        return None

def main():
    base_url = "http://218.199.69.58:5888"
    
    print("🚀 开始测试Markdown渲染修复效果")
    print(f"🌐 测试服务器: {base_url}")
    print("=" * 60)
    
    # 1. 测试服务器连接
    print("1️⃣ 测试服务器连接...")
    if not test_server_connection(base_url):
        print("❌ 服务器连接失败，无法继续测试")
        return
    
    # 2. 测试markdown测试页面
    print("\n2️⃣ 测试Markdown测试页面...")
    test_markdown_test_page(base_url)
    
    # 3. 测试AI响应中的表格
    print("\n3️⃣ 测试AI响应中的表格渲染...")
    ai_response = test_ai_response_with_table(base_url)
    
    print("\n" + "=" * 60)
    print("🎯 测试总结:")
    print(f"   - 服务器地址: {base_url}")
    print(f"   - 主页面: {base_url}/")
    print(f"   - Markdown测试页面: {base_url}/markdown-test")
    
    if ai_response:
        has_table = '|' in ai_response
        print(f"   - AI响应包含表格: {'✅ 是' if has_table else '❌ 否'}")
        
        if has_table:
            print("\n💡 建议:")
            print("   1. 在浏览器中访问主页面，发送包含表格的问题")
            print("   2. 检查前端是否正确渲染表格")
            print("   3. 如果表格仍未正确显示，检查浏览器控制台的错误信息")
        else:
            print("\n⚠️  注意: AI响应中未检测到表格内容，可能需要:")
            print("   1. 检查后端模型是否正确生成表格格式")
            print("   2. 确认prompt是否能引导模型生成表格")
    
    print("\n🔧 如需进一步调试，请:")
    print("   1. 打开浏览器开发者工具")
    print("   2. 访问主页面并发送表格相关问题")
    print("   3. 检查Network标签页中的API响应")
    print("   4. 检查Console标签页中的JavaScript错误")

if __name__ == "__main__":
    main()
