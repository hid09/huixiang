"""
测试语音转写 API 接口
"""
import requests
import base64
import json

BASE_URL = "http://127.0.0.1:8001"

def test_voice_transcribe():
    """测试语音转写 API"""

    # 1. 注册/登录获取 token
    print("1. 注册测试用户...")
    register_resp = requests.post(f"{BASE_URL}/api/user/register", json={
        "username": "voiceapi_test",
        "password": "test123",
        "name": "语音API测试用户"
    })
    print(f"   注册响应: {register_resp.status_code}")
    print(f"   注册内容: {register_resp.json()}")

    token = None
    if register_resp.status_code == 200:
        data = register_resp.json()
        if data.get("success"):
            token = data.get("data", {}).get("access_token")
        elif "已存在" in data.get("message", ""):
            # 用户已存在，尝试登录
            print("   用户已存在，尝试登录...")
            login_resp = requests.post(f"{BASE_URL}/api/user/login", json={
                "username": "voiceapi_test",
                "password": "test123"
            })
            print(f"   登录响应: {login_resp.status_code}")
            print(f"   登录内容: {login_resp.json()}")
            if login_resp.status_code == 200:
                login_data = login_resp.json()
                if login_data.get("success"):
                    token = login_data.get("data", {}).get("access_token")

    if not token:
        print("❌ 无法获取 token")
        return False

    print(f"   ✅ Token: {token[:20]}...")

    # 2. 测试语音转写 API
    print("\n2. 测试语音转写 API...")

    # 使用一个小的测试音频（阿里云示例）
    test_audio_url = "https://dashscope.oss-cn-beijing.aliyuncs.com/audios/welcome.mp3"

    # 下载测试音频
    print(f"   下载测试音频: {test_audio_url}")
    audio_resp = requests.get(test_audio_url)
    if audio_resp.status_code != 200:
        print("   ❌ 下载音频失败")
        return False

    audio_content = audio_resp.content
    print(f"   音频大小: {len(audio_content)} bytes")

    # 上传进行转写
    headers = {"Authorization": f"Bearer {token}"}
    files = {"audio": ("test.mp3", audio_content, "audio/mpeg")}

    print("   调用转写 API...")
    transcribe_resp = requests.post(
        f"{BASE_URL}/api/records/voice/transcribe",
        headers=headers,
        files=files,
        timeout=60
    )

    print(f"   响应状态: {transcribe_resp.status_code}")
    result = transcribe_resp.json()
    print(f"   响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")

    if result.get("success"):
        print("\n   ✅ 转写成功!")
        print(f"   文本: {result['data']['text']}")
        print(f"   情绪: {result['data']['emotion']}")
        print(f"   关键词: {result['data']['keywords']}")
        return True
    else:
        print(f"\n   ❌ 转写失败: {result.get('message')}")
        return False


if __name__ == "__main__":
    print("═══════════════════════════════════════")
    print("  语音转写 API 测试")
    print("═══════════════════════════════════════\n")

    success = test_voice_transcribe()

    print("\n═══════════════════════════════════════")
    if success:
        print("  🎉 测试通过！语音转写 API 已就绪")
    else:
        print("  ⚠️ 测试失败，请检查日志")
    print("═══════════════════════════════════════")
