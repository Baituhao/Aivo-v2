#!/usr/bin/env python3
"""
测试新工具
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tools.reminder_tool import ReminderTool
from tools.news_tool import NewsTool
from tools.translation_tool import TranslationTool
from tools.wiki_tool import WikiTool
from tools.note_tool import NoteTool


def test_all_tools():
    """测试所有新工具"""

    print("=" * 60)
    print("测试新工具")
    print("=" * 60)

    # 1. 提醒工具
    print("\n【1/5】提醒工具")
    print("-" * 60)
    reminder = ReminderTool()
    result = reminder.execute(action="add", content="明天开会", time="1小时后")
    print(result)

    # 2. 翻译工具
    print("\n【2/5】翻译工具")
    print("-" * 60)
    translator = TranslationTool()
    result = translator.execute(text="Hello, world!")
    print(result)

    # 3. 维基百科工具
    print("\n【3/5】维基百科工具")
    print("-" * 60)
    wiki = WikiTool()
    result = wiki.execute(query="人工智能", language="zh")
    print(result)

    # 4. 笔记工具
    print("\n【4/5】笔记工具")
    print("-" * 60)
    note = NoteTool()
    result = note.execute(action="add", content="测试笔记内容")
    print(result)

    # 5. 新闻工具
    print("\n【5/5】新闻工具")
    print("-" * 60)
    news = NewsTool()
    result = news.execute(category="technology")
    print(result)

    print("\n" + "=" * 60)
    print("✓ 所有工具测试完成")
    print("=" * 60)


if __name__ == "__main__":
    test_all_tools()
