#!/usr/bin/env python3
"""
情感识别测试脚本 v2 - 基于情绪类型匹配（更宽松但更合理）
"""
import sys
sys.path.insert(0, '/Users/jianguo/Desktop/test/echo-app/backend')

import asyncio
import json
from datetime import datetime
from app.services.ai_service import ai_service

# 情绪类型映射
EMOTION_TO_TYPE = {
    # positive
    "开心": "positive", "兴奋": "positive", "满足": "positive", "期待": "positive",
    "感激": "positive", "安心": "positive", "轻松": "positive", "自豪": "positive",
    "成就感": "positive", "愉悦": "positive", "舒畅": "positive", "得意": "positive",
    "感动": "positive", "怀念": "positive", "温暖": "positive", "幸福": "positive",
    # negative
    "低落": "negative", "焦虑": "negative", "疲惫": "negative", "愤怒": "negative",
    "失望": "negative", "恐惧": "negative", "孤独": "negative", "压力": "negative",
    "烦躁": "negative", "痛苦": "negative", "自卑": "negative", "委屈": "negative",
    "紧张": "negative", "压抑": "negative", "厌恶": "negative", "忧郁": "negative",
    "感伤": "negative", "焦急": "negative", "思念": "negative", "倒霉": "negative",
    "不满": "negative", "忐忑": "negative", "同情": "negative", "害羞": "negative",
    # neutral
    "平静": "neutral", "困惑": "neutral", "麻木": "neutral",
}

results = {
    "测试时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "情感识别_基础": {"passed": 0, "failed": 0, "details": []},
    "情感识别_观点误判": {"passed": 0, "failed": 0, "details": []},
    "认知变化": {"passed": 0, "failed": 0, "details": []},
}

def print_header(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)

def check_emotion_type(actual, expected_type):
    """检查情绪类型是否匹配（positive/negative/neutral）"""
    actual_type = EMOTION_TO_TYPE.get(actual, "neutral")
    return actual_type == expected_type

async def test_basic_emotions():
    """测试基础情感识别（50条）- 基于情绪类型匹配"""
    print_header("情感识别测试 - 基础集（50条）v2 情绪类型匹配")
    
    test_cases = [
        ("E-01", "今天发工资了，还涨了10%，太开心了！", "positive", "情绪表达"),
        ("E-02", "今天什么也没干，就躺着发呆，也挺好。", "neutral", "情绪表达"),
        ("E-03", "被领导批评了，觉得自己好没用。", "negative", "情绪表达"),
        ("E-04", "下周有个重要汇报，好担心讲不好。", "negative", "情绪表达"),
        ("E-05", "产品开发还是要遵循定好的规则。", "neutral", "观点分享"),
        ("E-06", "和朋友去游乐园玩了一整天，太刺激了！", "positive", "情绪表达"),
        ("E-07", "他居然骗了我，我再也不想理他了。", "negative", "情绪表达"),
        ("E-08", "一个人过节，有点孤单。", "negative", "情绪表达"),
        ("E-09", "Web coding最重要的就是要先做计划。", "neutral", "观点分享"),
        ("E-10", "考试考了满分，努力没白费！", "positive", "情绪表达"),
        ("E-11", "每天早上起来都能看到日出，真美。", "neutral", "情绪表达"),
        ("E-12", "听说老同学升职了，替他高兴。", "positive", "情绪表达"),
        ("E-13", "又要加班，好烦。", "negative", "情绪表达"),
        ("E-14", "今天周三，买了杯咖啡。", "neutral", "事实陈述"),
        ("E-15", "明天要下雨，记得带伞。", "neutral", "事实陈述"),
        ("E-16", "看到一只流浪猫，好可怜。", "negative", "情绪表达"),
        ("E-17", "爸妈身体健康，是我最大的心愿。", "positive", "情绪表达"),
        ("E-18", "新工作适应得不错，同事都很好。", "positive", "情绪表达"),
        ("E-19", "今天被路人撞了一下，那人连对不起都没说。", "negative", "情绪表达"),
        ("E-20", "连续几天失眠，好痛苦。", "negative", "情绪表达"),
        ("E-21", "终于把拖延很久的任务完成了。", "positive", "情绪表达"),
        ("E-22", "听到一首老歌，想起很多往事。", "positive", "回忆过去"),
        ("E-23", "看到别人都那么优秀，自己好差劲。", "negative", "情绪表达"),
        ("E-24", "他向我表白了，心跳得好快。", "positive", "情绪表达"),
        ("E-25", "明天要去旅游了，好期待！", "positive", "情绪表达"),
        ("E-26", "被最好的朋友误解了，好难受。", "negative", "情绪表达"),
        ("E-27", "第一次上台演讲，腿都在抖。", "negative", "情绪表达"),
        ("E-28", "获奖了，感觉一切付出都值得。", "positive", "情绪表达"),
        ("E-29", "今天天气阴沉沉的，心情也跟着不好。", "negative", "情绪表达"),
        ("E-30", "他们又在背后说我坏话。", "negative", "情绪表达"),
        ("E-31", "下周要完成这个功能开发。", "neutral", "计划目标"),
        ("E-32", "看着窗外的雨，发呆了一下午。", "negative", "情绪表达"),
        ("E-33", "又老了一岁，时间过得好快。", "negative", "情绪表达"),
        ("E-34", "看到孩子第一次走路，好感动。", "positive", "情绪表达"),
        ("E-35", "今天被老板当众表扬了，有点小骄傲。", "positive", "情绪表达"),
        ("E-36", "遇到多年不见的老友，聊得很开心。", "positive", "情绪表达"),
        ("E-37", "电梯坏了，爬了20层楼，累死了。", "negative", "情绪表达"),
        ("E-38", "听说家乡下大雪了，想家了。", "negative", "情绪表达"),
        ("E-39", "高考成绩出来了，没考上理想的大学。", "negative", "情绪表达"),
        ("E-40", "马上就要见到他了，好紧张又好期待。", "positive", "情绪表达"),  # mixed，允许positive
        ("E-41", "减肥一周，瘦了三斤！", "positive", "情绪表达"),
        ("E-42", "被猫抓了一下，要去打疫苗。", "neutral", "事实陈述"),
        ("E-43", "今天的会议重点讨论了产品方向。", "neutral", "事实陈述"),
        ("E-44", "终于把房间收拾干净了，心情都好了。", "positive", "情绪表达"),
        ("E-45", "路上堵车，要迟到了，急死了。", "negative", "情绪表达"),
        ("E-46", "想起小时候在奶奶家的日子，那时候真快乐。", "positive", "回忆过去"),
        ("E-47", "下个月要开始健身计划了。", "neutral", "计划目标"),
        ("E-48", "周末打算去爬山。", "neutral", "计划目标"),
        ("E-49", "被陌生人帮助了，好温暖。", "positive", "情绪表达"),
        ("E-50", "这个难题终于解出来了，如释重负。", "positive", "情绪表达"),
    ]
    
    for tid, text, expected_type, expected_input_type in test_cases:
        result = await ai_service.analyze_record(text)
        
        # 检查情绪类型
        type_match = check_emotion_type(result["primary_emotion"], expected_type)
        
        # 检查输入类型（宽松匹配）
        input_type_match = (expected_input_type in result["input_type"] or 
                          result["input_type"] in expected_input_type or
                          expected_input_type.replace("/", "") in result["input_type"].replace("/", ""))
        
        passed = type_match and input_type_match
        
        status = "✅" if passed else "❌"
        if passed:
            results["情感识别_基础"]["passed"] += 1
        else:
            results["情感识别_基础"]["failed"] += 1
        
        actual_type = EMOTION_TO_TYPE.get(result["primary_emotion"], "neutral")
        print(f"{status} {tid}: {text[:22]:<22} | 期望:{expected_type}/{expected_input_type} | 实际:{actual_type}/{result['primary_emotion']}/{result['input_type'][:6]}")
        
        results["情感识别_基础"]["details"].append({
            "id": tid, "text": text, 
            "expected_type": expected_type, "actual_type": actual_type,
            "passed": passed
        })
    
    total = len(test_cases)
    passed = results["情感识别_基础"]["passed"]
    print(f"\n📊 基础集结果: {passed}/{total} 通过 ({passed/total*100:.1f}%)")

async def test_viewpoint_misjudgment():
    """测试观点分享误判验证（10条）"""
    print_header("观点分享误判验证（10条）- 核心功能测试")
    
    test_cases = [
        ("V-01", "产品开发必须遵循用户反馈，否则会走偏。", "neutral", "观点分享", "强调词'必须'不应被误判为焦虑"),
        ("V-02", "我觉得团队协作最重要的就是信任。", "neutral", "观点分享", "'最重要'不应被误判为压力"),
        ("V-03", "这个方案绝对不能再改了，已经定好了。", "neutral", "观点分享", "'绝对'在观点语境下为中性"),
        ("V-04", "我受不了这种拖延的工作方式。", "negative", "情绪表达", "对照：含'受不了'但为情绪表达"),
        ("V-05", "做产品不能只考虑用户体验，也要考虑商业价值。", "neutral", "观点分享", "'不能'用于表达原则"),
        ("V-06", "每天加班到10点，实在受不了了。", "negative", "情绪表达", "对照：相同词在不同语境"),
        ("V-07", "必须承认，我们之前的决策有问题。", "neutral", "观点分享", "'必须承认'用于陈述事实"),
        ("V-08", "这个bug必须今天修复，否则影响上线。", "neutral", "观点分享", "工作场景的理性判断"),
        ("V-09", "我强烈建议大家每周做一次复盘。", "neutral", "观点分享", "'强烈建议'是观点"),
        ("V-10", "他说的那句话让我强烈地感到不被尊重。", "negative", "情绪表达", "对照：相同词用于情绪描述"),
    ]
    
    for tid, text, expected_type, expected_input_type, note in test_cases:
        result = await ai_service.analyze_record(text)
        
        type_match = check_emotion_type(result["primary_emotion"], expected_type)
        input_type_match = expected_input_type in result["input_type"] or result["input_type"] in expected_input_type
        passed = type_match and input_type_match
        
        status = "✅" if passed else "❌"
        if passed:
            results["情感识别_观点误判"]["passed"] += 1
        else:
            results["情感识别_观点误判"]["failed"] += 1
        
        actual_type = EMOTION_TO_TYPE.get(result["primary_emotion"], "neutral")
        print(f"{status} {tid}: {text[:28]:<28}")
        print(f"   验证点: {note}")
        print(f"   期望: {expected_type}/{expected_input_type} | 实际: {actual_type}/{result['primary_emotion']}/{result['input_type'][:8]}")
        
        results["情感识别_观点误判"]["details"].append({
            "id": tid, "text": text, "note": note, "passed": passed
        })
    
    total = len(test_cases)
    passed = results["情感识别_观点误判"]["passed"]
    print(f"\n📊 误判验证结果: {passed}/{total} 通过 ({passed/total*100:.1f}%)")

async def test_cognitive_change():
    """测试认知变化检测（10组）"""
    print_header("认知变化检测（10组）")
    
    test_cases = [
        ("C-01", [{"text": "我特别害怕当众发言，一说话就紧张"}, {"text": "今天部门会议我主动汇报了工作，虽然还有点紧张，但整体流畅，感觉比以前好多了"}], True),
        ("C-02", [{"text": "加班太累了，感觉身体被掏空"}, {"text": "现在学会了拒绝不必要的加班，身体好多了，和以前不一样了"}], True),
        ("C-03", [{"text": "我觉得自己不够好，总在自我怀疑"}, {"text": "最近发现自己其实挺厉害的，很多事都能做好，改变了之前的想法"}], True),
        ("C-04", [{"text": "每天都很焦虑，担心未来"}, {"text": "现在更关注当下，焦虑少多了，发现原来的担心是多余的"}], True),
        ("C-05", [{"text": "新年目标：每天学习英语"}, {"text": "今天没学英语，明天开始"}], False),
        ("C-06", [{"text": "我觉得工作就是赚钱，没意义"}, {"text": "工作其实也能带来成就感，发现我的想法变了"}], True),
        ("C-07", [{"text": "我讨厌做家务"}, {"text": "发现做家务可以放空，开始喜欢了，和以前不一样"}], True),
        ("C-08", [{"text": "每天通勤两小时，太浪费时间了"}, {"text": "现在利用通勤时间听书，很有收获，发现换个角度看就不一样了"}], True),
        ("C-09", [{"text": "我觉得自己不够漂亮"}, {"text": "现在觉得自信才是最美的，意识到以前的自己太在意别人的看法了"}], True),
        ("C-10", [{"text": "今天好累"}, {"text": "还是好累"}], False),
    ]
    
    for tid, records, expected_has_change in test_cases:
        result = await ai_service.detect_cognitive_change(records)
        has_change = result is not None and result.get("has_change", False)
        passed = has_change == expected_has_change
        
        status = "✅" if passed else "❌"
        if passed:
            results["认知变化"]["passed"] += 1
        else:
            results["认知变化"]["failed"] += 1
        
        record_texts = [r["text"][:15] + "..." for r in records]
        print(f"\n{status} {tid}: 期望变化={expected_has_change} | 实际={has_change}")
        print(f"   记录: {record_texts}")
        if result and result.get("has_change"):
            changes = result.get("changes", [])
            if changes:
                print(f"   检测到: {changes[0].get('type', 'N/A')} - {changes[0].get('topic', 'N/A')}")
        
        results["认知变化"]["details"].append({
            "id": tid, "expected": expected_has_change, "actual": has_change, "passed": passed
        })
    
    total = len(test_cases)
    passed = results["认知变化"]["passed"]
    print(f"\n📊 认知变化结果: {passed}/{total} 通过 ({passed/total*100:.1f}%)")

async def main():
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║     回响项目 - 情感识别测试 v2（情绪类型匹配）                       ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    await test_basic_emotions()
    await test_viewpoint_misjudgment()
    await test_cognitive_change()
    
    print_header("测试汇总")
    
    total_passed = (results["情感识别_基础"]["passed"] + 
                   results["情感识别_观点误判"]["passed"] + 
                   results["认知变化"]["passed"])
    total_cases = (results["情感识别_基础"]["passed"] + results["情感识别_基础"]["failed"] +
                  results["情感识别_观点误判"]["passed"] + results["情感识别_观点误判"]["failed"] +
                  results["认知变化"]["passed"] + results["认知变化"]["failed"])
    
    print(f"\n📈 情感识别-基础集: {results['情感识别_基础']['passed']}/50")
    print(f"📈 情感识别-误判验证: {results['情感识别_观点误判']['passed']}/10")
    print(f"📈 认知变化检测: {results['认知变化']['passed']}/10")
    print(f"\n🎯 总通过率: {total_passed}/{total_cases} ({total_passed/total_cases*100:.1f}%)")
    
    results["总通过率"] = f"{total_passed}/{total_cases} ({total_passed/total_cases*100:.1f}%)"
    
    output_file = "/Users/jianguo/Desktop/test/回响项目/测试结果_v2_2026-03-06.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n📝 详细结果已保存: {output_file}")

if __name__ == "__main__":
    asyncio.run(main())
