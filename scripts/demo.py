#!/usr/bin/env python3
"""
Demo演示脚本

自动运行预设的演示场景
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from llm_service_v2 import LLMServiceWithTools
from tts_service import TTSService
import time


class DemoRunner:
    def __init__(self):
        self.llm = LLMServiceWithTools()
        self.tts = TTSService()

    def run_scenario(self, name: str, conversations: list):
        """运行演示场景"""
        print("=" * 70)
        print(f"场景: {name}")
        print("=" * 70)

        for i, user_msg in enumerate(conversations, 1):
            print(f"\n[{i}] 用户: {user_msg}")

            # LLM生成回复
            response = self.llm.chat(user_msg)

            print(f"    Aivo: {response['speech']}")
            print(f"    [情感: {response['emotion']} | 动作: {response['action']}]")

            # 可选：生成语音
            # audio_path = self.tts.synthesize(response['speech'], response['emotion'])

            time.sleep(0.5)  # 稍微延迟，便于观察

        print("\n" + "=" * 70)

    def run_all_demos(self):
        """运行所有演示场景"""

        # 场景1：日常闲聊
        self.run_scenario(
            "场景1 - 日常闲聊",
            [
                "你好，我是小明",
                "今天天气真好",
                "我有点累了"
            ]
        )

        input("\n按回车继续下一个场景...")
        self.llm.clear_history()

        # 场景2：工具调用
        self.run_scenario(
            "场景2 - 工具调用（天气查询）",
            [
                "北京今天天气怎么样？",
                "那上海呢？"
            ]
        )

        input("\n按回车继续下一个场景...")
        self.llm.clear_history()

        # 场景3：计算器
        self.run_scenario(
            "场景3 - 计算器工具",
            [
                "帮我算一下，如果我每月存5000元，一年能存多少？",
                "那如果存两年呢？"
            ]
        )

        input("\n按回车继续下一个场景...")
        self.llm.clear_history()

        # 场景4：时间查询
        self.run_scenario(
            "场景4 - 时间查询",
            [
                "现在几点了？",
                "今天星期几？"
            ]
        )

        input("\n按回车继续下一个场景...")
        self.llm.clear_history()

        # 场景5：情感交互
        self.run_scenario(
            "场景5 - 情感识别",
            [
                "太棒了！我考试考了第一名！",
                "可是我有点紧张后面的比赛",
                "谢谢你的鼓励"
            ]
        )

        input("\n按回车继续下一个场景...")
        self.llm.clear_history()

        # 场景6：多步骤规划
        self.run_scenario(
            "场景6 - 多步骤任务规划",
            [
                "帮我安排一下明天的活动"
            ]
        )

        print("\n" + "=" * 70)
        print("✓ 所有演示场景完成！")
        print("=" * 70)


def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║          Aivo Demo 演示脚本                              ║
║                                                          ║
║  自动运行预设的演示场景，展示系统核心能力                  ║
╚══════════════════════════════════════════════════════════╝
    """)

    runner = DemoRunner()

    print("\n选择运行模式：")
    print("1. 运行所有场景（自动）")
    print("2. 单独选择场景")
    print("3. 自定义对话")

    choice = input("\n请选择 (1/2/3): ").strip()

    if choice == "1":
        runner.run_all_demos()
    elif choice == "2":
        print("\n可用场景：")
        print("1. 日常闲聊")
        print("2. 工具调用")
        print("3. 计算器")
        print("4. 时间查询")
        print("5. 情感交互")
        print("6. 多步骤规划")

        scenario = input("\n选择场景 (1-6): ").strip()
        # 根据选择运行对应场景
        print("功能开发中...")
    elif choice == "3":
        print("\n进入自定义对话模式（输入 quit 退出）：")
        while True:
            user_input = input("\n你: ").strip()
            if user_input.lower() in ['quit', 'exit']:
                break

            response = runner.llm.chat(user_input)
            print(f"Aivo: {response['speech']}")
            print(f"  [情感: {response['emotion']} | 动作: {response['action']}]")


if __name__ == "__main__":
    main()
