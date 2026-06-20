#!/usr/bin/env python3
"""
提醒工具

设置和查询提醒事项
"""

from .base import BaseTool
from typing import Dict
import json
import os
from datetime import datetime, timedelta


class ReminderTool(BaseTool):
    """提醒工具：设置提醒事项"""

    def __init__(self):
        super().__init__()
        self.reminders_file = "output/reminders.json"
        os.makedirs(os.path.dirname(self.reminders_file), exist_ok=True)
        self._load_reminders()

    def _load_reminders(self):
        """加载提醒"""
        if os.path.exists(self.reminders_file):
            with open(self.reminders_file, 'r', encoding='utf-8') as f:
                self.reminders = json.load(f)
        else:
            self.reminders = []

    def _save_reminders(self):
        """保存提醒"""
        with open(self.reminders_file, 'w', encoding='utf-8') as f:
            json.dump(self.reminders, f, ensure_ascii=False, indent=2)

    @property
    def name(self) -> str:
        return "reminder"

    @property
    def description(self) -> str:
        return "设置提醒事项。可以添加提醒、查看待办提醒、标记完成。支持相对时间（如'1小时后'、'明天'）。"

    @property
    def parameters(self) -> Dict:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "操作类型",
                    "enum": ["add", "list", "done"]
                },
                "content": {
                    "type": "string",
                    "description": "提醒内容（add时必需）"
                },
                "time": {
                    "type": "string",
                    "description": "提醒时间，支持相对时间如'1小时后'、'明天'、'3天后'，或具体时间如'2024-06-21 10:00'"
                },
                "reminder_id": {
                    "type": "integer",
                    "description": "提醒ID（done时必需）"
                }
            },
            "required": ["action"]
        }

    def _parse_time(self, time_str: str) -> str:
        """解析时间字符串"""
        time_str = time_str.strip()
        now = datetime.now()

        # 相对时间解析
        if "小时后" in time_str or "hour" in time_str.lower():
            hours = int(''.join(filter(str.isdigit, time_str)))
            target = now + timedelta(hours=hours)
        elif "分钟后" in time_str or "minute" in time_str.lower():
            minutes = int(''.join(filter(str.isdigit, time_str)))
            target = now + timedelta(minutes=minutes)
        elif "天后" in time_str or "day" in time_str.lower():
            days = int(''.join(filter(str.isdigit, time_str)))
            target = now + timedelta(days=days)
        elif "明天" in time_str or "tomorrow" in time_str.lower():
            target = now + timedelta(days=1)
        elif "后天" in time_str:
            target = now + timedelta(days=2)
        else:
            # 尝试解析具体时间
            try:
                target = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
            except:
                # 默认1小时后
                target = now + timedelta(hours=1)

        return target.strftime("%Y-%m-%d %H:%M")

    def execute(self, action: str, content: str = "", time: str = "1小时后", reminder_id: int = 0, **kwargs) -> str:
        """
        执行提醒操作

        Args:
            action: 操作类型（add/list/done）
            content: 提醒内容
            time: 提醒时间
            reminder_id: 提醒ID

        Returns:
            操作结果
        """
        try:
            if action == "add":
                # 添加提醒
                if not content:
                    return "错误：请提供提醒内容"

                reminder_time = self._parse_time(time)
                reminder = {
                    "id": len(self.reminders) + 1,
                    "content": content,
                    "time": reminder_time,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "pending"
                }
                self.reminders.append(reminder)
                self._save_reminders()
                return f"✓ 提醒已设置：{content}\n⏰ 时间：{reminder_time}"

            elif action == "list":
                # 列出待办提醒
                pending = [r for r in self.reminders if r['status'] == 'pending']

                if not pending:
                    return "暂无待办提醒"

                result = f"共有{len(pending)}个待办提醒：\n"
                for reminder in pending:
                    result += f"\n[{reminder['id']}] {reminder['time']}\n{reminder['content']}\n"

                return result

            elif action == "done":
                # 标记完成
                if not reminder_id:
                    return "错误：请提供提醒ID"

                for reminder in self.reminders:
                    if reminder['id'] == reminder_id:
                        reminder['status'] = 'done'
                        self._save_reminders()
                        return f"✓ 提醒已完成：{reminder['content']}"

                return f"未找到ID为{reminder_id}的提醒"

            else:
                return f"未知操作：{action}"

        except Exception as e:
            return f"提醒操作失败：{str(e)}"


# 测试代码
if __name__ == "__main__":
    tool = ReminderTool()

    print("=== 提醒工具测试 ===")

    # 测试1：添加提醒
    result1 = tool.execute(action="add", content="开会讨论项目", time="2小时后")
    print(result1)

    result2 = tool.execute(action="add", content="提交报告", time="明天")
    print(f"\n{result2}")

    # 测试2：列出提醒
    result3 = tool.execute(action="list")
    print(f"\n{result3}")

    # 测试3：标记完成
    result4 = tool.execute(action="done", reminder_id=1)
    print(f"\n{result4}")
