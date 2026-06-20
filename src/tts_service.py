#!/usr/bin/env python3
"""
TTS语音合成服务

功能：
1. 文本转语音
2. 情感标签添加
3. 音色智能选择
4. 音频文件管理
"""

import os
import base64
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv
from voice_manager import VoiceManager

load_dotenv()


class TTSService:
    def __init__(self):
        """初始化TTS服务"""
        self.client = OpenAI(
            api_key=os.getenv("MIMO_API_KEY"),
            base_url=os.getenv("MIMO_API_BASE", "https://token-plan-cn.xiaomimimo.com/v1")
        )
        self.voice_manager = VoiceManager()
        self.output_dir = "output/audio"
        os.makedirs(self.output_dir, exist_ok=True)

    def synthesize(
        self,
        text: str,
        emotion: str = "neutral",
        voice: Optional[str] = None,
        save_path: Optional[str] = None
    ) -> str:
        """
        合成语音

        Args:
            text: 要合成的文本
            emotion: 情感类型
            voice: 指定音色（不指定则自动选择）
            save_path: 保存路径（不指定则自动生成）

        Returns:
            音频文件路径
        """
        # 自动选择音色（如果未指定）
        if not voice:
            voice = self.voice_manager.select_voice(emotion)

        # 添加情感标签
        text_with_emotion = self.voice_manager.add_emotion_tag(text, emotion)

        # 构建用户消息（风格指导）
        style_guide = self._get_style_guide(emotion)

        try:
            # 调用TTS API
            completion = self.client.chat.completions.create(
                model="mimo-v2.5-tts",
                modalities=["text", "audio"],
                audio={"voice": voice, "format": "wav"},
                messages=[
                    {"role": "user", "content": style_guide},
                    {"role": "assistant", "content": text_with_emotion}
                ]
            )

            # 解码音频数据
            audio_base64 = completion.choices[0].message.audio.data
            audio_bytes = base64.b64decode(audio_base64)

            # 保存音频文件
            if not save_path:
                import time
                timestamp = int(time.time() * 1000)
                save_path = os.path.join(self.output_dir, f"tts_{timestamp}.wav")

            with open(save_path, "wb") as f:
                f.write(audio_bytes)

            print(f"✓ TTS生成成功: {save_path}")
            print(f"  音色: {voice}, 情感: {emotion}")

            return save_path

        except Exception as e:
            print(f"✗ TTS生成失败: {e}")
            raise

    def _get_style_guide(self, emotion: str) -> str:
        """根据情感获取风格指导"""
        guides = {
            "happy": "使用明亮活泼、充满能量的语气",
            "sad": "使用温柔平静、体贴关怀的语气",
            "neutral": "使用自然平和、不带情绪的语气",
            "surprised": "使用惊讶、充满好奇的语气"
        }
        return guides.get(emotion, "使用自然的语气")

    def play_audio(self, audio_path: str):
        """播放音频文件"""
        try:
            import platform
            import subprocess

            system = platform.system()

            if system == "Darwin":  # macOS
                subprocess.run(["afplay", audio_path], check=True)
            elif system == "Linux":
                subprocess.run(["aplay", audio_path], check=True)
            elif system == "Windows":
                import winsound
                winsound.PlaySound(audio_path, winsound.SND_FILENAME)

            print(f"✓ 播放完成: {audio_path}")

        except Exception as e:
            print(f"✗ 播放失败: {e}")


# 测试代码
if __name__ == "__main__":
    print("=== TTS服务测试 ===\n")

    tts = TTSService()

    # 测试不同情感
    test_cases = [
        ("你好，很高兴见到你！", "happy"),
        ("别担心，一切都会好起来的", "sad"),
        ("今天是星期三", "neutral"),
        ("哇！真的吗？", "surprised")
    ]

    for text, emotion in test_cases:
        print(f"合成: {text} [{emotion}]")
        audio_path = tts.synthesize(text, emotion)
        print(f"保存: {audio_path}\n")

    print("测试完成！可以到 output/audio/ 目录查看生成的音频文件")
