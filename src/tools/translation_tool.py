#!/usr/bin/env python3
"""
翻译工具

使用MyMemory翻译API（免费）
"""

from .base import BaseTool
from typing import Dict
import requests


class TranslationTool(BaseTool):
    """翻译工具：中英互译"""

    @property
    def name(self) -> str:
        return "translate"

    @property
    def description(self) -> str:
        return "翻译文本，支持中英互译。可以自动检测语言或指定源语言和目标语言。"

    @property
    def parameters(self) -> Dict:
        return {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "要翻译的文本"
                },
                "target_lang": {
                    "type": "string",
                    "description": "目标语言代码，zh=中文，en=英文，默认自动检测并翻译",
                    "enum": ["zh", "en", "auto"]
                }
            },
            "required": ["text"]
        }

    def execute(self, text: str, target_lang: str = "auto", **kwargs) -> str:
        """
        执行翻译

        Args:
            text: 要翻译的文本
            target_lang: 目标语言（zh/en/auto）

        Returns:
            翻译结果
        """
        try:
            # 自动检测语言
            if target_lang == "auto":
                # 简单判断：包含中文则翻译成英文，否则翻译成中文
                if any('\u4e00' <= char <= '\u9fff' for char in text):
                    source_lang = "zh-CN"
                    target_lang = "en"
                else:
                    source_lang = "en"
                    target_lang = "zh-CN"
            else:
                # 用户指定目标语言
                if target_lang == "zh":
                    source_lang = "en"
                    target_lang = "zh-CN"
                else:
                    source_lang = "zh-CN"
                    target_lang = "en"

            # 调用MyMemory翻译API（免费）
            url = "https://api.mymemory.translated.net/get"
            params = {
                "q": text,
                "langpair": f"{source_lang}|{target_lang}"
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            translated_text = data["responseData"]["translatedText"]

            return f"翻译结果：{translated_text}"

        except Exception as e:
            return f"翻译失败：{str(e)}"


# 测试代码
if __name__ == "__main__":
    tool = TranslationTool()

    print("=== 翻译工具测试 ===")

    # 测试1：中译英
    result1 = tool.execute("你好，世界！")
    print(f"中译英: {result1}")

    # 测试2：英译中
    result2 = tool.execute("Hello, world!")
    print(f"英译中: {result2}")

    # 测试3：指定目标语言
    result3 = tool.execute("人工智能", target_lang="en")
    print(f"指定目标语言: {result3}")
