#!/usr/bin/env python3
"""
音色管理模块

功能：
1. 加载音色配置
2. 根据情感自动选择音色
3. 生成带情感标签的TTS文本
"""

import json
import os
from typing import Dict, Optional


class VoiceManager:
    def __init__(self, config_path: str = "config/voice_settings.json"):
        """初始化音色管理器"""
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """加载配置文件"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 返回默认配置
            return {
                "default_voice": "冰糖",
                "gender_preference": "female",
                "auto_switch_voice": True,
                "enable_emotion_tags": True,
                "voice_mapping": {
                    "female": {
                        "happy": "冰糖",
                        "sad": "茉莉",
                        "neutral": "茉莉",
                        "surprised": "冰糖"
                    },
                    "male": {
                        "happy": "白桦",
                        "sad": "苏打",
                        "neutral": "苏打",
                        "surprised": "白桦"
                    }
                }
            }

    def select_voice(self, emotion: str, gender_preference: Optional[str] = None) -> str:
        """
        根据情感选择音色

        Args:
            emotion: 情感类型 (happy/sad/neutral/surprised)
            gender_preference: 性别偏好 (female/male)，不传则使用配置默认值

        Returns:
            音色名称
        """
        if not self.config.get("auto_switch_voice", False):
            return self.config.get("default_voice", "冰糖")

        gender = gender_preference or self.config.get("gender_preference", "female")
        voice_map = self.config.get("voice_mapping", {})

        selected_voice = voice_map.get(gender, {}).get(emotion, self.config.get("default_voice", "冰糖"))
        return selected_voice

    def add_emotion_tag(self, text: str, emotion: str) -> str:
        """
        为文本添加情感标签

        Args:
            text: 原始文本
            emotion: 情感类型

        Returns:
            带情感标签的文本
        """
        if not self.config.get("enable_emotion_tags", False):
            return text

        emotion_tags = {
            "happy": "[开心]",
            "sad": "[悲伤]",
            "neutral": "",  # 中性不加标签
            "surprised": "[惊讶]",
            "excited": "[兴奋]"
        }

        tag = emotion_tags.get(emotion, "")
        return f"{tag}{text}" if tag else text

    def get_available_voices(self, gender: str = "chinese_female") -> list:
        """获取可用音色列表"""
        return self.config.get("available_voices", {}).get(gender, [])

    def save_config(self):
        """保存配置"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def update_settings(self, **kwargs):
        """更新设置"""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
        self.save_config()


# 使用示例
if __name__ == "__main__":
    manager = VoiceManager()

    # 测试不同情感的音色选择
    test_emotions = ["happy", "sad", "neutral", "surprised"]

    print("=== 女声音色选择 ===")
    for emotion in test_emotions:
        voice = manager.select_voice(emotion, "female")
        text = manager.add_emotion_tag("你好，今天天气不错！", emotion)
        print(f"{emotion}: {voice} - {text}")

    print("\n=== 男声音色选择 ===")
    for emotion in test_emotions:
        voice = manager.select_voice(emotion, "male")
        text = manager.add_emotion_tag("你好，今天天气不错！", emotion)
        print(f"{emotion}: {voice} - {text}")
