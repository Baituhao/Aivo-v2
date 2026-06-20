#!/usr/bin/env python3
"""
完整测试：MiMo ASR + TTS
"""

import os
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("MIMO_API_KEY"),
    base_url=os.getenv("MIMO_API_BASE", "https://token-plan-cn.xiaomimimo.com/v1")
)


def test_tts():
    """测试TTS：多种音色和情感"""
    print("\n" + "=" * 60)
    print("测试MiMo TTS")
    print("=" * 60)

    tests = [
        {
            "name": "中文女声-冰糖（明亮活泼）",
            "voice": "冰糖",
            "user_msg": "使用明亮活泼的语气",
            "text": "你好，今天天气真不错！",
            "output": "tests/output_bingtang.wav"
        },
        {
            "name": "中文男声-苏打（兴奋情感）",
            "voice": "苏打",
            "user_msg": "表现出惊喜和兴奋的情感",
            "text": "[兴奋]太好了！明天是晴天！",
            "output": "tests/output_suoda_excited.wav"
        },
        {
            "name": "中文女声-茉莉（平静温柔）",
            "voice": "茉莉",
            "user_msg": "使用平静温柔的语气",
            "text": "别担心，一切都会好起来的。",
            "output": "tests/output_moli_calm.wav"
        }
    ]

    results = []

    for test in tests:
        print(f"\n测试：{test['name']}")
        try:
            completion = client.chat.completions.create(
                model="mimo-v2.5-tts",
                modalities=["text", "audio"],
                audio={"voice": test["voice"], "format": "wav"},
                messages=[
                    {"role": "user", "content": test["user_msg"]},
                    {"role": "assistant", "content": test["text"]}
                ]
            )

            # 保存音频
            audio_base64 = completion.choices[0].message.audio.data
            audio_bytes = base64.b64decode(audio_base64)

            with open(test["output"], "wb") as f:
                f.write(audio_bytes)

            print(f"  ✓ 成功生成")
            print(f"  音色: {test['voice']}")
            print(f"  文本: {test['text']}")
            print(f"  输出: {test['output']}")
            results.append(True)

        except Exception as e:
            print(f"  ✗ 失败: {str(e)}")
            results.append(False)

    return all(results)


def test_asr():
    """测试ASR：语音识别"""
    print("\n" + "=" * 60)
    print("测试MiMo ASR")
    print("=" * 60)

    test_audio_path = "tests/test_audio.wav"

    if not os.path.exists(test_audio_path):
        print("⚠️  未找到测试音频: tests/test_audio.wav")
        print("   请先录制测试音频：")
        print("   python tests/record_audio.py")
        return None

    try:
        with open(test_audio_path, "rb") as f:
            audio_bytes = f.read()
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

        completion = client.chat.completions.create(
            model="mimo-v2.5-asr",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_audio",
                            "input_audio": {
                                "data": f"data:audio/wav;base64,{audio_base64}"
                            }
                        }
                    ]
                }
            ],
            extra_body={
                "asr_options": {
                    "language": "zh"
                }
            }
        )

        transcript = completion.choices[0].message.content
        print(f"\n✓ ASR识别成功")
        print(f"  识别结果: {transcript}")
        return True

    except Exception as e:
        print(f"\n✗ ASR失败: {str(e)}")
        return False


def main():
    print("=" * 60)
    print("MiMo 完整能力测试（ASR + TTS）")
    print("=" * 60)

    if not os.getenv("MIMO_API_KEY"):
        print("\n❌ 未配置 MIMO_API_KEY")
        return

    print(f"\nAPI Key: {os.getenv('MIMO_API_KEY')[:8]}...")
    print(f"API Base: {os.getenv('MIMO_API_BASE')}")

    # 测试TTS
    tts_result = test_tts()

    # 测试ASR
    asr_result = test_asr()

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    print(f"TTS（语音合成）: {'✓ 通过' if tts_result else '✗ 未通过'}")
    if asr_result is None:
        print(f"ASR（语音识别）: ⊘ 跳过（需要测试音频）")
    else:
        print(f"ASR（语音识别）: {'✓ 通过' if asr_result else '✗ 未通过'}")

    print("\n" + "=" * 60)
    print("下一步")
    print("=" * 60)

    if tts_result:
        print("✓ TTS已验证，可以播放生成的音频试听效果")

    if asr_result is None:
        print("⊘ 录制测试音频以验证ASR：")
        print("   pip install pyaudio")
        print("   python tests/record_audio.py")
    elif asr_result:
        print("✓ ASR已验证，录音识别功能正常")

    if tts_result and (asr_result or asr_result is None):
        print("\n🎉 MiMo API验证完成！")
        print("   现在可以开始开发完整链路")


if __name__ == "__main__":
    main()
