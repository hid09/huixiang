"""
AI 服务层 - 封装阿里云百炼 API（OpenAI 兼容协议）

模型配置：
- ASR: qwen3-asr-flash (语音转文字)
- 分析: qwen-plus (情绪/标签提取)
- 日常生成: qwen-plus (每日日记生成)
- 深度智能: qwen-max (月度/年度复盘、认知洞察)
"""
import json
import base64
import logging
import asyncio
from typing import Optional, List, Dict, Any
from openai import OpenAI
from app.config import DASHSCOPE_API_KEY

logger = logging.getLogger(__name__)

# 模型配置
MODEL_ASR = "qwen3-asr-flash"
MODEL_ANALYSIS = "qwen-plus"
MODEL_DIARY = "qwen-plus"
MODEL_DEEP = "qwen-max"

# OpenAI 兼容协议 base URL
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# 初始化 OpenAI 客户端
client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url=BASE_URL,
    timeout=60.0,
)

# ==================== 情绪标准化配置 ====================

# 标准情绪池（与 Prompt 中的定义一致）
VALID_EMOTIONS = {
    # 正向
    "开心", "兴奋", "满足", "期待", "感激", "平静",
    # 负向
    "疲惫", "焦虑", "低落", "愤怒", "失望", "恐惧", "孤独", "压力", "烦躁",
    # 中性
    "困惑", "麻木",
}

EMOTION_MAPPING = {
    # ========== 满足类 ==========
    "怀念": "满足",      # 回忆是温暖的
    "思念": "低落",      # 想家/想人通常带点伤感
    "感动": "满足",      # 被温暖到
    "骄傲": "满足",      # 自豪
    "得意": "满足",      # 小骄傲
    "舒畅": "满足",      # 舒服畅快
    "成就感": "满足",    # 做成了事
    "解脱": "满足",      # 如释重负
    "温馨": "满足",      # 温暖
    "幸福": "满足",      # 幸福感
    "欣慰": "满足",      # 欣喜安慰
    "释怀": "满足",      # 放下了
    "佩服": "满足",      # 敬佩
    "温暖": "满足",      # 被关怀
    "甜蜜": "满足",      # 甜蜜感
    "轻松": "满足",      # 轻松自在
    # ========== 开心类 ==========
    "愉悦": "开心",      # 快乐
    "喜悦": "开心",      # 喜气洋洋
    "欢乐": "开心",      # 欢快
    # ========== 兴奋类 ==========
    "激动": "兴奋",      # 激动不已
    "震撼": "兴奋",      # 震撼人心
    # ========== 期待类 ==========
    "盼望": "期待",      # 盼望
    "渴望": "期待",      # 迫切期待
    # ========== 感激类 ==========
    "感谢": "感激",      # 感谢
    "感恩": "感激",      # 感恩
    # ========== 平静类 ==========
    "安心": "平静",      # 放心
    "感慨": "平静",      # 感慨
    "柔软": "平静",      # 柔软
    "温柔": "平静",      # 温柔
    "无聊": "平静",      # 无聊
    "羡慕": "平静",      # 羡慕
    "敬畏": "平静",      # 敬畏
    # ========== 困惑类 ==========
    "迷茫": "困惑",      # 迷茫
    "不解": "困惑",      # 不理解
    # ========== 疲惫类 ==========
    "累": "疲惫",        # 累
    "心累": "疲惫",      # 心累
    "痛苦": "疲惫",      # 很难受
    # ========== 焦虑类 ==========
    "紧张": "焦虑",      # 精神紧绷
    "焦急": "焦虑",      # 焦急
    "忐忑": "焦虑",      # 七上八下
    "担心": "焦虑",      # 担心
    "害羞": "兴奋",      # 害羞通常伴随心跳加速
    # ========== 低落类 ==========
    "自卑": "低落",      # 看不起自己
    "委屈": "低落",      # 受了气
    "压抑": "低落",      # 心情沉重
    "忧郁": "低落",      # 忧愁
    "感伤": "低落",      # 伤感
    "同情": "低落",      # 为别人难过
    "唏嘘": "低落",      # 唏嘘
    "无奈": "低落",      # 无奈
    "惆怅": "低落",      # 惆怅
    "郁闷": "低落",      # 郁闷
    "沮丧": "低落",      # 沮丧
    "轻微低落": "低落",  # 轻微低落
    "轻微感伤": "低落",  # 轻微感伤
    "被忽视感": "低落",  # 被忽视
    "羞耻": "低落",      # 羞耻
    "受伤": "低落",      # 受伤
    "怜悯": "低落",      # 怜悯
    "伤感": "低落",      # 伤感
    "心碎": "低落",      # 心碎
    "无助": "低落",      # 无助
    "心疼": "低落",      # 心疼
    "愧疚": "低落",      # 愧疚
    # ========== 愤怒类 ==========
    "生气": "愤怒",      # 生气
    # ========== 烦躁类 ==========
    "不爽": "烦躁",      # 不高兴
    "倒霉": "烦躁",      # 运气不好
    "不满": "烦躁",      # 不满意
    "厌恶": "烦躁",      # 讨厌
    # ========== 恐惧类 ==========
    "恐惧": "焦虑",      # 害怕
    "害怕": "恐惧",      # 害怕
    "惊慌": "恐惧",      # 惊慌
    # ========== 其他 ==========
    "释然": "满足",      # 释然
    "emo": "低落",       # emo
    "开心但累": "满足",  # 开心但累
    # 注意: 孤独是独立情绪，不需要映射
}


def normalize_emotion(emotion: str) -> str:
    """
    将情绪词标准化为预定义列表中的值

    Args:
        emotion: AI 返回的原始情绪词

    Returns:
        标准化后的情绪词
    """
    if not emotion:
        return "平静"

    # 1. 如果已经是标准值，直接返回
    if emotion in VALID_EMOTIONS:
        return emotion

    # 2. 查映射表
    if emotion in EMOTION_MAPPING:
        logger.info(f"情绪标准化: {emotion} -> {EMOTION_MAPPING[emotion]}")
        return EMOTION_MAPPING[emotion]

    # 3. 未知情绪，记录日志，返回默认值
    logger.warning(f"未知情绪词: {emotion}，映射为默认值: 平静")
    return "平静"


class AIService:
    """AI 服务类 - 使用 OpenAI 兼容协议"""

    # ==================== 语音转写 ====================

    @staticmethod
    async def transcribe_audio_url(audio_url: str) -> Dict[str, Any]:
        """
        通过 URL 进行语音转文字（含语音情感识别）

        Args:
            audio_url: 音频文件 URL（需要公网可访问）

        Returns:
            {"text": "转写文本", "asr_emotion": "neutral"}，失败返回 {"text": None, "asr_emotion": "neutral"}
        """
        default_result = {"text": None, "asr_emotion": "neutral"}
        try:
            logger.info(f"开始语音转写(URL): {audio_url}")

            completion = client.chat.completions.create(
                model=MODEL_ASR,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_audio",
                                "input_audio": {
                                    "data": audio_url
                                }
                            }
                        ]
                    }
                ],
                extra_body={
                    "asr_options": {
                        "enable_itn": False
                    }
                }
            )

            result = completion.choices[0].message.content

            # 提取 ASR 语音情感（从 annotations 中）
            asr_emotion = "neutral"
            message = completion.choices[0].message
            if hasattr(message, 'annotations') and message.annotations:
                for anno in message.annotations:
                    if isinstance(anno, dict) and anno.get("type") == "audio_info":
                        asr_emotion = anno.get("emotion", "neutral")
                        break

            logger.info(f"转写成功: {result[:50]}..., ASR情感: {asr_emotion}")
            return {"text": result, "asr_emotion": asr_emotion}

        except Exception as e:
            logger.error(f"语音转写异常: {e}")
            return default_result

    @staticmethod
    async def transcribe_audio_file(file_content: bytes, file_format: str = "webm") -> Dict[str, Any]:
        """
        上传音频文件进行转写（Base64 方式，含语音情感识别）

        Args:
            file_content: 音频文件二进制内容
            file_format: 音频格式 (webm, wav, mp3, m4a 等)

        Returns:
            {"text": "转写文本", "asr_emotion": "neutral"}，失败返回 {"text": None, "asr_emotion": "neutral"}
        """
        import time
        default_result = {"text": None, "asr_emotion": "neutral"}
        try:
            t_start = time.time()
            print(f"🎤 [ASR] 开始音频转写, 格式: {file_format}, 大小: {len(file_content)/1024:.1f} KB", flush=True)

            # 获取 MIME 类型
            mime_types = {
                "webm": "audio/webm",
                "wav": "audio/wav",
                "mp3": "audio/mpeg",
                "m4a": "audio/mp4",
                "ogg": "audio/ogg",
                "flac": "audio/flac",
            }
            mime_type = mime_types.get(file_format.lower(), "audio/webm")

            # 转换为 Base64 Data URI
            t_encode_start = time.time()
            base64_str = base64.b64encode(file_content).decode()
            data_uri = f"data:{mime_type};base64,{base64_str}"
            t_encode_end = time.time()
            print(f"🎤 [ASR] Base64编码耗时: {t_encode_end - t_encode_start:.3f}秒, 编码后大小: {len(data_uri)/1024:.1f} KB", flush=True)

            # 调用千问ASR API
            t_api_start = time.time()
            print(f"🎤 [ASR] 开始调用千问API...", flush=True)
            completion = client.chat.completions.create(
                model=MODEL_ASR,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_audio",
                                "input_audio": {
                                    "data": data_uri
                                }
                            }
                        ]
                    }
                ],
                extra_body={
                    "asr_options": {
                        "enable_itn": False
                    }
                }
            )
            t_api_end = time.time()
            api_time = t_api_end - t_api_start
            print(f"🎤 [ASR] 千问API返回耗时: {api_time:.2f}秒 {'⚠️' if api_time > 3 else '✅'}", flush=True)

            result = completion.choices[0].message.content

            # 提取 ASR 语音情感（从 annotations 中）
            asr_emotion = "neutral"
            message = completion.choices[0].message
            if hasattr(message, 'annotations') and message.annotations:
                for anno in message.annotations:
                    if isinstance(anno, dict) and anno.get("type") == "audio_info":
                        asr_emotion = anno.get("emotion", "neutral")
                        break

            t_total = time.time() - t_start
            print(f"🎤 [ASR] 转写成功! 总耗时: {t_total:.2f}秒, 文本: {result[:30]}..., ASR情感: {asr_emotion}", flush=True)
            return {"text": result, "asr_emotion": asr_emotion}

        except Exception as e:
            logger.error(f"语音转写异常: {e}")
            import traceback
            traceback.print_exc()
            return default_result

    # 兼容旧接口
    @staticmethod
    async def transcribe_audio(audio_url: str) -> Dict[str, Any]:
        """兼容旧接口 - 通过 URL 转写（返回 dict）"""
        return await AIService.transcribe_audio_url(audio_url)

    # ==================== 情绪/标签分析（增强版）====================

    @staticmethod
    async def analyze_record(text: str) -> Dict[str, Any]:
        """
        分析单条记录：提取混合情绪、触发事件、潜在需求等

        Args:
            text: 记录文本

        Returns:
            {
                "emotion": "positive/neutral/negative",  # 主导情绪分类
                "emotion_score": 0.8,
                "mixed_emotions": {"满足": 6, "疲惫": 7},  # 混合情绪及强度
                "primary_emotion": "疲惫",  # 具体的主导情绪
                "input_type": "情绪表达",  # 输入类型
                "triggers": ["项目上线"],  # 触发事件
                "unspoken_need": "希望付出被看见",  # 潜在需求
                "energy_level": 4,  # 能量水平 1-10
                "brief_summary": "一句话概括",
                "keywords": ["工作", "朋友"],
                "topics": ["社交", "休闲"]
            }
        """
        prompt = f"""你是一位专业的心理咨询师，擅长细腻的情绪分析。请根据用户输入，严格按以下规则输出JSON。

【类型判断】
- A. 情绪表达/回忆过去：包含个人情绪词（如累、开心）或明显情感倾向；回忆过去需分析其中情绪。
- B. 观点/方法论/事实/计划：客观陈述，无明显情绪词（常见特征词："应该""建议""关键是""不是非得""还是要""可以考虑"等）。

【处理方式】
- 类型B：直接返回中性结果。
- 类型A：深度分析情绪，识别混合情绪及强度(1-10)，并推断触发事件和潜在需求。

【情绪参考】
- 正向：开心、兴奋、满足、期待、感激
- 负向：疲惫、焦虑、低落、愤怒、失望、恐惧、孤独、压力、烦躁
- 中性：平静、困惑、麻木

【关键边界规则】
- 强调词（最重要的/必须）≠ 情绪，仍视为中性观点。
- 言外之意适度解读（如"还行吧"可能隐含失落），但不可过度。
- 若输入既包含观点又含情绪，按情绪表达处理。

【输出JSON格式】
{{
  "mixed_emotions": {{"情绪名": 强度(1-10)}},
  "primary_emotion": "主导情绪",
  "emotion": "positive/neutral/negative",
  "emotion_score": 0.0~1.0,
  "input_type": "情绪表达/回忆过去/观点分享/事实陈述/计划目标",
  "triggers": ["触发事件"],
  "unspoken_need": "潜在需求",
  "energy_level": 1-10,
  "brief_summary": "一句话概括核心内容",
  "keywords": ["关键词"],
  "topics": ["话题标签"]
}}

【示例】
输入："Web coding最重要的还是要先做计划"
输出：{{"mixed_emotions":{{"平静":5}},"primary_emotion":"平静","emotion":"neutral","emotion_score":0.5,"input_type":"观点分享","triggers":[],"unspoken_need":"","energy_level":5,"brief_summary":"用户分享编程需先计划的观点","keywords":["Web coding","计划"],"topics":["技术方法论"]}}

输入："今天好累，开了三个会人都麻了"
输出：{{"mixed_emotions":{{"疲惫":8}},"primary_emotion":"疲惫","emotion":"negative","emotion_score":0.2,"input_type":"情绪表达","triggers":["开了三个会"],"unspoken_need":"希望减少会议或获得休息","energy_level":2,"brief_summary":"用户因连续开会感到极度疲惫","keywords":["累","开会"],"topics":["工作压力"]}}

用户输入：{text}

只输出JSON，不要任何其他内容。"""

        import time
        try:
            t_start = time.time()
            print(f"🧠 [分析] 开始情绪分析, 文本长度: {len(text)}字符", flush=True)

            completion = client.chat.completions.create(
                model=MODEL_ANALYSIS,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.3,
            )

            t_api = time.time() - t_start
            print(f"🧠 [分析] qwen-plus API耗时: {t_api:.2f}秒 {'⚠️' if t_api > 3 else '✅'}", flush=True)

            content = completion.choices[0].message.content
            # 尝试解析 JSON
            try:
                # 去除可能的 markdown 代码块标记
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]

                result = json.loads(content.strip())

                # 确保必要字段存在
                result.setdefault("emotion", "neutral")
                result.setdefault("emotion_score", 0.5)
                result.setdefault("mixed_emotions", {})
                result.setdefault("primary_emotion", "平静")
                result.setdefault("input_type", "情绪表达")  # 新增
                result.setdefault("triggers", [])
                result.setdefault("unspoken_need", "")
                result.setdefault("energy_level", 5)
                result.setdefault("brief_summary", "")
                result.setdefault("keywords", [])
                result.setdefault("topics", [])

                # 情绪标准化：确保 primary_emotion 和 mixed_emotions 中的情绪词都在预定义范围内
                result["primary_emotion"] = normalize_emotion(result.get("primary_emotion"))
                if result.get("mixed_emotions"):
                    result["mixed_emotions"] = {
                        normalize_emotion(k): v
                        for k, v in result["mixed_emotions"].items()
                    }

                logger.info(f"分析成功: primary_emotion={result.get('primary_emotion')}, mixed={result.get('mixed_emotions')}")
                return result
            except json.JSONDecodeError:
                logger.error(f"JSON 解析失败: {content}")
                return AIService._get_default_analysis()

        except Exception as e:
            logger.error(f"分析异常: {e}")
            return AIService._get_default_analysis()

    @staticmethod
    def _get_default_analysis() -> Dict[str, Any]:
        """返回默认分析结果"""
        return {
            "emotion": "neutral",
            "emotion_score": 0.5,
            "mixed_emotions": {},
            "primary_emotion": "平静",
            "input_type": "情绪表达",
            "triggers": [],
            "unspoken_need": "",
            "energy_level": 5,
            "brief_summary": "",
            "keywords": [],
            "topics": []
        }

    # ==================== 日记生成（v1.1 分层策略）====================

    @staticmethod
    async def generate_simple_diary(records: List[Dict[str, Any]], date_str: str) -> Dict[str, Any]:
        """
        简化版日记生成（1-2条有效记录时使用）

        特点：
        - 只生成 what_happened（整合1-2条记录）
        - thoughts 固定为空 []
        - small_discovery 固定为 null
        - closing 更简短温柔
        - 不生成 tomorrow_hint

        Args:
            records: 当日记录列表（1-2条）
            date_str: 日期字符串

        Returns:
            简化版日记结构
        """
        # 构建记录摘要
        records_text = "\n".join([
            f"- {r.get('text', '')}"
            for r in records
        ])

        prompt = f"""你是"回响"，一个懂用户的老朋友。

【用户今天说的】
{records_text}

【你的任务】
用户今天只说了很少的话，帮他把这一两句整理成一句简洁的记录。

【输出要求】
返回 JSON（只返回 JSON，不要其他内容）：
{{
    "mood_tag": "简短的心情标签，5字以内",
    "emotion_type": "positive/neutral/negative 之一",
    "keywords": ["关键词1"],
    "what_happened": ["一句话概括用户今天说的"],
    "thoughts": [],
    "small_discovery": null,
    "closing": "简短温柔的结束语，10字以内"
}}

【规则】
1. what_happened：用第三人称，一句话概括，10-20字
2. thoughts：固定为空数组 []
3. small_discovery：固定为 null
4. closing：简短温柔，如"累了就歇歇 🌙"、"晚安"
5. 不要 AI 腔，不要"综上所述"

【示例】
用户说："今天有点累，昨天练得太多了"

输出：
{{
    "mood_tag": "需要休息",
    "emotion_type": "negative",
    "keywords": ["休息"],
    "what_happened": ["昨天运动量大，今天感觉累"],
    "thoughts": [],
    "small_discovery": null,
    "closing": "歇歇吧 🌙"
}}
"""

        try:
            completion = client.chat.completions.create(
                model=MODEL_DIARY,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7,
            )

            content = completion.choices[0].message.content
            try:
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]

                result = json.loads(content.strip())

                # 确保字段存在
                result.setdefault("mood_tag", "普通的一天")
                result.setdefault("emotion_type", "neutral")
                result.setdefault("keywords", [])
                result.setdefault("what_happened", [])
                result.setdefault("thoughts", [])
                result.setdefault("small_discovery", None)
                result.setdefault("closing", "晚安 🌙")
                result.setdefault("tomorrow_hint", None)

                logger.info(f"简化版日记生成成功: {date_str}")
                return result

            except json.JSONDecodeError:
                logger.error(f"简化版 JSON 解析失败: {content}")
                return AIService._get_default_simple_diary(date_str, records)

        except Exception as e:
            logger.error(f"简化版日记生成异常: {e}")
            return AIService._get_default_simple_diary(date_str, records)

    @staticmethod
    def _get_default_simple_diary(date_str: str, records: List[Dict]) -> Dict[str, Any]:
        """简化版默认日记"""
        # 尝试从记录中提取文本
        if records:
            text = records[0].get("text", "")
            what_happened = [text[:20] + "..." if len(text) > 20 else text]
        else:
            what_happened = ["今天记录了一些想法"]

        return {
            "mood_tag": "普通的一天",
            "emotion_type": "neutral",
            "keywords": [],
            "what_happened": what_happened,
            "thoughts": [],
            "small_discovery": None,
            "closing": "晚安 🌙",
            "tomorrow_hint": None
        }

    # ==================== 日记生成（完整版）====================

    @staticmethod
    async def generate_diary(records: List[Dict[str, Any]], date_str: str) -> Dict[str, Any]:
        """
        根据当日记录生成结构化日记（v3.0）

        Args:
            records: 当日记录列表 [{"text": "...", "time": "09:30", "emotion": "positive"}, ...]
            date_str: 日期字符串 "2024-03-01"

        Returns:
            {
                "mood_tag": "心情标签",
                "emotion_type": "positive/neutral/negative/mixed",
                "keywords": ["关键词1", "关键词2"],
                "what_happened": ["事件1", "事件2"],
                "thoughts": ["思考1", "思考2"],
                "small_discovery": "小发现或None",
                "closing": "结束语",
                "tomorrow_hint": "明日提示或None"
            }
        """
        # 构建记录摘要
        records_text = "\n".join([
            f"- [{r.get('time', '未知时间')}] ({r.get('emotion', '中性')}) {r.get('text', '')}"
            for r in records
        ])

        prompt = f"""你是"回响"，一个真正懂用户的老朋友。

【你是谁】
- 你像一个认识很久的朋友，记得他说过的话，能听出他没说出口的心事
- 你不会评判他，但你能看见他的开心、委屈、疲惫、期待
- 你说话很自然，像发微信一样，不会用"值得一提的是"这种AI腔

【用户今天的记录】
日期：{date_str}
{records_text}

【你在做什么】
帮他把今天的碎碎念整理成一份有温度的日记。

【核心规则：what_happened 和 thoughts 必须区分】

这是最重要的规则！两个内容不能重复：

1. what_happened（客观事件）：
   - 用户**做了什么、发生了什么**
   - 用第三人称描述："早上开会"、"中午和朋友吃饭"
   - 合并同类事件，不要流水账
   - 每条 10-20 字，2-4 条

2. thoughts（主观思考）：
   - 用户的**想法、感悟、灵感**，用原话提炼
   - 必须是用户**在思考的内容**，不是发生的事
   - 如果用户只是说了发生的事，没有表达想法，thoughts 就留空 []
   - 每条一句话，1-3 条

【判断方法】
- "今天去跑步了" → what_happened
- "觉得跑步让心情变好" → thoughts
- "中午吃了火锅" → what_happened
- "发现好吃的火锅能治愈一天" → thoughts
- "今天很累" → what_happened（这是状态描述）
- "觉得累是因为昨晚没睡好" → thoughts

【绝对禁止】
❌ 把同一条记录同时放进 what_happened 和 thoughts
❌ 用 AI 腔转述："用户今天在思考..."
❌ 没有想法时硬编 thoughts
❌ 综上所述值得注意的是建议你等 AI 腔

【字段说明】

1. mood_tag：给今天起个有温度的标签（5-10字）
2. emotion_type：positive/neutral/negative/mixed
3. keywords：2-4个关键词
4. what_happened：客观事件，2-4条
5. thoughts：主观想法，没有就 []
6. small_discovery：小发现，没有就 null
7. closing：简短温柔的结束语
8. tomorrow_hint：明天计划，没有就 null

返回JSON：
{{
    "mood_tag": "心情标签",
    "emotion_type": "positive/neutral/negative/mixed",
    "keywords": ["关键词1", "关键词2"],
    "what_happened": ["事件1", "事件2"],
    "thoughts": ["思考1"],
    "small_discovery": "小发现或null",
    "closing": "结束语",
    "tomorrow_hint": "明日提示或null"
}}

【示例1】
用户记录：
- 10:00 "开会又被老板diss了，烦"
- 14:00 "同事给我带了奶茶，还行"
- 20:00 "回家路上看到夕阳挺美的"
- 22:00 "在想要不要给产品加个暗黑模式"

输出：
{{
    "mood_tag": "被小事治愈的一天",
    "emotion_type": "mixed",
    "keywords": ["工作", "同事", "夕阳"],
    "what_happened": [
        "早上开会时被老板批评了",
        "同事给带了奶茶，傍晚看了夕阳"
    ],
    "thoughts": ["想给产品加个暗黑模式"],
    "small_discovery": "小小的善意能抵消挫败感",
    "closing": "今天辛苦了，晚安 🌙",
    "tomorrow_hint": null
}}

【示例2 - 没有思考时】
用户记录：
- 09:00 "今天有点累"
- 18:00 "去超市买了点东西"

输出：
{{
    "mood_tag": "普通的一天",
    "emotion_type": "neutral",
    "keywords": ["休息", "购物"],
    "what_happened": ["今天感觉有点累", "傍晚去超市买了东西"],
    "thoughts": [],
    "small_discovery": null,
    "closing": "早点休息 🌙",
    "tomorrow_hint": null
}}
"""

        try:
            completion = client.chat.completions.create(
                model=MODEL_DIARY,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.7,
            )

            content = completion.choices[0].message.content
            try:
                # 去除可能的 markdown 代码块标记
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]

                result = json.loads(content.strip())

                # 确保必要字段存在（v3.0）
                result.setdefault("mood_tag", "普通的一天")
                result.setdefault("emotion_type", "neutral")
                result.setdefault("keywords", [])
                result.setdefault("what_happened", [])
                result.setdefault("thoughts", [])
                result.setdefault("small_discovery", None)
                result.setdefault("closing", "明天见！")
                result.setdefault("tomorrow_hint", None)

                # emotion_type 兜底处理：只允许 positive/neutral/negative/mixed
                valid_emotions = ["positive", "neutral", "negative", "mixed"]
                if result.get("emotion_type") not in valid_emotions:
                    # 尝试映射常见值
                    emotion_mapping = {
                        "calm": "neutral",
                        "happy": "positive",
                        "sad": "negative",
                        "anxious": "negative",
                        "tired": "negative",
                    }
                    original = result.get("emotion_type", "neutral")
                    result["emotion_type"] = emotion_mapping.get(original, "neutral")
                    logger.warning(f"emotion_type 兜底映射: {original} -> {result['emotion_type']}")

                logger.info(f"日记生成成功: {date_str}, mood_tag={result.get('mood_tag')}")
                return result
            except json.JSONDecodeError:
                logger.error(f"JSON 解析失败: {content}")
                return AIService._get_default_diary(date_str)

        except Exception as e:
            logger.error(f"日记生成异常: {e}")
            return AIService._get_default_diary(date_str)

    @staticmethod
    def _get_default_diary(date_str: str) -> Dict[str, Any]:
        """返回默认日记结构（v3.0）"""
        return {
            "mood_tag": "普通的一天",
            "emotion_type": "neutral",
            "keywords": [],
            "what_happened": ["今天记录了一些想法和感受"],
            "thoughts": [],
            "small_discovery": None,
            "closing": "明天见，愿你有个好梦 🌙",
            "tomorrow_hint": None
        }

    # ==================== 认知变化检测 ====================

    @staticmethod
    def _has_change_signals(text: str) -> bool:
        """检测文本中是否有变化信号词"""
        signals = ["突然", "意识到", "以前", "改变", "发现", "曾经", "过去", "原来", "不一样了", "变了"]
        return any(s in text for s in signals)

    @staticmethod
    async def detect_cognitive_change(records: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        检测认知变化（只在有信号词时触发）

        Args:
            records: 当日记录列表

        Returns:
            {
                "has_change": true/false,
                "changes": [{
                    "type": "变化类型",
                    "topic": "涉及的话题",
                    "before": "之前的想法",
                    "after": "现在的想法",
                    "evidence": "用户原话证据"
                }],
                "insight": "对这个变化的洞察"
            }
            或 None（无变化或无信号词）
        """
        # 合并所有记录文本
        all_text = " ".join([r.get("text", "") for r in records])

        # 检查是否有变化信号词
        if not AIService._has_change_signals(all_text):
            logger.info("未检测到变化信号词，跳过认知变化检测")
            return None

        records_text = "\n".join([
            f"- {r.get('text', '')}"
            for r in records
        ])

        prompt = f"""你是"回响"，一个善于观察的成长伙伴。请分析用户的当前记录，检测用户是否**自己说出了变化**。

【用户记录】
{records_text}

【检测信号】
用户可能用以下方式表达变化：
- "以前我觉得...现在我发现..."
- "我突然意识到..."
- "和过去不同的是..."
- "原来我一直..."
- "我发现我变了..."

【变化类型】
1. 观点转变：对某事的看法发生了改变
2. 自我认知：对自己有了新的认识
3. 关系觉察：对人际关系的理解加深了
4. 价值观萌芽：一个新的价值观在形成
5. 行为动机：理解了自己为什么会做某事

返回JSON（只返回JSON，不要其他内容）：
{{
    "has_change": true或false,
    "changes": [
        {{
            "type": "变化类型",
            "topic": "涉及的话题",
            "before": "之前的想法（简短）",
            "after": "现在的想法（简短）",
            "evidence": "用户原话中的证据"
        }}
    ],
    "insight": "对这个变化的温和洞察（一句话，帮用户深化觉察）"
}}

【注意】
- 只报告真实、有意义的变化，不要过度解读
- 如果没有明显变化，返回 {{"has_change": false}}
- before 和 after 要简短有力，便于展示
"""

        try:
            completion = client.chat.completions.create(
                model=MODEL_DIARY,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.5,
            )

            content = completion.choices[0].message.content
            try:
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]

                result = json.loads(content.strip())

                if not result.get("has_change"):
                    return None

                logger.info(f"检测到认知变化: {result.get('changes', [])}")
                return result

            except json.JSONDecodeError:
                logger.error(f"认知变化 JSON 解析失败: {content}")
                return None

        except Exception as e:
            logger.error(f"认知变化检测异常: {e}")
            return None

    # ==================== 周回顾生成 ====================

    @staticmethod
    async def generate_weekly_review(
        records: List[Dict[str, Any]],
        week_start: str,
        week_end: str
    ) -> Dict[str, Any]:
        """
        生成周回顾

        Args:
            records: 本周所有记录
            week_start: 周开始日期
            week_end: 周结束日期

        Returns:
            周回顾数据
        """
        records_text = "\n".join([
            f"- [{r.get('date', '')} {r.get('time', '')}] {r.get('text', '')}"
            for r in records
        ])

        prompt = f"""你是一个专业的周回顾分析师。请根据用户本周的记录，生成一份有洞察力的周回顾。

时间范围：{week_start} 至 {week_end}

本周记录：
{records_text}

请生成周回顾，返回 JSON 格式：
{{
    "week_summary": "本周概述（50-80字）",
    "emotion_trend": ["周一:positive", "周二:neutral", ...],
    "top_keywords": ["关键词1", "关键词2", "关键词3", "关键词4", "关键词5"],
    "focus_topics": ["关注点1", "关注点2", "关注点3"],
    "habit_changes": ["习惯变化1", "习惯变化2"],
    "cognitive_insights": ["认知洞察1", "认知洞察2"],
    "suggestions": ["建议1", "建议2", "建议3"]
}}

要求：
1. week_summary 用温暖有洞察力的语气
2. emotion_trend 列出每天的总体情绪
3. top_keywords 本周高频关键词
4. focus_topics 本周主要关注的话题
5. suggestions 给出 2-3 条下周建议
"""

        try:
            completion = client.chat.completions.create(
                model=MODEL_ANALYSIS,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.6,
            )

            content = completion.choices[0].message.content
            try:
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]

                result = json.loads(content.strip())
                logger.info(f"周回顾生成成功: {week_start} - {week_end}")
                return result
            except json.JSONDecodeError:
                logger.error(f"JSON 解析失败: {content}")
                return AIService._get_default_weekly_review()

        except Exception as e:
            logger.error(f"周回顾生成异常: {e}")
            return AIService._get_default_weekly_review()

    @staticmethod
    def _get_default_weekly_review() -> Dict[str, Any]:
        """返回默认周回顾"""
        return {
            "week_summary": "这一周你记录了许多想法和感受。",
            "emotion_trend": [],
            "top_keywords": [],
            "focus_topics": [],
            "habit_changes": [],
            "cognitive_insights": [],
            "suggestions": ["继续坚持记录，让成长看得见"]
        }

    # ==================== 深度分析（使用 qwen-max）====================

    @staticmethod
    async def generate_monthly_review(
        records: List[Dict[str, Any]],
        month_start: str,
        month_end: str
    ) -> Dict[str, Any]:
        """
        生成月度复盘（使用 qwen-max）

        Args:
            records: 本月所有记录
            month_start: 月开始日期
            month_end: 月结束日期

        Returns:
            月度复盘数据
        """
        records_text = "\n".join([
            f"- [{r.get('date', '')} {r.get('time', '')}] ({r.get('emotion', '')}) {r.get('text', '')}"
            for r in records
        ])

        prompt = f"""你是一个专业的月度复盘分析师。请根据用户本月的记录，生成一份深度的月度复盘报告。

时间范围：{month_start} 至 {month_end}

本月记录：
{records_text}

请生成月度复盘，返回 JSON 格式：
{{
    "month_summary": "本月概述（80-120字）",
    "emotion_distribution": {{"positive": 0.5, "neutral": 0.3, "negative": 0.2}},
    "key_events": ["重要事件1", "重要事件2", "重要事件3"],
    "growth_points": ["成长点1", "成长点2"],
    "challenges": ["挑战1", "挑战2"],
    "cognitive_changes": ["认知变化1（对比过去和现在）"],
    "next_month_suggestions": ["下月建议1", "下月建议2", "下月建议3"]
}}

要求：
1. 深度分析，有洞察力
2. 语气温暖但专业
3. 认知变化要具体，对比过去和现在的观点差异
"""

        try:
            completion = client.chat.completions.create(
                model=MODEL_DEEP,  # 使用 qwen-max
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3000,
                temperature=0.6,
            )

            content = completion.choices[0].message.content
            try:
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]

                result = json.loads(content.strip())
                logger.info(f"月度复盘生成成功: {month_start} - {month_end}")
                return result
            except json.JSONDecodeError:
                logger.error(f"JSON 解析失败: {content}")
                return AIService._get_default_monthly_review()

        except Exception as e:
            logger.error(f"月度复盘生成异常: {e}")
            return AIService._get_default_monthly_review()

    @staticmethod
    def _get_default_monthly_review() -> Dict[str, Any]:
        """返回默认月度复盘"""
        return {
            "month_summary": "这个月你记录了许多想法和感受。",
            "emotion_distribution": {"positive": 0.5, "neutral": 0.3, "negative": 0.2},
            "key_events": [],
            "growth_points": ["坚持记录本身就是一种成长"],
            "challenges": [],
            "cognitive_changes": [],
            "next_month_suggestions": ["继续记录，发现更多自己"]
        }


# 创建全局实例
ai_service = AIService()
