#!/usr/bin/env python3
"""
情感识别 + 认知变化测试脚本
测试 ai_service.analyze_record() 和 detect_cognitive_change()
"""
import sys
sys.path.insert(0, '/Users/jianguo/Desktop/test/echo-app/backend')

import asyncio
import json
from datetime import datetime
from app.services.ai_service import ai_service

# 测试结果收集
results = {
    "测试时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "情感识别": [],
    "认知变化": []
}

def print_divider(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def print_result(test_id, text, expected, actual, passed):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"\n{test_id} {status}")
    print(f"  输入: {text[:50]}...")
    print(f"  期望: emotion={expected['emotion']}, primary={expected['primary']}, type={expected['type']}")
    print(f"  实际: emotion={actual['emotion']}, primary={actual['primary_emotion']}, type={actual['input_type']}")

async def test_emotion_analysis():
    """测试情感识别功能"""
    print_divider("情感识别测试")
    
    test_cases = [
        # 情绪表达类
        {
            "id": "E-01",
            "text": "今天好累，开了三个会人都麻了",
            "expected": {"emotion": "negative", "primary": "疲惫", "type": "情绪表达"}
        },
        {
            "id": "E-02",
            "text": "终于把项目做完了，虽然累但挺有成就感的",
            "expected": {"emotion": "mixed", "primary": "满足", "type": "情绪表达"}
        },
        {
            "id": "E-03",
            "text": "今天发工资了，还涨了10%，太开心了！",
            "expected": {"emotion": "positive", "primary": "开心", "type": "情绪表达"}
        },
        # 观点分享类（重点验证不误判）
        {
            "id": "V-01",
            "text": "产品开发还是要遵循定好的规则",
            "expected": {"emotion": "neutral", "primary": "平静", "type": "观点分享"}
        },
        {
            "id": "V-02",
            "text": "Web coding最重要的就是要先做计划",
            "expected": {"emotion": "neutral", "primary": "平静", "type": "观点分享"}
        },
        {
            "id": "V-03",
            "text": "在一些产品应用场景上，不是非得使用大模型",
            "expected": {"emotion": "neutral", "primary": "平静", "type": "观点分享"}
        },
        {
            "id": "V-04",
            "text": "必须承认，我们之前的决策有问题",
            "expected": {"emotion": "neutral", "primary": "平静", "type": "观点分享"}
        },
        # 事实陈述类
        {
            "id": "F-01",
            "text": "今天周三，买了杯咖啡",
            "expected": {"emotion": "neutral", "primary": "平静", "type": "事实陈述"}
        },
        # 计划目标类
        {
            "id": "P-01",
            "text": "明天要完成这个功能",
            "expected": {"emotion": "neutral", "primary": "平静", "type": "计划目标"}
        },
        # 回忆过去类
        {
            "id": "M-01",
            "text": "想起小时候在奶奶家的日子，那时候真快乐",
            "expected": {"emotion": "positive", "primary": "开心", "type": "回忆过去"}
        },
    ]
    
    pass_count = 0
    for tc in test_cases:
        result = await ai_service.analyze_record(tc["text"])
        
        # 判断是否通过
        emotion_match = result["emotion"] == tc["expected"]["emotion"] or (
            tc["expected"]["emotion"] == "mixed" and result["emotion"] in ["positive", "negative", "mixed"]
        )
        primary_match = result["primary_emotion"] == tc["expected"]["primary"]
        type_match = tc["expected"]["type"] in result["input_type"] or result["input_type"] in tc["expected"]["type"]
        
        passed = emotion_match and primary_match and type_match
        if passed:
            pass_count += 1
        
        print_result(tc["id"], tc["text"], tc["expected"], result, passed)
        
        results["情感识别"].append({
            "id": tc["id"],
            "text": tc["text"],
            "expected": tc["expected"],
            "actual": {
                "emotion": result["emotion"],
                "primary_emotion": result["primary_emotion"],
                "input_type": result["input_type"]
            },
            "passed": passed
        })
    
    print(f"\n📊 情感识别测试结果: {pass_count}/{len(test_cases)} 通过")
    results["情感识别通过率"] = f"{pass_count}/{len(test_cases)}"
    
    return pass_count, len(test_cases)

async def test_cognitive_change():
    """测试认知变化检测"""
    print_divider("认知变化检测测试")
    
    test_cases = [
        {
            "id": "C-01",
            "records": [
                {"text": "我突然意识到，以前总觉得加班是努力，现在觉得那是效率低"},
                {"text": "决定以后先做重要的事，不瞎忙"}
            ],
            "expected_has_change": True
        },
        {
            "id": "C-02",
            "records": [
                {"text": "发现做家务可以放空，开始喜欢了"},
            ],
            "expected_has_change": True
        },
        {
            "id": "C-03",
            "records": [
                {"text": "今天好累"},
                {"text": "还是好累"},
            ],
            "expected_has_change": False
        },
        {
            "id": "C-04",
            "records": [
                {"text": "现在更关注当下，焦虑少多了"},
            ],
            "expected_has_change": True
        },
    ]
    
    pass_count = 0
    for tc in test_cases:
        result = await ai_service.detect_cognitive_change(tc["records"])
        has_change = result is not None and result.get("has_change", False)
        passed = has_change == tc["expected_has_change"]
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"\n{tc['id']} {status}")
        print(f"  记录: {[r['text'][:30] for r in tc['records']]}")
        print(f"  期望变化: {tc['expected_has_change']}")
        print(f"  实际变化: {has_change}")
        
        if result and result.get("has_change"):
            print(f"  变化详情: {result.get('changes', [])}")
        
        results["认知变化"].append({
            "id": tc["id"],
            "expected_has_change": tc["expected_has_change"],
            "actual_has_change": has_change,
            "passed": passed
        })
        
        if passed:
            pass_count += 1
    
    print(f"\n📊 认知变化测试结果: {pass_count}/{len(test_cases)} 通过")
    results["认知变化通过率"] = f"{pass_count}/{len(test_cases)}"
    
    return pass_count, len(test_cases)

async def main():
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║        回响项目 - 情感识别 & 认知变化 测试                  ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    
    # 测试情感识别
    emotion_pass, emotion_total = await test_emotion_analysis()
    
    # 测试认知变化
    cognitive_pass, cognitive_total = await test_cognitive_change()
    
    # 汇总
    print_divider("测试汇总")
    total_pass = emotion_pass + cognitive_pass
    total_cases = emotion_total + cognitive_total
    
    print(f"\n✨ 情感识别: {emotion_pass}/{emotion_total} 通过")
    print(f"✨ 认知变化: {cognitive_pass}/{cognitive_total} 通过")
    print(f"\n🎯 总通过率: {total_pass}/{total_cases} ({total_pass/total_cases*100:.1f}%)")
    
    results["总通过率"] = f"{total_pass}/{total_cases} ({total_pass/total_cases*100:.1f}%)"
    
    # 保存结果
    output_file = "/Users/jianguo/Desktop/test/回响项目/测试结果_情感识别_2026-03-06.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n📝 测试结果已保存: {output_file}")

if __name__ == "__main__":
    asyncio.run(main())
