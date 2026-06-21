#!/usr/bin/env python3
"""
带工具调用的LLM对话服务（升级版）
"""

import os
import json
from typing import List, Dict, Optional, Any
from openai import OpenAI
from dotenv import load_dotenv
from tools import tool_registry

load_dotenv()


class LLMServiceWithTools:
    def __init__(self):
        """初始化LLM服务"""
        self.client = OpenAI(
            api_key=os.getenv("MIMO_API_KEY"),
            base_url=os.getenv("MIMO_API_BASE", "https://token-plan-cn.xiaomimimo.com/v1")
        )
        self.model = "mimo-v2.5-pro"
        self.conversation_history: List[Dict] = []
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """加载系统提示词"""
        return """你是一个友好的数字人助手，名字叫Aivo。

你必须严格按照以下JSON格式回复：
{
  "speech": "你要说的话（自然、口语化、简洁）",
  "emotion": "当前情感（必须是以下之一：happy, sad, neutral, surprised）",
  "action": "动作（必须是以下之一：nod, shake, wave, none）"
}

回复规则：
1. speech要自然口语化，像真人说话一样
2. emotion要准确反映对话的情感氛围
3. action要符合语境（如肯定时点头nod，否定时摇头shake，打招呼时挥手wave）
4. 回复要简洁，一般1-2句话即可
5. 当使用工具后，用自然语言解释工具返回的结果

示例：
用户："今天天气怎么样？"
你会调用get_weather工具，然后根据结果回复：
{"speech": "今天北京天气晴朗，温度25度，很适合出门呢", "emotion": "happy", "action": "nod"}

用户："几点了？"
你会调用get_datetime工具，然后回复：
{"speech": "现在是下午3点25分", "emotion": "neutral", "action": "none"}
"""

    def chat(self, user_message: str, use_tools: bool = True) -> Dict[str, Any]:
        """
        发送消息并获取回复（支持工具调用）

        Args:
            user_message: 用户消息
            use_tools: 是否启用工具调用

        Returns:
            解析后的JSON响应
        """
        # 构建消息列表
        messages = [{"role": "system", "content": self.system_prompt}]

        # 添加历史对话
        if self.conversation_history:
            messages.extend(self.conversation_history[-10:])

        # 添加当前用户消息
        messages.append({"role": "user", "content": user_message})

        # 准备工具定义
        tools = tool_registry.get_all_definitions() if use_tools else None

        try:
            # 第一次调用LLM
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
            }

            if tools:
                kwargs["tools"] = tools

            completion = self.client.chat.completions.create(**kwargs)
            message = completion.choices[0].message

            # 检查是否需要调用工具
            if hasattr(message, 'tool_calls') and message.tool_calls:
                print(f"\n🔧 调用工具中...")

                # 执行工具调用
                tool_results = []
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)

                    print(f"  - {tool_name}({tool_args})")

                    # 执行工具
                    result = tool_registry.execute_tool(tool_name, **tool_args)
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": tool_name,
                        "content": result
                    })

                    print(f"    结果: {result}")

                # 将工具调用和结果加入消息历史
                messages.append({
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        } for tc in message.tool_calls
                    ]
                })

                for tr in tool_results:
                    messages.append(tr)

                # 第二次调用LLM，让它根据工具结果生成回复
                print(f"\n💭 生成最终回复...")
                completion2 = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    response_format={"type": "json_object"},
                    temperature=0.7
                )

                response_content = completion2.choices[0].message.content

            else:
                # 没有工具调用，直接返回
                # 需要重新调用以获取JSON格式
                kwargs["response_format"] = {"type": "json_object"}
                completion2 = self.client.chat.completions.create(**kwargs)
                response_content = completion2.choices[0].message.content

            # 解析响应
            response_data = json.loads(response_content)

            # 验证必需字段
            if not all(key in response_data for key in ['speech', 'emotion', 'action']):
                raise ValueError("响应缺少必需字段")

            # 更新对话历史
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": response_content
            })

            return response_data

        except Exception as e:
            print(f"✗ LLM调用错误: {e}")
            return {
                "speech": "抱歉，我遇到了一些问题",
                "emotion": "sad",
                "action": "none"
            }

    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []

    def add_to_history(self, role: str, content: str):
        """添加消息到对话历史"""
        self.conversation_history.append({
            "role": role,
            "content": content
        })

    def get_history(self) -> List[Dict]:
        """获取对话历史"""
        return self.conversation_history

    def set_history(self, history: List[Dict]):
        """设置对话历史"""
        self.conversation_history = history


# 测试代码
if __name__ == "__main__":
    print("=== 带工具调用的LLM测试 ===\n")

    llm = LLMServiceWithTools()

    test_messages = [
        "你好",
        "北京今天天气怎么样？",
        "现在几点了？",
        "帮我算一下 25 * 4",
        "谢谢你"
    ]

    for msg in test_messages:
        print(f"\n用户: {msg}")
        response = llm.chat(msg)
        print(f"Aivo: {response['speech']}")
        print(f"  [情感: {response['emotion']}, 动作: {response['action']}]")
