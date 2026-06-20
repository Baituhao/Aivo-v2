#!/usr/bin/env python3
"""
测试工具调用系统
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tools import tool_registry, WeatherTool, DateTimeTool, CalculatorTool


def test_tools():
    """测试所有工具"""
    print("=" * 60)
    print("工具调用系统测试")
    print("=" * 60)

    # 显示已注册的工具
    print(f"\n已注册工具数量: {len(tool_registry.tools)}")
    for tool_name in tool_registry.tools.keys():
        print(f"  - {tool_name}")

    # 测试天气工具
    print("\n" + "=" * 60)
    print("测试1：天气查询")
    print("=" * 60)
    result = tool_registry.execute_tool("get_weather", city="北京")
    print(f"结果: {result}")

    result = tool_registry.execute_tool("get_weather", city="上海")
    print(f"结果: {result}")

    # 测试时间工具
    print("\n" + "=" * 60)
    print("测试2：时间查询")
    print("=" * 60)
    result = tool_registry.execute_tool("get_datetime", format="full")
    print(f"完整时间: {result}")

    result = tool_registry.execute_tool("get_datetime", format="date")
    print(f"仅日期: {result}")

    result = tool_registry.execute_tool("get_datetime", format="time")
    print(f"仅时间: {result}")

    # 测试计算器
    print("\n" + "=" * 60)
    print("测试3：计算器")
    print("=" * 60)
    result = tool_registry.execute_tool("calculate", expression="2+3*4")
    print(f"结果: {result}")

    result = tool_registry.execute_tool("calculate", expression="(100-25)/3")
    print(f"结果: {result}")

    # 测试工具定义导出
    print("\n" + "=" * 60)
    print("测试4：Function Calling格式导出")
    print("=" * 60)
    definitions = tool_registry.get_all_definitions()
    print(f"工具定义数量: {len(definitions)}")
    for defn in definitions:
        print(f"\n工具: {defn['function']['name']}")
        print(f"  描述: {defn['function']['description']}")


if __name__ == "__main__":
    test_tools()
