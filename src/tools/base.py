#!/usr/bin/env python3
"""
工具基类

所有工具都继承此基类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseTool(ABC):
    """工具基类"""

    @property
    @abstractmethod
    def name(self) -> str:
        """工具名称"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """工具描述"""
        pass

    @property
    @abstractmethod
    def parameters(self) -> Dict:
        """工具参数定义（JSON Schema格式）"""
        pass

    @abstractmethod
    def execute(self, **kwargs) -> str:
        """
        执行工具

        Returns:
            执行结果（字符串）
        """
        pass

    def to_function_definition(self) -> Dict:
        """转换为OpenAI Function Calling格式"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }


class ToolRegistry:
    """工具注册表"""

    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        """注册工具"""
        self.tools[tool.name] = tool
        print(f"✓ 工具已注册: {tool.name}")

    def get_tool(self, name: str) -> BaseTool:
        """获取工具"""
        return self.tools.get(name)

    def get_all_definitions(self) -> List[Dict]:
        """获取所有工具的Function定义"""
        return [tool.to_function_definition() for tool in self.tools.values()]

    def execute_tool(self, name: str, **kwargs) -> str:
        """执行工具"""
        tool = self.get_tool(name)
        if not tool:
            return f"错误：工具 '{name}' 不存在"

        try:
            result = tool.execute(**kwargs)
            return result
        except Exception as e:
            return f"工具执行错误: {str(e)}"


# 全局工具注册表
tool_registry = ToolRegistry()
