#!/usr/bin/env python3
"""
维基百科查询工具

查询维基百科知识
"""

from .base import BaseTool
from typing import Dict
import requests


class WikiTool(BaseTool):
    """维基百科查询工具"""

    @property
    def name(self) -> str:
        return "wiki"

    @property
    def description(self) -> str:
        return "查询维基百科，获取知识和概念的详细解释。支持中英文查询。"

    @property
    def parameters(self) -> Dict:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "要查询的词条或概念"
                },
                "language": {
                    "type": "string",
                    "description": "查询语言（zh=中文，en=英文）",
                    "enum": ["zh", "en"]
                }
            },
            "required": ["query"]
        }

    def execute(self, query: str, language: str = "zh", **kwargs) -> str:
        """
        查询维基百科

        Args:
            query: 查询词条
            language: 语言（zh/en）

        Returns:
            查询结果摘要
        """
        try:
            # 选择维基百科API端点
            if language == "zh":
                api_url = "https://zh.wikipedia.org/api/rest_v1/page/summary/"
            else:
                api_url = "https://en.wikipedia.org/api/rest_v1/page/summary/"

            # 调用维基百科API
            response = requests.get(
                f"{api_url}{query}",
                headers={"User-Agent": "Aivo-Bot/1.0"},
                timeout=10
            )

            if response.status_code == 404:
                return f"未找到'{query}'的相关信息"

            response.raise_for_status()
            data = response.json()

            # 提取摘要
            title = data.get("title", query)
            extract = data.get("extract", "无法获取摘要")

            # 限制长度
            if len(extract) > 300:
                extract = extract[:300] + "..."

            result = f"📚 {title}\n\n{extract}"

            # 如果有URL，附上链接
            if "content_urls" in data and "desktop" in data["content_urls"]:
                url = data["content_urls"]["desktop"]["page"]
                result += f"\n\n🔗 详细信息: {url}"

            return result

        except Exception as e:
            return f"维基百科查询失败：{str(e)}"


# 测试代码
if __name__ == "__main__":
    tool = WikiTool()

    print("=== 维基百科工具测试 ===")

    # 测试1：中文查询
    result1 = tool.execute(query="人工智能", language="zh")
    print(result1)

    print("\n" + "="*60 + "\n")

    # 测试2：英文查询
    result2 = tool.execute(query="Machine Learning", language="en")
    print(result2)

    print("\n" + "="*60 + "\n")

    # 测试3：不存在的词条
    result3 = tool.execute(query="这个词条不存在abcxyz123", language="zh")
    print(result3)
