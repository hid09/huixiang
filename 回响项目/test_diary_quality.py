#!/usr/bin/env python3
"""
日记生成质量评估测试
生成15组日记，供人工评分
"""
import sys
sys.path.insert(0, '/Users/jianguo/Desktop/test/echo-app/backend')

import asyncio
import json
from datetime import datetime
from app.services.ai_service import ai_service

# 测试集（15组）
TEST_CASES = {
    "分层场景": [
        {
            "组号": "组1",
            "记录数": 0,
            "记录": [],
            "预期策略": "不生成日记"
        },
        {
            "组号": "组2", 
            "记录数": 1,
            "记录": [
                {"time": "12:00", "text": "今天什么也没干，就躺着发呆。", "emotion": "平静"}
            ],
            "预期策略": "简化版"
        },
        {
            "组号": "组3",
            "记录数": 2,
            "记录": [
                {"time": "09:00", "text": "早上挤地铁，人超级多", "emotion": "烦躁"},
                {"time": "18:00", "text": "加班到八点，累死了", "emotion": "疲惫"}
            ],
            "预期策略": "简化版"
        },
        {
            "组号": "组4",
            "记录数": 3,
            "记录": [
                {"time": "09:30", "text": "项目上线成功！", "emotion": "兴奋"},
                {"time": "12:30", "text": "和同事聚餐吃火锅", "emotion": "开心"},
                {"time": "18:00", "text": "下班看到晚霞，拍了照片", "emotion": "满足"}
            ],
            "预期策略": "完整版"
        },
        {
            "组号": "组5",
            "记录数": 5,
            "记录": [
                {"time": "08:00", "text": "收到offer，激动！", "emotion": "兴奋"},
                {"time": "12:00", "text": "租房子遇到问题", "emotion": "焦虑"},
                {"time": "15:00", "text": "房东临时涨价，烦", "emotion": "愤怒"},
                {"time": "18:00", "text": "总算定下来了", "emotion": "轻松"},
                {"time": "23:00", "text": "累但安心", "emotion": "满足"}
            ],
            "预期策略": "完整版"
        }
    ],
    "完整测试": [
        {
            "组号": "组6",
            "场景": "情绪低落的一天",
            "记录": [
                {"time": "10:00", "text": "又被老板骂了，说我进度慢，心情很差。", "emotion": "低落"},
                {"time": "14:00", "text": "下午开会完全不在状态，感觉自己什么都做不好。", "emotion": "低落"},
                {"time": "22:00", "text": "晚上一个人发呆，不知道该怎么办。", "emotion": "低落"}
            ]
        },
        {
            "组号": "组7",
            "场景": "亲情温暖的一天",
            "记录": [
                {"time": "11:00", "text": "收到妈妈寄来的特产，都是我爱吃的。", "emotion": "感动"},
                {"time": "18:30", "text": "和朋友视频，聊了一个多小时。", "emotion": "开心"},
                {"time": "21:00", "text": "给妈妈打电话，说很想她。", "emotion": "思念"}
            ]
        },
        {
            "组号": "组8",
            "场景": "面试前焦虑，后来安心",
            "记录": [
                {"time": "09:00", "text": "明天有个重要面试，好紧张。", "emotion": "焦虑"},
                {"time": "14:00", "text": "复习面试题，感觉好多不会。", "emotion": "焦虑"},
                {"time": "21:00", "text": "和妈妈视频，她安慰了我，好多了。", "emotion": "平静"}
            ]
        },
        {
            "组号": "组9",
            "场景": "追星快乐的一天",
            "记录": [
                {"time": "10:00", "text": "抢到了偶像演唱会的门票！太幸运了！", "emotion": "兴奋"},
                {"time": "15:00", "text": "和闺蜜分享好消息，约好一起去。", "emotion": "开心"},
                {"time": "20:00", "text": "开始学唱偶像的新歌，虽然跑调。", "emotion": "开心"}
            ]
        },
        {
            "组号": "组10",
            "场景": "被气到，然后发泄",
            "记录": [
                {"time": "09:30", "text": "同事甩锅给我，气死了。", "emotion": "愤怒"},
                {"time": "13:00", "text": "和主管解释清楚，但还是很生气。", "emotion": "愤怒"},
                {"time": "19:00", "text": "下班后打了场球，发泄了一下。", "emotion": "平静"}
            ]
        },
        {
            "组号": "组11",
            "场景": "小确幸的一天",
            "记录": [
                {"time": "08:00", "text": "今天尝试了新的早餐搭配，意外好吃。", "emotion": "满足"},
                {"time": "14:00", "text": "发现一个效率很高的新方法，记下来了。", "emotion": "满足"},
                {"time": "19:30", "text": "走路时听到一首好听的歌，搜了歌单。", "emotion": "开心"}
            ]
        },
        {
            "组号": "组12",
            "场景": "认知变化-工作意义",
            "记录": [
                {"time": "10:00", "text": "今天突然意识到，我以前总觉得加班是努力，现在觉得那是效率低。", "emotion": "平静"},
                {"time": "15:00", "text": "决定以后先做重要的事，不瞎忙。", "emotion": "平静"},
                {"time": "22:00", "text": "感觉想通了很多事情。", "emotion": "满足"}
            ]
        },
        {
            "组号": "组13",
            "场景": "困难解决的一天",
            "记录": [
                {"time": "09:00", "text": "项目遇到瓶颈，很头疼。", "emotion": "烦躁"},
                {"time": "14:00", "text": "和团队讨论，有了新思路。", "emotion": "期待"},
                {"time": "20:00", "text": "问题解决了，松了口气。", "emotion": "轻松"}
            ]
        },
        {
            "组号": "组14",
            "场景": "从不开心到惊喜",
            "记录": [
                {"time": "08:30", "text": "下雨天，不想上班。", "emotion": "低落"},
                {"time": "12:00", "text": "点了外卖，比想象中好吃。", "emotion": "满足"},
                {"time": "18:00", "text": "雨停了，看到了彩虹，心情突然好了。", "emotion": "开心"}
            ]
        },
        {
            "组号": "组15",
            "场景": "被认可的一天",
            "记录": [
                {"time": "09:00", "text": "今天被客户夸了，说我很专业。", "emotion": "满足"},
                {"time": "13:00", "text": "中午和同事一起吃了新开的餐厅，不错。", "emotion": "满足"},
                {"time": "19:00", "text": "晚上练了会儿吉他，进步了一点点。", "emotion": "满足"}
            ]
        }
    ]
}

async def generate_diaries():
    """生成所有测试日记"""
    results = {
        "测试时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "评估说明": {
            "评分维度": {
                "相关性": "日记内容是否基于用户记录（1-5分，≥4分及格）",
                "情感共鸣": "语气是否适配当日情绪，有温度（1-5分，≥4分及格）",
                "结构完整": "v3.0结构完整（1-5分，5分及格）",
                "创意性": "小发现、思考碎片是否有洞察（1-5分，≥3分可接受）",
                "噪音过滤": "有效过滤无效记录（1-5分，≥4分及格）"
            },
            "v3.0结构": ["mood_tag", "emotion_type", "keywords", "what_happened", "thoughts", "small_discovery", "closing", "tomorrow_hint"]
        },
        "分层场景测试": [],
        "完整测试集": []
    }
    
    print("═══════════════════════════════════════════════════════════")
    print("  日记生成质量评估测试")
    print("═══════════════════════════════════════════════════════════\n")
    
    # 分层场景测试
    print("【分层场景测试】\n")
    for case in TEST_CASES["分层场景"]:
        group = case["组号"]
        records = case["记录"]
        count = case["记录数"]
        
        print(f"📝 {group} ({count}条记录)...")
        
        if count == 0:
            print(f"   策略: 不生成日记\n")
            results["分层场景测试"].append({
                "组号": group,
                "记录数": 0,
                "策略": "不生成日记",
                "日记": None
            })
            continue
        elif count <= 2:
            diary = await ai_service.generate_simple_diary(records, "2026-03-06")
            strategy = "简化版"
        else:
            diary = await ai_service.generate_diary(records, "2026-03-06")
            strategy = "完整版"
        
        print(f"   策略: {strategy}")
        print(f"   mood_tag: {diary.get('mood_tag', 'N/A')}")
        print(f"   emotion_type: {diary.get('emotion_type', 'N/A')}")
        print()
        
        results["分层场景测试"].append({
            "组号": group,
            "记录数": count,
            "策略": strategy,
            "输入记录": records,
            "日记": diary
        })
    
    # 完整测试集
    print("\n【完整测试集（≥3条场景）】\n")
    for case in TEST_CASES["完整测试"]:
        group = case["组号"]
        scene = case["场景"]
        records = case["记录"]
        
        print(f"📝 {group} - {scene}")
        
        diary = await ai_service.generate_diary(records, "2026-03-06")
        
        # 认知变化检测
        cognitive = await ai_service.detect_cognitive_change(records)
        
        print(f"   mood_tag: {diary.get('mood_tag', 'N/A')}")
        print(f"   what_happened: {diary.get('what_happened', [])}")
        print(f"   thoughts: {diary.get('thoughts', [])}")
        if cognitive:
            print(f"   认知变化: ✅ {cognitive.get('changes', [])[0].get('topic', 'N/A') if cognitive.get('changes') else 'N/A'}")
        print()
        
        results["完整测试集"].append({
            "组号": group,
            "场景": scene,
            "输入记录": records,
            "日记": diary,
            "认知变化": cognitive
        })
    
    return results

async def main():
    results = await generate_diaries()
    
    # 保存结果
    output_file = "/Users/jianguo/Desktop/test/回响项目/日记生成评估_2026-03-06.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("═══════════════════════════════════════════════════════════")
    print(f"✅ 测试完成！结果已保存到:")
    print(f"   {output_file}")
    print("═══════════════════════════════════════════════════════════")
    print("\n📋 评估说明:")
    print("   请打开 JSON 文件，对每条日记按以下维度评分（1-5分）:")
    print("   1. 相关性：是否基于用户记录")
    print("   2. 情感共鸣：语气是否温暖适配")
    print("   3. 结构完整：v3.0字段是否齐全")
    print("   4. 创意性：小发现是否有洞察")
    print("   5. 噪音过滤：无效内容是否过滤")

if __name__ == "__main__":
    asyncio.run(main())
