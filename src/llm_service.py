#!/usr/bin/env python3
"""
LLM对话服务

功能：
1. 多轮对话管理
2. 动作指令协议输出
3. 工具调用支持
4. Prompt模板管理
"""

import os
import json
from typing import List, Dict, Optional, Any
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class LLMService:
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
  "action": "动作（必须是以下之一：nod, shake, wave, none）",
  "tool_calls": []  // 如果需要调用工具，填写工具调用信息
}

回复规则：
1. speech要自然口语化，像真人说话一样
2. emotion要准确反映对话的情感氛围
3. action要符合语境（如肯定时点头nod，否定时摇头shake，打招呼时挥手wave）
4. 回复要简洁，一般1-2句话即可
5. 对于简单问题直接回答，不要过度解释

示例：
用户："今天天气怎么样？"
回复：{"speech": "让我帮你查一下", "emotion": "neutral", "action": "nod", "tool_calls": [{"name": "get_weather"}]}

用户："太好了！"
回复：{"speech": "是的，真是个好消息！", "emotion": "happy", "action": "nod"}

用户："我有点难过"
回复：{"speech": "别难过，我陪着你呢", "emotion": "sad", "action": "none"}
"""

    def chat(
        self,
        user_message: str,
        tools: Optional[List[Dict]] = None,
        use_history: bool = True
    ) -> Dict[str, Any]:
        """
        发送消息并获取回复

        Args:
            user_message: 用户消息
            tools: 可用工具列表
            use_history: 是否使用对话历史

        Returns:
            解析后的JSON响应
        """
        # 构建消息列表
        messages = []

        # 添加系统提示
        messages.append({
            "role": "system",
            "content": self.system_prompt
        })

        # 添加历史对话（如果启用）
        if use_history and self.conversation_history:
            messages.extend(self.conversation_history[-10:])  # 只保留最近10轮

        # 添加当前用户消息
        messages.append({
            "role": "user",
            "content": user_message
        })

        # 调用LLM
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "response_format": {"type": "json_object"},
                "temperature": 0.7,
            }

            # 如果有工具，添加工具定义
            if tools:
                kwargs["tools"] = tools

            completion = self.client.chat.completions.create(**kwargs)

            # 解析响应
            response_content = completion.choices[0].message.content
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

        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            return {
                "speech": "抱歉，我有点混乱了",
                "emotion": "neutral",
                "action": "none"
            }
        except Exception as e:
            print(f"LLM调用错误: {e}")
            return {
                "speech": "抱歉，我遇到了一些问题",
                "emotion": "sad",
                "action": "none"
            }

    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []

    def get_history(self) -> List[Dict]:
        """获取对话历史"""
        return self.conversation_history


# 测试代码
if __name__ == "__main__":
    print("=== LLM服务测试 ===\n")

    llm = LLMService()

    # 测试对话
    test_messages = [
        "你好！",
        "今天天气怎么样？",
        "太好了，我很开心！",
        "我有点难过",
        "谢谢你陪我聊天"
    ]

    for msg in test_messages:
        print(f"用户: {msg}")
        response = llm.chat(msg)
        print(f"Aivo: {response['speech']}")
        print(f"  [情感: {response['emotion']}, 动作: {response['action']}]")
        print()
