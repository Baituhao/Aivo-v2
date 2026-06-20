#!/usr/bin/env python3
"""
天气查询工具

使用免费的wttr.in API
"""

import requests
from .base import BaseTool


class WeatherTool(BaseTool):
    """天气查询工具"""

    @property
    def name(self) -> str:
        return "get_weather"

    @property
    def description(self) -> str:
        return "查询指定城市的实时天气信息"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称，例如：北京、上海、Beijing"
                }
            },
            "required": ["city"]
        }

    def execute(self, city: str, **kwargs) -> str:
        """
        查询天气

        Args:
            city: 城市名称

        Returns:
            天气信息字符串
        """
        try:
            # 使用wttr.in免费API
            url = f"https://wttr.in/{city}?format=%C+%t+%h+%w"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                weather_data = response.text.strip()
                # 格式化输出
                parts = weather_data.split()
                if len(parts) >= 4:
                    condition = parts[0]
                    temperature = parts[1]
                    humidity = parts[2]
                    wind = parts[3]

                    return f"{city}的天气：{condition}，温度{temperature}，湿度{humidity}，风速{wind}"
                else:
                    return f"{city}的天气：{weather_data}"
            else:
                return f"无法获取{city}的天气信息"

        except Exception as e:
            return f"天气查询失败: {str(e)}"


# 使用示例
if __name__ == "__main__":
    tool = WeatherTool()
    print(f"工具名: {tool.name}")
    print(f"描述: {tool.description}")
    print("\n测试查询：")
    print(tool.execute(city="北京"))
    print(tool.execute(city="上海"))
