#!/usr/bin/env python3
"""
测试Qwen API的工具调用能力

Qwen（通义千问）作为对话大脑，验证：
1. 基础对话
2. Function Calling
3. 结构化JSON输出
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

QWEN_API_KEY = os.getenv("QWEN_API_KEY")
QWEN_API_BASE = os.getenv("QWEN_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")


class QwenAPITester:
    def __init__(self, api_key: str, api_base: str):
        self.api_key = api_key
        self.api_base = api_base
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def test_basic_chat(self) -> bool:
        """测试基础对话"""
        print("\n=== 测试1：基础对话 ===")

        payload = {
            "model": "qwen-plus",  # 或 qwen-turbo, qwen-max
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
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                print(f"✓ 对话成功")
                print(f"  回复: {content}")
                return True
            else:
                print(f"✗ 请求失败: {response.status_code}")
                print(f"  响应: {response.text}")
                return False

        except Exception as e:
            print(f"✗ 异常: {str(e)}")
            return False

    def test_function_calling(self) -> bool:
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
                                "description": "城市名称"
                            }
                        },
                        "required": ["city"]
                    }
                }
            }
        ]

        payload = {
            "model": "qwen-plus",
            "messages": [
                {"role": "user", "content": "北京今天天气怎么样？"}
            ],
            "tools": tools
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

                if 'tool_calls' in message:
                    print(f"✓ 支持Function Calling")
                    tool_call = message['tool_calls'][0]
                    print(f"  调用工具: {tool_call.get('function', {}).get('name')}")
                    print(f"  参数: {tool_call.get('function', {}).get('arguments')}")
                    return True
                else:
                    print(f"✗ 未触发Function Calling")
                    return False
            else:
                print(f"✗ 请求失败: {response.status_code}")
                return False

        except Exception as e:
            print(f"✗ 异常: {str(e)}")
            return False

    def test_json_output(self) -> bool:
        """测试结构化JSON输出"""
        print("\n=== 测试3：结构化JSON输出 ===")

        payload = {
            "model": "qwen-plus",
            "messages": [
                {
                    "role": "system",
                    "content": """你必须严格按照以下JSON格式回复，不要有任何其他内容：
{
  "speech": "回复文本",
  "emotion": "happy/sad/neutral/surprised之一",
  "action": "nod/shake/wave/none之一"
}"""
                },
                {
                    "role": "user",
                    "content": "太好了，明天是晴天！"
                }
            ],
            "response_format": {"type": "json_object"}
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

                try:
                    parsed = json.loads(content)
                    if all(key in parsed for key in ['speech', 'emotion', 'action']):
                        print(f"✓ 支持结构化JSON输出")
                        print(f"  输出: {json.dumps(parsed, ensure_ascii=False, indent=2)}")
                        return True
                    else:
                        print(f"✗ JSON格式不完整")
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


def main():
    print("=" * 60)
    print("Qwen（通义千问）API 能力验证")
    print("=" * 60)

    if not QWEN_API_KEY:
        print("\n❌ 未配置 QWEN_API_KEY")
        print("\n获取方式：")
        print("1. 访问 https://dashscope.aliyun.com/")
        print("2. 注册/登录阿里云账号")
        print("3. 开通DashScope服务（有免费额度）")
        print("4. 获取API Key")
        return

    print(f"\nAPI Base: {QWEN_API_BASE}")
    print(f"API Key: {QWEN_API_KEY[:8]}...")

    tester = QwenAPITester(QWEN_API_KEY, QWEN_API_BASE)

    results = {
        "基础对话": tester.test_basic_chat(),
        "Function Calling": tester.test_function_calling(),
        "JSON输出": tester.test_json_output()
    }

    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "✓ 通过" if passed else "✗ 未通过"
        print(f"{test_name}: {status}")

    if all(results.values()):
        print("\n✓ Qwen完全满足项目需求，可以作为对话大脑！")
    else:
        print("\n⚠️  部分测试未通过，请检查API配置")


if __name__ == "__main__":
    main()
