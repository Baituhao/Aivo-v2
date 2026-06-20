#!/usr/bin/env python3
"""
笔记工具

本地存储和查询笔记
"""

from .base import BaseTool
from typing import Dict
import json
import os
from datetime import datetime


class NoteTool(BaseTool):
    """笔记工具：记录和查询笔记"""

    def __init__(self):
        super().__init__()
        self.notes_file = "output/notes.json"
        os.makedirs(os.path.dirname(self.notes_file), exist_ok=True)
        self._load_notes()

    def _load_notes(self):
        """加载笔记"""
        if os.path.exists(self.notes_file):
            with open(self.notes_file, 'r', encoding='utf-8') as f:
                self.notes = json.load(f)
        else:
            self.notes = []

    def _save_notes(self):
        """保存笔记"""
        with open(self.notes_file, 'w', encoding='utf-8') as f:
            json.dump(self.notes, f, ensure_ascii=False, indent=2)

    @property
    def name(self) -> str:
        return "note"

    @property
    def description(self) -> str:
        return "记录或查询笔记。可以添加新笔记、查看所有笔记、搜索笔记内容。"

    @property
    def parameters(self) -> Dict:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "操作类型",
                    "enum": ["add", "list", "search"]
                },
                "content": {
                    "type": "string",
                    "description": "笔记内容（add时必需）或搜索关键词（search时必需）"
                }
            },
            "required": ["action"]
        }

    def execute(self, action: str, content: str = "", **kwargs) -> str:
        """
        执行笔记操作

        Args:
            action: 操作类型（add/list/search）
            content: 笔记内容或搜索关键词

        Returns:
            操作结果
        """
        try:
            if action == "add":
                # 添加笔记
                if not content:
                    return "错误：请提供笔记内容"

                note = {
                    "id": len(self.notes) + 1,
                    "content": content,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                self.notes.append(note)
                self._save_notes()
                return f"✓ 笔记已保存（编号：{note['id']}）"

            elif action == "list":
                # 列出所有笔记
                if not self.notes:
                    return "暂无笔记"

                result = f"共有{len(self.notes)}条笔记：\n"
                for note in self.notes[-5:]:  # 只显示最近5条
                    result += f"\n[{note['id']}] {note['timestamp']}\n{note['content']}\n"

                if len(self.notes) > 5:
                    result += f"\n（仅显示最近5条，共{len(self.notes)}条）"

                return result

            elif action == "search":
                # 搜索笔记
                if not content:
                    return "错误：请提供搜索关键词"

                matches = [
                    note for note in self.notes
                    if content.lower() in note['content'].lower()
                ]

                if not matches:
                    return f"未找到包含'{content}'的笔记"

                result = f"找到{len(matches)}条相关笔记：\n"
                for note in matches:
                    result += f"\n[{note['id']}] {note['timestamp']}\n{note['content']}\n"

                return result

            else:
                return f"未知操作：{action}"

        except Exception as e:
            return f"笔记操作失败：{str(e)}"


# 测试代码
if __name__ == "__main__":
    tool = NoteTool()

    print("=== 笔记工具测试 ===")

    # 测试1：添加笔记
    result1 = tool.execute(action="add", content="明天要开会")
    print(result1)

    result2 = tool.execute(action="add", content="记得买牛奶")
    print(result2)

    # 测试2：列出笔记
    result3 = tool.execute(action="list")
    print(f"\n{result3}")

    # 测试3：搜索笔记
    result4 = tool.execute(action="search", content="开会")
    print(f"\n{result4}")
