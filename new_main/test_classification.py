#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试查询意图分类功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from model.RAG import Agent

def test_classification():
    """测试各种类型的查询"""
    
    print("=" * 80)
    print("查询意图分类测试")
    print("=" * 80)
    
    # 初始化 Agent（会加载 BM25 索引）
    print("\n正在初始化 Agent...")
    agent = Agent()
    print("初始化完成！\n")
    
    # 测试用例
    test_cases = [
        # Technology 类型
        ("洪水来了怎么办？", ["Technology"]),
        ("如何使用灭火器？", ["Technology"]),
        ("地震时的自救措施有哪些？", ["Technology"]),
        ("泥石流的预防方法", ["Technology"]),
        
        # Case 类型
        ("历史上有哪些重大火灾案例？", ["Case"]),
        ("2008年汶川地震的情况", ["Case"]),
        ("给我讲一个洪灾的真实故事", ["Case"]),
        ("有什么典型的应急事故案例？", ["Case"]),
        
        # PopSci 类型
        ("什么是泥石流？", ["PopSci"]),
        ("为什么会发生地震？", ["PopSci"]),
        ("台风是如何形成的？", ["PopSci"]),
        ("解释一下洪涝灾害的原理", ["PopSci"]),
        
        # Regulation 类型
        ("应急管理法规有哪些？", ["Regulation"]),
        ("相关的安全标准是什么？", ["Regulation"]),
        ("国家对消防的规定", ["Regulation"]),
        ("查一下应急预案的相关条例", ["Regulation"]),
        
        # 混合类型
        ("有哪些火灾案例？如何预防？", ["Case", "Technology"]),
        ("地震是什么？怎么自救？", ["PopSci", "Technology"]),
        ("法规要求的应急措施有哪些？", ["Regulation", "Technology"]),
        
        # 模糊查询（应该多路召回）
        ("告诉我一些信息", None),
        ("帮我查一下", None),
    ]
    
    print("=" * 80)
    print("开始测试")
    print("=" * 80)
    
    correct = 0
    total = 0
    
    for query, expected_types in test_cases:
        print(f"\n{'='*80}")
        print(f"📝 测试问题: {query}")
        print(f"🎯 期望类型: {expected_types if expected_types else '多路召回'}")
        print(f"{'-'*80}")
        
        # 规则分类
        result_types = agent.classify_query_intent(query, use_llm=False)
        
        # 判断是否正确
        if expected_types is None:
            # 期望多路召回（返回所有4个类型）
            is_correct = len(result_types) == 4
        else:
            # 检查期望的类型是否都在结果中
            is_correct = all(t in result_types for t in expected_types)
        
        total += 1
        if is_correct:
            correct += 1
            print(f"✅ 分类正确")
        else:
            print(f"❌ 分类错误")
        
        print(f"{'='*80}")
    
    # 统计结果
    accuracy = (correct / total) * 100 if total > 0 else 0
    
    print(f"\n{'='*80}")
    print("测试结果统计")
    print(f"{'='*80}")
    print(f"总测试数: {total}")
    print(f"正确数: {correct}")
    print(f"错误数: {total - correct}")
    print(f"准确率: {accuracy:.1f}%")
    print(f"{'='*80}")
    
    if accuracy >= 80:
        print("\n🎉 测试通过！分类效果良好")
    elif accuracy >= 60:
        print("\n⚠️  测试基本通过，建议优化关键词库")
    else:
        print("\n❌ 测试未通过，需要优化分类逻辑")
    
    return accuracy >= 60


def test_llm_classification():
    """测试 LLM 分类（可选）"""
    print("\n" + "=" * 80)
    print("LLM 分类测试（可选）")
    print("=" * 80)
    
    agent = Agent()
    
    test_queries = [
        "洪水来了怎么办？",
        "什么是泥石流？",
        "有哪些火灾案例？",
        "应急管理法规有哪些？"
    ]
    
    for query in test_queries:
        print(f"\n问题: {query}")
        try:
            result = agent.classify_query_intent(query, use_llm=True)
            print(f"LLM分类结果: {result}")
        except Exception as e:
            print(f"LLM分类失败: {e}")


def compare_methods():
    """对比规则和LLM两种方法"""
    print("\n" + "=" * 80)
    print("规则分类 vs LLM分类 对比测试")
    print("=" * 80)
    
    agent = Agent()
    
    test_queries = [
        "发生火灾时应该如何正确使用灭火器进行扑救？",
        "请介绍一下2008年汶川大地震的基本情况和救援过程",
        "能否解释一下泥石流的形成原理和主要特征？",
        "国家关于应急管理和灾害预防的相关法律法规有哪些？"
    ]
    
    import time
    
    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"问题: {query}")
        print(f"{'-'*80}")
        
        # 规则分类
        start = time.time()
        rule_result = agent.classify_query_intent(query, use_llm=False)
        rule_time = (time.time() - start) * 1000
        print(f"⏱️  耗时: {rule_time:.1f}ms")
        
        # LLM分类（如果可用）
        try:
            print(f"\n{'-'*80}")
            start = time.time()
            llm_result = agent.classify_query_intent(query, use_llm=True)
            llm_time = (time.time() - start) * 1000
            print(f"⏱️  耗时: {llm_time:.1f}ms")
            
            print(f"\n对比:")
            print(f"  规则分类: {rule_result} ({rule_time:.1f}ms)")
            print(f"  LLM分类:  {llm_result} ({llm_time:.1f}ms)")
            print(f"  速度差异: {llm_time/rule_time:.1f}x")
        except Exception as e:
            print(f"\nLLM分类不可用: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="测试查询意图分类功能")
    parser.add_argument("--mode", choices=["basic", "llm", "compare", "all"], 
                       default="basic", help="测试模式")
    args = parser.parse_args()
    
    if args.mode == "basic" or args.mode == "all":
        success = test_classification()
        if not success:
            sys.exit(1)
    
    if args.mode == "llm" or args.mode == "all":
        test_llm_classification()
    
    if args.mode == "compare" or args.mode == "all":
        compare_methods()
    
    print("\n✅ 所有测试完成！")

