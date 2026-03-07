"""
测试 ASR 语音转写功能
使用阿里云百炼 qwen3-asr-flash 模型
"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI

# 配置
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

print(f"🔑 API Key: {DASHSCOPE_API_KEY[:10]}...")

# 初始化客户端
client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url=BASE_URL,
    timeout=60.0,
)


async def test_asr_with_url():
    """测试使用 URL 进行语音转写"""
    print("\n🧪 测试 ASR (URL 方式)...")

    # 使用阿里云官方示例音频
    test_audio_url = "https://dashscope.oss-cn-beijing.aliyuncs.com/audios/welcome.mp3"

    try:
        completion = client.chat.completions.create(
            model="qwen3-asr-flash",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_audio",
                            "input_audio": {
                                "data": test_audio_url
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
        print(f"✅ 转写成功!")
        print(f"📝 结果: {result}")
        return True

    except Exception as e:
        print(f"❌ 转写失败: {e}")
        return False


async def test_qwen_plus():
    """测试 qwen-plus 文本生成"""
    print("\n🧪 测试 qwen-plus (文本生成)...")

    try:
        completion = client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {"role": "user", "content": "你好，请用一句话介绍你自己。"}
            ],
            max_tokens=100,
        )

        result = completion.choices[0].message.content
        print(f"✅ 调用成功!")
        print(f"📝 结果: {result[:100]}...")
        return True

    except Exception as e:
        print(f"❌ 调用失败: {e}")
        return False


async def test_qwen_max():
    """测试 qwen-max 深度分析"""
    print("\n🧪 测试 qwen-max (深度分析)...")

    try:
        completion = client.chat.completions.create(
            model="qwen-max",
            messages=[
                {"role": "user", "content": "你好，请用一句话介绍你自己。"}
            ],
            max_tokens=100,
        )

        result = completion.choices[0].message.content
        print(f"✅ 调用成功!")
        print(f"📝 结果: {result[:100]}...")
        return True

    except Exception as e:
        print(f"❌ 调用失败: {e}")
        return False


async def main():
    print("═══════════════════════════════════════")
    print("  回响 - AI 服务测试")
    print("  模型: qwen3-asr-flash, qwen-plus, qwen-max")
    print("═══════════════════════════════════════")

    results = []

    # 测试 ASR
    results.append(("ASR (qwen3-asr-flash)", await test_asr_with_url()))

    # 测试 qwen-plus
    results.append(("文本生成 (qwen-plus)", await test_qwen_plus()))

    # 测试 qwen-max
    results.append(("深度分析 (qwen-max)", await test_qwen_max()))

    # 汇总
    print("\n═══════════════════════════════════════")
    print("  测试结果汇总")
    print("═══════════════════════════════════════")

    all_passed = True
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False

    print("═══════════════════════════════════════")

    if all_passed:
        print("🎉 所有测试通过！AI 服务已就绪。")
    else:
        print("⚠️ 部分测试失败，请检查配置。")

    return all_passed


if __name__ == "__main__":
    asyncio.run(main())
