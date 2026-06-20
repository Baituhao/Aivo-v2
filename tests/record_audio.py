#!/usr/bin/env python3
"""
录制测试音频

用Mac麦克风录制5秒音频，保存为 tests/test_audio.wav
用于测试MiMo ASR
"""

import pyaudio
import wave

def record_audio(output_path="tests/test_audio.wav", duration=5):
    """录制音频"""

    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000

    print("=" * 60)
    print("录制测试音频")
    print("=" * 60)
    print(f"\n请说一句话（将录制{duration}秒）：")
    print('例如："你好，今天天气怎么样？"')
    print("\n按回车开始...")
    input()

    p = pyaudio.PyAudio()

    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )

    print("\n🎤 录音中...")

    frames = []
    for i in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("✓ 录音完成")

    stream.stop_stream()
    stream.close()
    p.terminate()

    # 保存为WAV文件
    wf = wave.open(output_path, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    print(f"✓ 音频已保存: {output_path}")
    print(f"\n现在可以运行: python tests/test_mimo_complete.py")


if __name__ == "__main__":
    record_audio()
