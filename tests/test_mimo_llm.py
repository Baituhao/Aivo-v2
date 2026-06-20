#!/usr/bin/env python3
"""
测试MiMo LLM（mimo-v2.5-pro）的对话和工具调用能力
"""

import os
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()

client = OpenAI(
    api_key=os.getenv("MIMO_API_KEY"),
    base_url=os.getenv("MIMO_API_BASE", "https://token-plan-cn.xiaomimimo.com/v1")
)


def test_basic_chat():
    """测试基础对话"""
    print("\n=== 测试1：基础对话 ===")

    try:
        completion = client.chat.completions.create(
            model="mimo-v2.5-pro",
            messages=[
                {"role": "user", "content": "你好，请用一句话介绍你自己"}
            ]
        )

        response = completion.choices[0].message.content
        print(f"✓ 对话成功")
        print(f"  回复: {response}")
        return True

    except Exception as e:
        print(f"✗ 对话失败: {str(e)}")
        return False


def test_function_calling():
    """测试Function Calling"""
    print("\n=== 测试2：Function Calling ===")

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "查询指定城市的天气",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "城市名称，例如：北京、上海"
                        }
                    },
                    "required": ["city"]
                }
            }
        }
    ]

    try:
        completion = client.chat.completions.create(
            model="mimo-v2.5-pro",
            messages=[
                {"role": "user", "content": "北京今天天气怎么样？"}
            ],
            tools=tools
        )

        message = completion.choices[0].message

        if hasattr(message, 'tool_calls') and message.tool_calls:
            print(f"✓ 支持Function Calling")
            tool_call = message.tool_calls[0]
            print(f"  调用工具: {tool_call.function.name}")
            print(f"  参数: {tool_call.function.arguments}")
            return True
        else:
            print(f"✗ 不支持或未触发Function Calling")
            print(f"  普通回复: {message.content}")
            return False

    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        return False


def test_json_output():
    """测试结构化JSON输出（动作指令协议）"""
    print("\n=== 测试3：动作指令协议 ===")

    try:
        completion = client.chat.completions.create(
            model="mimo-v2.5-pro",
            messages=[
                {
                    "role": "system",
                    "content": """你是一个数字人助手。你必须严格按照以下JSON格式回复：
{
  "speech": "你要说的话",
  "emotion": "当前情感（happy/sad/neutral/surprised之一）",
  "action": "动作（nod/shake/wave/none之一）"
}

示例：
- 用户说"太好了"，你应该回复：{"speech": "是的，真是个好消息！", "emotion": "happy", "action": "nod"}
- 用户说"真遗憾"，你应该回复：{"speech": "别灰心，会有转机的", "emotion": "sad", "action": "none"}
"""
                },
                {
                    "role": "user",
                    "content": "太好了，明天是晴天！"
                }
            ],
            response_format={"type": "json_object"}
        )

        content = completion.choices[0].message.content

        try:
            parsed = json.loads(content)
            if all(key in parsed for key in ['speech', 'emotion', 'action']):
                print(f"✓ 支持动作指令协议")
                print(f"  输出: {json.dumps(parsed, ensure_ascii=False, indent=2)}")
                return True
            else:
                print(f"✗ JSON格式不完整")
                print(f"  输出: {content}")
                return False
        except json.JSONDecodeError:
            print(f"✗ 无法解析为JSON")
            print(f"  输出: {content}")
            return False

    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        return False


def main():
    print("=" * 60)
    print("MiMo LLM (mimo-v2.5-pro) 能力测试")
    print("=" * 60)

    if not os.getenv("MIMO_API_KEY"):
        print("\n❌ 未配置 MIMO_API_KEY")
        return

    results = {
        "基础对话": test_basic_chat(),
        "Function Calling": test_function_calling(),
        "动作指令协议": test_json_output()
    }

    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "✓ 通过" if passed else "✗ 未通过"
        print(f"{test_name}: {status}")

    print("\n" + "=" * 60)
    print("最终方案")
    print("=" * 60)

    if all(results.values()):
        print("✓ MiMo完全满足需求！")
        print("\n完整技术栈（全MiMo）：")
        print("  ASR: MiMo")
        print("  LLM: MiMo mimo-v2.5-pro")
        print("  TTS: MiMo")
        print("  部署: Mac本地（0显存）")
        print("\n💡 建议：先跑通 录音→ASR→LLM→TTS→播放 完整链路")
        print("   数字人可用静态图片+表情切换，快速验证智能体能力")
    else:
        print("⚠️  MiMo部分能力不支持")
        if not results["Function Calling"]:
            print("  - 工具调用不支持，需在JSON中自定义tool_call字段")
        if not results["动作指令协议"]:
            print("  - JSON输出不稳定，需调整Prompt")


if __name__ == "__main__":
    main()
