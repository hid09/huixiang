"""
噪音过滤函数单元测试
测试目标：验证 _is_valid_record 函数能正确过滤无效记录
"""
import pytest
from app.services.diary_service import _is_valid_record, _is_semantic_fragment, _calc_info_score


class TestNoiseFilter:
    """噪音过滤测试类"""

    # ==================== 纯语气词测试 ====================
    def test_pure_emotion_chars(self):
        """测试纯语气词被过滤"""
        assert _is_valid_record("嗯嗯啊啊") == False, "纯语气词应被过滤"
        assert _is_valid_record("哼哼哈哈") == False, "纯语气词应被过滤"
        assert _is_valid_record("哦哦额") == False, "纯语气词应被过滤"
        assert _is_valid_record("嗯") == False, "单字语气词应被过滤"

    def test_repeated_chars(self):
        """测试纯重复字符被过滤"""
        assert _is_valid_record("哈哈哈哈") == False, "纯重复应被过滤"
        assert _is_valid_record("嘿嘿嘿") == False, "纯重复应被过滤"
        assert _is_valid_record("啊啊啊啊啊啊") == False, "纯重复应被过滤"

    # ==================== 测试词过滤 ====================
    def test_english_test_words(self):
        """测试英文测试词被过滤"""
        assert _is_valid_record("Hello") == False, "Hello应被过滤"
        assert _is_valid_record("hello") == False, "hello应被过滤"
        assert _is_valid_record("hello hello") == False, "hello hello应被过滤"
        assert _is_valid_record("Hi") == False, "Hi应被过滤"
        assert _is_valid_record("test") == False, "test应被过滤"
        assert _is_valid_record("ok") == False, "ok应被过滤"

    def test_chinese_test_patterns(self):
        """测试中文测试词被过滤"""
        assert _is_valid_record("喂喂喂能听到吗") == False, "测试句子应被过滤"
        assert _is_valid_record("能听到") == False, "测试句子应被过滤"
        assert _is_valid_record("这是什么") == False, "测试句子应被过滤"
        assert _is_valid_record("起开滚") == False, "测试句子应被过滤"

    # ==================== 短文本过滤 ====================
    def test_short_text(self):
        """测试过短文本被过滤"""
        assert _is_valid_record("") == False, "空文本应被过滤"
        assert _is_valid_record("   ") == False, "空格应被过滤"
        assert _is_valid_record("abc") == False, "短英文应被过滤"
        assert _is_valid_record("你好") == False, "短中文应被过滤"

    # ==================== 有效文本测试 ====================
    def test_valid_text(self):
        """测试正常文本通过"""
        assert _is_valid_record("今天完成了一个重要功能开发") == True, "正常文本应通过"
        assert _is_valid_record("产品开发还是要遵循定好的规则") == True, "正常文本应通过"
        assert _is_valid_record("终于把项目做完了，虽然累但挺有成就感") == True, "正常文本应通过"
        assert _is_valid_record("今天周三，买了杯咖啡") == True, "正常文本应通过"

    def test_valid_long_text(self):
        """测试长文本通过"""
        long_text = "今天是一个非常充实的日子，早上起来之后，我就开始整理昨天的工作内容，下午和团队一起讨论了产品方向，晚上又写了很多代码，感觉很有成就感"
        assert _is_valid_record(long_text) == True, "长文本应通过"

    # ==================== 边界情况测试 ====================
    def test_edge_cases(self):
        """测试边界情况"""
        # 带标点的正常句子
        assert _is_valid_record("今天好累，开了三个会人都麻了。") == True, "带标点的句子应通过"
        
        # 混合内容
        assert _is_valid_record("Hello，今天开会") == True, "混合内容应通过（有实质内容）"


class TestSemanticFragment:
    """语义碎片检测测试"""

    def test_incomplete_sentences(self):
        """测试不完整句子"""
        assert _is_semantic_fragment("今天做了") == True, "不完整句子应被检测"
        assert _is_semantic_fragment("刚才看了") == True, "不完整句子应被检测"
        assert _is_semantic_fragment("昨天去了") == True, "不完整句子应被检测"
        assert _is_semantic_fragment("刚去") == False, "不匹配模式的不完整句子不会被检测（符合预期）"

    def test_complete_sentences(self):
        """测试完整句子不被误判"""
        assert _is_semantic_fragment("今天做了一个重要功能") == False, "完整句子不应被误判"
        assert _is_semantic_fragment("刚才看了一场电影") == False, "完整句子不应被误判"


class TestInfoScore:
    """信息量评分测试"""

    def test_short_text_score(self):
        """测试短文本评分低"""
        score = _calc_info_score("测试")
        assert score < 2, f"短文本评分应<2，实际: {score}"

    def test_long_text_score(self):
        """测试长文本评分高"""
        score = _calc_info_score("今天完成了一个非常重要的功能开发，团队协作很顺畅，大家都很满意这个结果")
        assert score >= 3, f"长文本评分应>=3，实际: {score}"

    def test_emotion_text_score(self):
        """测试情感文本评分"""
        score = _calc_info_score("今天好累啊，但是很有成就感")
        assert score >= 2, f"情感文本评分应>=2，实际: {score}"
