#!/usr/bin/env python3
"""
测试小米MiMo API的工具调用能力

验证项：
1. 基础对话能力
2. Function Calling（工具调用）
3. 结构化JSON输出
4. 流式输出（可选）
"""

import os
import json
import requests
from typing import Dict, Any, List
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

MIMO_API_KEY = os.getenv("MIMO_API_KEY")
MIMO_API_BASE = os.getenv("MIMO_API_BASE", "https://api.mimo.xiaomi.com/v1")


class MiMoAPITester:
    def __init__(self, api_key: str, api_base: str):
        self.api_key = api_key
        self.api_base = api_base
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def test_basic_chat(self) -> bool:
        """测试1：基础对话能力"""
        print("\n=== 测试1：基础对话能力 ===")

        payload = {
            "model": "mimo-chat",  # 根据实际模型名称调整
            "messages": [
                {"role": "user", "content": "你好，请用一句话介绍你自己"}
            ]
        }

        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                print(f"✓ 对话成功")
                print(f"  回复: {result.get('choices', [{}])[0].get('message', {}).get('content', 'N/A')}")
                return True
            else:
                print(f"✗ 请求失败: {response.status_code}")
                print(f"  响应: {response.text}")
                return False

        except Exception as e:
            print(f"✗ 异常: {str(e)}")
            return False

    def test_function_calling(self) -> bool:
        """测试2：Function Calling（工具调用）"""
        print("\n=== 测试2：Function Calling（工具调用）===")

        # 定义一个简单的天气查询工具
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

        payload = {
            "model": "mimo-chat",
            "messages": [
                {"role": "user", "content": "北京今天天气怎么样？"}
            ],
            "tools": tools,
            "tool_choice": "auto"
        }

        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                message = result.get('choices', [{}])[0].get('message', {})

                # 检查是否调用了工具
                if 'tool_calls' in message:
                    print(f"✓ 支持Function Calling")
                    tool_call = message['tool_calls'][0]
                    print(f"  调用工具: {tool_call.get('function', {}).get('name')}")
                    print(f"  参数: {tool_call.get('function', {}).get('arguments')}")
                    return True
                else:
                    print(f"✗ 不支持Function Calling或未触发")
                    print(f"  普通回复: {message.get('content', 'N/A')}")
                    return False
            else:
                print(f"✗ 请求失败: {response.status_code}")
                print(f"  响应: {response.text}")
                return False

        except Exception as e:
            print(f"✗ 异常: {str(e)}")
            return False

    def test_json_output(self) -> bool:
        """测试3：结构化JSON输出"""
        print("\n=== 测试3：结构化JSON输出 ===")

        # 测试是否能按照指定格式输出JSON
        schema = {
            "type": "object",
            "properties": {
                "speech": {"type": "string", "description": "回复文本"},
                "emotion": {"type": "string", "enum": ["happy", "sad", "neutral", "surprised"]},
                "action": {"type": "string", "enum": ["nod", "shake", "wave", "none"]}
            },
            "required": ["speech", "emotion", "action"]
        }

        payload = {
            "model": "mimo-chat",
            "messages": [
                {
                    "role": "system",
                    "content": f"你必须严格按照以下JSON格式回复：{json.dumps(schema, ensure_ascii=False)}"
                },
                {
                    "role": "user",
                    "content": "太好了，明天是晴天！"
                }
            ],
            "response_format": {"type": "json_object"}  # OpenAI格式的JSON mode
        }

        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')

                # 尝试解析JSON
                try:
                    parsed = json.loads(content)
                    if all(key in parsed for key in ['speech', 'emotion', 'action']):
                        print(f"✓ 支持结构化JSON输出")
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
            else:
                print(f"✗ 请求失败: {response.status_code}")
                return False

        except Exception as e:
            print(f"✗ 异常: {str(e)}")
            return False

    def test_streaming(self) -> bool:
        """测试4：流式输出（可选）"""
        print("\n=== 测试4：流式输出（可选）===")

        payload = {
            "model": "mimo-chat",
            "messages": [
                {"role": "user", "content": "请数1到5"}
            ],
            "stream": True
        }

        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=self.headers,
                json=payload,
                stream=True,
                timeout=30
            )

            if response.status_code == 200:
                print(f"✓ 支持流式输出")
                print(f"  流式内容: ", end="", flush=True)

                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            data = line[6:]
                            if data != '[DONE]':
                                try:
                                    chunk = json.loads(data)
                                    content = chunk.get('choices', [{}])[0].get('delta', {}).get('content', '')
                                    print(content, end="", flush=True)
                                except:
                                    pass
                print()
                return True
            else:
                print(f"✗ 不支持流式输出: {response.status_code}")
                return False

        except Exception as e:
            print(f"✗ 异常: {str(e)}")
            return False


def main():
    print("=" * 60)
    print("小米MiMo API 能力验证测试")
    print("=" * 60)

    if not MIMO_API_KEY:
        print("\n❌ 错误：未找到 MIMO_API_KEY")
        print("请先创建 .env 文件并配置API密钥")
        print("参考 .env.example 文件")
        return

    print(f"\nAPI Base: {MIMO_API_BASE}")
    print(f"API Key: {MIMO_API_KEY[:8]}...")

    tester = MiMoAPITester(MIMO_API_KEY, MIMO_API_BASE)

    # 运行所有测试
    results = {
        "基础对话": tester.test_basic_chat(),
        "Function Calling": tester.test_function_calling(),
        "JSON输出": tester.test_json_output(),
        "流式输出": tester.test_streaming()
    }

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "✓ 通过" if passed else "✗ 未通过"
        print(f"{test_name}: {status}")

    # 给出建议
    print("\n" + "=" * 60)
    print("建议")
    print("=" * 60)

    if results["Function Calling"] and results["JSON输出"]:
        print("✓ 小米MiMo API 完全满足项目需求，可以使用！")
    elif results["JSON输出"]:
        print("⚠ MiMo不支持Function Calling，但支持JSON输出")
        print("  建议：可以通过Prompt工程实现工具调用（在JSON中包含tool_call字段）")
    else:
        print("✗ 小米MiMo API 不满足项目核心需求")
        print("  建议：切换到Qwen/DeepSeek/Claude")
        print("  - Qwen（通义千问）：国产，中文好，工具调用稳定")
        print("  - DeepSeek：性价比最高，价格极低")
        print("  - Claude：工具调用最稳定，推理能力顶级")


if __name__ == "__main__":
    main()
