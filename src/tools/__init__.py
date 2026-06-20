"""
工具包

导入所有可用工具
"""

from .base import BaseTool, ToolRegistry, tool_registry
from .weather import WeatherTool
from .utils import DateTimeTool, CalculatorTool
from .search import SearchTool
from .reminder_tool import ReminderTool
from .news_tool import NewsTool
from .translation_tool import TranslationTool
from .wiki_tool import WikiTool
from .note_tool import NoteTool

# 注册所有工具
tool_registry.register(WeatherTool())
tool_registry.register(DateTimeTool())
tool_registry.register(CalculatorTool())
tool_registry.register(SearchTool())
tool_registry.register(ReminderTool())
tool_registry.register(NewsTool())
tool_registry.register(TranslationTool())
tool_registry.register(WikiTool())
tool_registry.register(NoteTool())

__all__ = [
    'BaseTool',
    'ToolRegistry',
    'tool_registry',
    'WeatherTool',
    'DateTimeTool',
    'CalculatorTool',
    'SearchTool',
    'ReminderTool',
    'NewsTool',
    'TranslationTool',
    'WikiTool',
    'NoteTool'
]
