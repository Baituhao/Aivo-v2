#!/usr/bin/env python3
"""
时间日期工具
"""

from datetime import datetime
from .base import BaseTool


class DateTimeTool(BaseTool):
    """日期时间查询工具"""

    @property
    def name(self) -> str:
        return "get_datetime"

    @property
    def description(self) -> str:
        return "获取当前的日期和时间信息"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "format": {
                    "type": "string",
                    "description": "返回格式：date(仅日期)、time(仅时间)、full(完整)",
                    "enum": ["date", "time", "full"]
                }
            },
            "required": []
        }

    def execute(self, format: str = "full", **kwargs) -> str:
        """
        获取日期时间

        Args:
            format: 返回格式

        Returns:
            格式化的日期时间字符串
        """
        now = datetime.now()

        if format == "date":
            return now.strftime("今天是%Y年%m月%d日，星期%w")
        elif format == "time":
            return now.strftime("现在是%H:%M:%S")
        else:  # full
            weekdays = ["一", "二", "三", "四", "五", "六", "日"]
            weekday = weekdays[now.weekday()]
            return now.strftime(f"现在是%Y年%m月%d日，星期{weekday}，%H:%M:%S")


class CalculatorTool(BaseTool):
    """简单计算器工具"""

    @property
    def name(self) -> str:
        return "calculate"

    @property
    def description(self) -> str:
        return "执行简单的数学计算，支持加减乘除"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "数学表达式，例如：2+3*4"
                }
            },
            "required": ["expression"]
        }

    def execute(self, expression: str, **kwargs) -> str:
        """
        计算表达式

        Args:
            expression: 数学表达式

        Returns:
            计算结果
        """
        try:
            # 安全计算（只允许数字和基本运算符）
            allowed_chars = set("0123456789+-*/(). ")
            if not all(c in allowed_chars for c in expression):
                return "错误：表达式包含不允许的字符"

            result = eval(expression)
            return f"{expression} = {result}"

        except Exception as e:
            return f"计算错误: {str(e)}"


# 测试
if __name__ == "__main__":
    dt_tool = DateTimeTool()
    print(dt_tool.execute())
    print(dt_tool.execute(format="date"))
    print(dt_tool.execute(format="time"))

    calc_tool = CalculatorTool()
    print(calc_tool.execute(expression="2+3*4"))
    print(calc_tool.execute(expression="(10+5)/3"))
