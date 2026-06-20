#!/usr/bin/env python3
"""
Aivo数字人主程序 V2（支持工具调用）

完整对话链路：录音 → ASR → LLM（工具调用）→ TTS → 播放
"""

import os
import sys

# 添加src目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from asr_service import ASRService
from llm_service_v2 import LLMServiceWithTools
from tts_service import TTSService


class AivoBotV2:
    def __init__(self):
        """初始化Aivo数字人"""
        print("=" * 60)
        print("Aivo 数字人系统初始化中（支持工具调用）...")
        print("=" * 60)

        self.asr = ASRService()
        self.llm = LLMServiceWithTools()
        self.tts = TTSService()

        print("✓ ASR服务已加载")
        print("✓ LLM服务已加载（支持工具：天气、时间、计算器）")
        print("✓ TTS服务已加载")
        print("\n系统就绪！\n")

    def process_text_input(self, text: str) -> dict:
        """
        处理文本输入（无需录音）

        Args:
            text: 用户输入的文本

        Returns:
            完整响应
        """
        print(f"\n{'='*60}")
        print(f"用户: {text}")
        print(f"{'='*60}")

        # 1. LLM生成回复（可能调用工具）
        response = self.llm.chat(text)

        print(f"\n💬 Aivo: {response['speech']}")
        print(f"  [情感: {response['emotion']}, 动作: {response['action']}]")

        # 2. TTS合成语音
        print(f"\n🎵 合成语音...")
        audio_path = self.tts.synthesize(
            text=response['speech'],
            emotion=response['emotion']
        )

        # 3. 播放音频
        print(f"\n🔊 播放中...")
        self.tts.play_audio(audio_path)

        return {
            "user_text": text,
            "response": response,
            "audio_path": audio_path
        }

    def process_voice_input(self, duration: int = 5) -> dict:
        """
        处理语音输入

        Args:
            duration: 录音时长

        Returns:
            完整响应
        """
        # 1. 录音并识别
        print(f"\n{'='*60}")
        print("🎤 语音输入模式")
        print(f"{'='*60}")
        user_text = self.asr.record_and_transcribe(duration=duration)

        print(f"\n用户说: {user_text}")

        # 2. LLM生成回复
        response = self.llm.chat(user_text)

        print(f"\n💬 Aivo: {response['speech']}")
        print(f"  [情感: {response['emotion']}, 动作: {response['action']}]")

        # 3. TTS合成语音
        print(f"\n🎵 合成语音...")
        audio_path = self.tts.synthesize(
            text=response['speech'],
            emotion=response['emotion']
        )

        # 4. 播放音频
        print(f"\n🔊 播放中...")
        self.tts.play_audio(audio_path)

        return {
            "user_text": user_text,
            "response": response,
            "audio_path": audio_path
        }

    def chat_loop_text(self):
        """文本对话循环"""
        print("=" * 60)
        print("Aivo 文本对话模式（支持工具调用）")
        print("=" * 60)
        print("可用工具：")
        print("  - 天气查询：问\"北京天气怎么样？\"")
        print("  - 时间查询：问\"现在几点了？\"")
        print("  - 计算器：问\"帮我算25*4\"")
        print("\n命令：")
        print("  - 'quit' 或 'exit' 退出")
        print("  - 'clear' 清空对话历史")
        print("  - 'history' 查看对话历史\n")

        while True:
            try:
                user_input = input("你: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['quit', 'exit', '退出']:
                    print("\n再见！👋")
                    break

                if user_input.lower() in ['clear', '清空']:
                    self.llm.clear_history()
                    print("✓ 对话历史已清空\n")
                    continue

                if user_input.lower() in ['history', '历史']:
                    history = self.llm.conversation_history
                    if history:
                        print("\n对话历史：")
                        for i, msg in enumerate(history):
                            role = "你" if msg['role'] == 'user' else "Aivo"
                            content = msg['content'][:50] + "..." if len(msg['content']) > 50 else msg['content']
                            print(f"  {i+1}. {role}: {content}")
                    else:
                        print("\n暂无对话历史")
                    print()
                    continue

                self.process_text_input(user_input)
                print()

            except KeyboardInterrupt:
                print("\n\n再见！👋")
                break
            except Exception as e:
                print(f"\n❌ 错误: {e}\n")

    def chat_loop_voice(self, duration: int = 5):
        """语音对话循环"""
        print("=" * 60)
        print("Aivo 语音对话模式（支持工具调用）")
        print("=" * 60)
        print(f"录音时长: {duration}秒")
        print("按回车开始录音，输入 'quit' 退出\n")

        while True:
            try:
                cmd = input("按回车开始录音（或输入命令）: ").strip()

                if cmd.lower() in ['quit', 'exit', '退出']:
                    print("\n再见！👋")
                    break

                if cmd.lower() in ['clear', '清空']:
                    self.llm.clear_history()
                    print("✓ 对话历史已清空\n")
                    continue

                self.process_voice_input(duration=duration)
                print()

            except KeyboardInterrupt:
                print("\n\n再见！👋")
                break
            except Exception as e:
                print(f"\n❌ 错误: {e}\n")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="Aivo数字人系统 V2（支持工具调用）")
    parser.add_argument(
        "--mode",
        choices=["text", "voice"],
        default="text",
        help="对话模式：text(文本) 或 voice(语音)"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=5,
        help="语音模式下的录音时长（秒）"
    )

    args = parser.parse_args()

    # 初始化系统
    bot = AivoBotV2()

    # 启动对话循环
    if args.mode == "text":
        bot.chat_loop_text()
    else:
        bot.chat_loop_voice(duration=args.duration)


if __name__ == "__main__":
    main()
