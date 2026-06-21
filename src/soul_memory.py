#!/usr/bin/env python3
"""
Soul Memory & Skill 管理系统
- 人格记忆：存储用户偏好、习惯、背景信息
- 技能系统：存储特定领域的知识和能力
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class SoulMemory:
    """灵魂记忆管理器"""

    def __init__(self, memory_dir: Path):
        self.memory_dir = memory_dir
        self.memory_dir.mkdir(exist_ok=True)

        # 记忆文件路径
        self.personality_file = self.memory_dir / "personality.json"
        self.user_profile_file = self.memory_dir / "user_profile.json"
        self.skills_file = self.memory_dir / "skills.json"
        self.preferences_file = self.memory_dir / "preferences.json"

        # 加载所有记忆
        self.personality = self._load_json(self.personality_file, self._default_personality())
        self.user_profile = self._load_json(self.user_profile_file, self._default_user_profile())
        self.skills = self._load_json(self.skills_file, self._default_skills())
        self.preferences = self._load_json(self.preferences_file, self._default_preferences())

    def _load_json(self, file_path: Path, default: dict) -> dict:
        """加载JSON文件"""
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载文件失败 {file_path}: {e}")
        return default

    def _save_json(self, file_path: Path, data: dict):
        """保存JSON文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存文件失败 {file_path}: {e}")

    def _default_personality(self) -> dict:
        """默认人格设定"""
        return {
            "name": "Aivo",
            "role": "AI数字人助手",
            "traits": [
                "友好热情",
                "专业可靠",
                "善解人意",
                "积极向上"
            ],
            "speaking_style": "温暖亲切，乐于助人",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def _default_user_profile(self) -> dict:
        """默认用户画像"""
        return {
            "name": "",
            "preferences": [],
            "interests": [],
            "habits": [],
            "background": "",
            "interaction_history": {
                "first_interaction": None,
                "total_interactions": 0,
                "favorite_topics": []
            },
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def _default_skills(self) -> dict:
        """默认技能列表"""
        return {
            "knowledge_domains": [
                {"name": "通用对话", "level": "expert", "enabled": True},
                {"name": "天气查询", "level": "expert", "enabled": True},
                {"name": "信息搜索", "level": "expert", "enabled": True},
                {"name": "文本翻译", "level": "expert", "enabled": True},
                {"name": "数学计算", "level": "expert", "enabled": True}
            ],
            "custom_skills": [],
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def _default_preferences(self) -> dict:
        """默认偏好设置"""
        return {
            "language": "中文",
            "voice": "冰糖",
            "response_style": "详细",
            "emoji_usage": "适中",
            "humor_level": "适中",
            "formality": "友好",
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    # ==================== 人格管理 ====================

    def update_personality(self, **kwargs):
        """更新人格设定"""
        self.personality.update(kwargs)
        self.personality["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._save_json(self.personality_file, self.personality)

    def get_personality(self) -> dict:
        """获取人格设定"""
        return self.personality

    # ==================== 用户画像 ====================

    def update_user_profile(self, **kwargs):
        """更新用户画像"""
        self.user_profile.update(kwargs)
        self.user_profile["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._save_json(self.user_profile_file, self.user_profile)

    def add_user_interest(self, interest: str):
        """添加用户兴趣"""
        if interest not in self.user_profile["interests"]:
            self.user_profile["interests"].append(interest)
            self.update_user_profile()

    def add_user_habit(self, habit: str):
        """添加用户习惯"""
        if habit not in self.user_profile["habits"]:
            self.user_profile["habits"].append(habit)
            self.update_user_profile()

    def get_user_profile(self) -> dict:
        """获取用户画像"""
        return self.user_profile

    # ==================== 技能管理 ====================

    def add_skill(self, name: str, level: str = "beginner", enabled: bool = True):
        """添加技能"""
        skill = {"name": name, "level": level, "enabled": enabled}
        self.skills["custom_skills"].append(skill)
        self.skills["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._save_json(self.skills_file, self.skills)

    def remove_skill(self, name: str):
        """移除技能"""
        self.skills["custom_skills"] = [
            s for s in self.skills["custom_skills"] if s["name"] != name
        ]
        self.skills["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._save_json(self.skills_file, self.skills)

    def toggle_skill(self, name: str, enabled: bool):
        """切换技能状态"""
        for skill in self.skills["knowledge_domains"] + self.skills["custom_skills"]:
            if skill["name"] == name:
                skill["enabled"] = enabled
        self.skills["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._save_json(self.skills_file, self.skills)

    def get_skills(self) -> dict:
        """获取所有技能"""
        return self.skills

    def get_enabled_skills(self) -> List[str]:
        """获取已启用的技能"""
        enabled = []
        for skill in self.skills["knowledge_domains"] + self.skills["custom_skills"]:
            if skill.get("enabled", True):
                enabled.append(skill["name"])
        return enabled

    # ==================== 偏好设置 ====================

    def update_preferences(self, **kwargs):
        """更新偏好设置"""
        self.preferences.update(kwargs)
        self.preferences["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._save_json(self.preferences_file, self.preferences)

    def get_preferences(self) -> dict:
        """获取偏好设置"""
        return self.preferences

    # ==================== 综合信息 ====================

    def get_summary(self) -> str:
        """获取记忆摘要"""
        summary = f"""
📊 Soul Memory 摘要

🎭 人格设定:
  - 名称: {self.personality['name']}
  - 角色: {self.personality['role']}
  - 特质: {', '.join(self.personality['traits'])}

👤 用户画像:
  - 兴趣: {', '.join(self.user_profile['interests']) if self.user_profile['interests'] else '未记录'}
  - 习惯: {', '.join(self.user_profile['habits']) if self.user_profile['habits'] else '未记录'}
  - 互动次数: {self.user_profile['interaction_history']['total_interactions']}

🛠️ 技能状态:
  - 知识领域: {len(self.skills['knowledge_domains'])}个
  - 自定义技能: {len(self.skills['custom_skills'])}个
  - 已启用: {len(self.get_enabled_skills())}个

⚙️ 偏好设置:
  - 语言: {self.preferences['language']}
  - 音色: {self.preferences['voice']}
  - 回复风格: {self.preferences['response_style']}
        """
        return summary.strip()

    def export_all(self, export_path: Path):
        """导出所有记忆"""
        export_data = {
            "personality": self.personality,
            "user_profile": self.user_profile,
            "skills": self.skills,
            "preferences": self.preferences,
            "exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

    def import_all(self, import_path: Path):
        """导入所有记忆"""
        with open(import_path, 'r', encoding='utf-8') as f:
            import_data = json.load(f)

        if "personality" in import_data:
            self.personality = import_data["personality"]
            self._save_json(self.personality_file, self.personality)

        if "user_profile" in import_data:
            self.user_profile = import_data["user_profile"]
            self._save_json(self.user_profile_file, self.user_profile)

        if "skills" in import_data:
            self.skills = import_data["skills"]
            self._save_json(self.skills_file, self.skills)

        if "preferences" in import_data:
            self.preferences = import_data["preferences"]
            self._save_json(self.preferences_file, self.preferences)
