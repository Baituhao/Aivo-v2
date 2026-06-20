#!/usr/bin/env python3
"""
测试小米MiMo ASR API

小米MiMo是语音识别专用API，用于：
- 录音 → 文本转换
- 支持中文、英文等多语言
"""

import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

MIMO_API_KEY = os.getenv("MIMO_API_KEY")
MIMO_API_BASE = os.getenv("MIMO_API_BASE", "https://api.xiaomimimo.com/v1")


def test_mimo_asr():
    """测试MiMo ASR语音识别"""
    print("\n=== 测试小米MiMo ASR ===")

    if not MIMO_API_KEY:
        print("❌ 未配置 MIMO_API_KEY")
        return False

    # 创建测试音频（实际使用时替换为真实录音）
    # 这里需要一个真实的音频文件来测试
    test_audio_path = "tests/test_audio.wav"

    if not os.path.exists(test_audio_path):
        print("⚠️  未找到测试音频文件")
        print("   请准备一个测试音频文件: tests/test_audio.wav")
        print("   或录制一段语音：\"你好，今天天气怎么样？\"")
        return None

    # 读取音频并转为base64
    with open(test_audio_path, "rb") as f:
        audio_data = base64.b64encode(f.read()).decode('utf-8')

    # 构造请求
    payload = {
        "model": "mimo-v2.5-asr",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_audio",
                        "input_audio": {
                            "data": f"data:audio/wav;base64,{audio_data}"
                        }
                    }
                ]
            }
        ],
        "asr_options": {
            "language": "zh"
        }
    }

    headers = {
        "api-key": MIMO_API_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            f"{MIMO_API_BASE}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            transcript = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            print(f"✓ ASR识别成功")
            print(f"  识别结果: {transcript}")
            return True
        else:
            print(f"✗ 请求失败: {response.status_code}")
            print(f"  响应: {response.text}")
            return False

    except Exception as e:
        print(f"✗ 异常: {str(e)}")
        return False


def main():
    print("=" * 60)
    print("小米MiMo ASR 测试")
    print("=" * 60)
    print("\n📝 说明：")
    print("  MiMo API是语音识别专用，负责：录音 → 文本")
    print("  对话大脑需要另选：Qwen / DeepSeek / Claude")

    result = test_mimo_asr()

    print("\n" + "=" * 60)
    print("结论")
    print("=" * 60)
    print("✓ MiMo用于ASR（替代Whisper）")
    print("✗ MiMo不能用作对话大脑")
    print("\n建议架构：")
    print("  录音 → MiMo ASR → Qwen大脑 → 阿里TTS → 数字人驱动")


if __name__ == "__main__":
    main()
