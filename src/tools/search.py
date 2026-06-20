#!/usr/bin/env python3
"""
网络搜索工具

使用DuckDuckGo进行网络搜索（免费）
"""

import requests
from .base import BaseTool


class SearchTool(BaseTool):
    """网络搜索工具"""

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return "在互联网上搜索信息，获取最新资讯和知识"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索关键词或问题"
                }
            },
            "required": ["query"]
        }

    def execute(self, query: str, **kwargs) -> str:
        """
        执行搜索

        Args:
            query: 搜索关键词

        Returns:
            搜索结果摘要
        """
        try:
            # 使用DuckDuckGo即时搜索API（免费，无需API key）
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1
            }

            response = requests.get(url, params=params, timeout=5)

            if response.status_code == 200:
                data = response.json()

                # 提取摘要
                abstract = data.get('AbstractText', '')
                if abstract:
                    return f"搜索结果：{abstract}"

                # 如果没有摘要，尝试提取相关主题
                related_topics = data.get('RelatedTopics', [])
                if related_topics:
                    results = []
                    for topic in related_topics[:3]:  # 只取前3个
                        if 'Text' in topic:
                            results.append(topic['Text'])

                    if results:
                        return "搜索结果：\n" + "\n".join(f"- {r}" for r in results)

                return f"未找到关于 '{query}' 的详细信息"

            else:
                return "搜索服务暂时不可用"

        except Exception as e:
            return f"搜索失败: {str(e)}"


# 测试
if __name__ == "__main__":
    tool = SearchTool()
    print(f"工具名: {tool.name}")
    print(f"描述: {tool.description}")
    print("\n测试搜索：")
    print(tool.execute(query="Python编程语言"))
    print()
    print(tool.execute(query="人工智能"))
