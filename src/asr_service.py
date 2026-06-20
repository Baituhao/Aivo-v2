#!/usr/bin/env python3
"""
ASR语音识别服务

功能：
1. 录音功能
2. 音频转文本
3. 错误处理和重试
"""

import os
import base64
import wave
import pyaudio
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class ASRService:
    def __init__(self):
        """初始化ASR服务"""
        self.client = OpenAI(
            api_key=os.getenv("MIMO_API_KEY"),
            base_url=os.getenv("MIMO_API_BASE", "https://token-plan-cn.xiaomimimo.com/v1")
        )
        self.output_dir = "output/recordings"
        os.makedirs(self.output_dir, exist_ok=True)

        # 录音参数
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000

    def record_audio(self, duration: int = 5, save_path: Optional[str] = None) -> str:
        """
        录制音频

        Args:
            duration: 录制时长（秒）
            save_path: 保存路径（不指定则自动生成）

        Returns:
            音频文件路径
        """
        print(f"\n🎤 开始录音（{duration}秒）...")

        p = pyaudio.PyAudio()

        # 打开音频流
        stream = p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )

        frames = []

        # 录音
        for i in range(0, int(self.rate / self.chunk * duration)):
            data = stream.read(self.chunk)
            frames.append(data)

        print("✓ 录音完成")

        # 停止和关闭流
        stream.stop_stream()
        stream.close()
        p.terminate()

        # 保存文件
        if not save_path:
            import time
            timestamp = int(time.time() * 1000)
            save_path = os.path.join(self.output_dir, f"recording_{timestamp}.wav")

        wf = wave.open(save_path, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(p.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(frames))
        wf.close()

        print(f"✓ 音频已保存: {save_path}")

        return save_path

    def transcribe(self, audio_path: str, language: str = "zh") -> str:
        """
        音频转文本

        Args:
            audio_path: 音频文件路径
            language: 语言代码（zh/en）

        Returns:
            识别的文本
        """
        print(f"\n📝 识别中...")

        try:
            # 读取音频文件
            with open(audio_path, "rb") as f:
                audio_bytes = f.read()

            # 转为base64
            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

            # 调用ASR API
            completion = self.client.chat.completions.create(
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
                        "language": language
                    }
                }
            )

            transcript = completion.choices[0].message.content
            print(f"✓ 识别结果: {transcript}")

            return transcript

        except Exception as e:
            print(f"✗ ASR识别失败: {e}")
            raise

    def record_and_transcribe(self, duration: int = 5, language: str = "zh") -> str:
        """
        录音并识别（一步完成）

        Args:
            duration: 录制时长（秒）
            language: 语言代码

        Returns:
            识别的文本
        """
        audio_path = self.record_audio(duration)
        transcript = self.transcribe(audio_path, language)
        return transcript


# 测试代码
if __name__ == "__main__":
    print("=== ASR服务测试 ===")

    asr = ASRService()

    print("\n请说一句话（将录制5秒）：")
    print("按回车开始...")
    input()

    try:
        text = asr.record_and_transcribe(duration=5)
        print(f"\n最终识别结果: {text}")
    except Exception as e:
        print(f"\n测试失败: {e}")
