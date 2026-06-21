#!/usr/bin/env python3
"""
Aivo Web界面 V6 - 优化版
- Live2D via iframe（绕过Gradio沙箱）
- 气泡内嵌音频
- 简化的录音功能
"""

import os
import sys
import base64
import gradio as gr
from pathlib import Path
import time
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from llm_service_v2 import LLMServiceWithTools
from tts_service import TTSService
from voice_manager import VoiceManager
from asr_service import ASRService
from soul_memory import SoulMemory

# live2d.html的绝对路径
STATIC_DIR = Path(__file__).parent / "static"
LIVE2D_HTML = STATIC_DIR / "live2d_pixi.html"  # 有 Cubism 4 Core 了，再试一次

# 会话保存目录
SESSIONS_DIR = Path(__file__).parent.parent / "sessions"
SESSIONS_DIR.mkdir(exist_ok=True)

# Soul Memory 目录
MEMORY_DIR = Path(__file__).parent.parent / "memory"
MEMORY_DIR.mkdir(exist_ok=True)


class AivoWebUIV6:
    def __init__(self):
        self.llm = LLMServiceWithTools()
        self.tts = TTSService()
        self.voice_manager = VoiceManager()
        self.asr = ASRService()
        self.soul_memory = SoulMemory(MEMORY_DIR)  # 初始化灵魂记忆系统
        self.current_voice = "冰糖"
        self.current_emotion = "neutral"  # 保存当前情感
        self.session_start_time = time.time()
        self.response_times = []  # 记录每次响应时长
        self.current_session_id = None  # 当前会话ID
        self.stats = {
            "conversation_count": 0,
            "tool_calls": 0,
            "emotion_changes": 0,
            "last_emotion": "neutral",
            "total_words": 0,  # 总字数
            "avg_response_length": 0,  # 平均回复长度
            "most_used_tool": "无",  # 最常用工具
            "tool_usage": {},  # 工具使用次数统计
            "emotion_distribution": {  # 情感分布
                "happy": 0,
                "sad": 0,
                "neutral": 0,
                "angry": 0,
                "surprised": 0
            },
            "longest_conversation": 0,  # 最长连续对话
            "total_audio_duration": 0,  # 总音频时长（秒）
        }
        self.conversation_history = []  # 完整对话历史（用于导出和搜索）
        self._load_or_create_session()  # 自动加载或创建会话

    def _load_or_create_session(self):
        """加载最近的会话或创建新会话"""
        session_files = sorted(SESSIONS_DIR.glob("session_*.json"), key=lambda x: x.stat().st_mtime, reverse=True)

        if session_files:
            # 加载最近的会话
            latest_session = session_files[0]
            try:
                with open(latest_session, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)

                self.current_session_id = session_data.get('session_id')
                self.session_start_time = session_data.get('session_start_time', time.time())
                self.response_times = session_data.get('response_times', [])
                self.stats = session_data.get('stats', self.stats)
                self.conversation_history = session_data.get('conversation_history', [])

                print(f"✅ 已加载会话: {self.current_session_id}")
                print(f"   对话数: {len(self.conversation_history)}")
            except Exception as e:
                print(f"⚠️ 加载会话失败: {e}，创建新会话")
                self._create_new_session()
        else:
            self._create_new_session()

    def _create_new_session(self):
        """创建新会话"""
        self.current_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_start_time = time.time()
        self.response_times = []
        self.stats = {
            "conversation_count": 0,
            "tool_calls": 0,
            "emotion_changes": 0,
            "last_emotion": "neutral",
            "total_words": 0,
            "avg_response_length": 0,
            "most_used_tool": "无",
            "tool_usage": {},
            "emotion_distribution": {
                "happy": 0,
                "sad": 0,
                "neutral": 0,
                "angry": 0,
                "surprised": 0
            },
            "longest_conversation": 0,
            "total_audio_duration": 0,
        }
        self.conversation_history = []
        self._save_session()
        print(f"🆕 已创建新会话: {self.current_session_id}")

    def _save_session(self):
        """保存当前会话到文件"""
        if not self.current_session_id:
            return

        session_file = SESSIONS_DIR / f"session_{self.current_session_id}.json"
        session_data = {
            "session_id": self.current_session_id,
            "created_at": datetime.fromtimestamp(self.session_start_time).strftime("%Y-%m-%d %H:%M:%S"),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "session_start_time": self.session_start_time,
            "response_times": self.response_times,
            "stats": self.stats,
            "conversation_history": self.conversation_history
        }

        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存会话失败: {e}")

    def _get_sessions_list(self):
        """获取所有会话列表"""
        session_files = sorted(SESSIONS_DIR.glob("session_*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
        sessions = []

        for session_file in session_files:
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)

                    # 获取第一条用户消息
                    first_message = "空会话"
                    if session_data.get('conversation_history'):
                        first_conv = session_data['conversation_history'][0]
                        first_message = first_conv.get('user', '空会话')
                        # 限制长度，避免过长
                        if len(first_message) > 30:
                            first_message = first_message[:30] + "..."

                    sessions.append({
                        "id": session_data.get('session_id'),
                        "created_at": session_data.get('created_at'),
                        "last_updated": session_data.get('last_updated'),
                        "conversation_count": len(session_data.get('conversation_history', [])),
                        "first_message": first_message
                    })
            except Exception as e:
                print(f"⚠️ 读取会话文件失败 {session_file}: {e}")

        return sessions

    def _get_initial_session_choices(self):
        """获取初始会话选择列表"""
        sessions = self._get_sessions_list()
        choices = []
        for s in sessions:
            # 格式：💬 "第一条消息..." (5条对话) - 2025-06-21 14:30 [ID:xxx]
            choice = f"💬 \"{s['first_message']}\" ({s['conversation_count']}条) - {s['last_updated']} [ID:{s['id']}]"
            choices.append(choice)
        return choices

    def load_session(self, session_id: str):
        """加载指定会话"""
        session_file = SESSIONS_DIR / f"session_{session_id}.json"

        if not session_file.exists():
            return None, self._format_stats(), "❌ 会话不存在", None

        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)

            # 更新当前会话信息
            self.current_session_id = session_data.get('session_id')
            self.session_start_time = session_data.get('session_start_time', time.time())
            self.response_times = session_data.get('response_times', [])
            self.stats = session_data.get('stats', self.stats)
            self.conversation_history = session_data.get('conversation_history', [])

            # 🔧 关键修复：恢复 LLM 的对话历史记忆
            self.llm.clear_history()  # 先清空当前历史

            # 重建 LLM 历史记忆
            llm_history = []
            for conv in self.conversation_history:
                # 用户消息
                llm_history.append({
                    "role": "user",
                    "content": conv['user']
                })
                # 助手消息（需要重建 JSON 格式）
                assistant_response = {
                    "speech": conv['assistant'],
                    "emotion": conv.get('emotion', 'neutral'),
                    "action": "none"
                }
                llm_history.append({
                    "role": "assistant",
                    "content": json.dumps(assistant_response, ensure_ascii=False)
                })

            # 设置 LLM 历史
            self.llm.set_history(llm_history)

            # 重建对话历史显示（包含音频气泡）
            history = []
            for conv in self.conversation_history:
                history.append({"role": "user", "content": conv['user']})
                # 注意：加载的历史对话不包含音频，只显示文本
                history.append({"role": "assistant", "content": conv['assistant']})

            # 获取当前会话的显示文本
            sessions = self._get_sessions_list()
            current_display = None
            for s in sessions:
                if s['id'] == session_id:
                    current_display = f"💬 \"{s['first_message']}\" ({s['conversation_count']}条) - {s['last_updated']} [ID:{s['id']}]"
                    break

            print(f"✅ 已加载会话: {session_id}，包含 {len(self.conversation_history)} 轮对话")
            print(f"   LLM 历史记忆已恢复: {len(llm_history)} 条消息")
            return history, self._format_stats(), f"✅ 已加载会话: {session_id}，包含 {len(self.conversation_history)} 轮对话", current_display
        except Exception as e:
            print(f"❌ 加载会话失败: {e}")
            import traceback
            traceback.print_exc()
            return None, self._format_stats(), f"❌ 加载失败: {str(e)}", None

    def _audio_to_base64(self, audio_path: str) -> str:
        """将音频文件转为base64"""
        if not audio_path or not os.path.exists(audio_path):
            return ""
        try:
            with open(audio_path, "rb") as f:
                data = base64.b64encode(f.read()).decode()
            return f"data:audio/wav;base64,{data}"
        except Exception as e:
            print(f"音频编码失败: {e}")
            return ""

    def _make_bubble(self, text: str, audio_path: str) -> str:
        """生成带内嵌音频的消息HTML"""
        audio_b64 = self._audio_to_base64(audio_path)
        audio_html = ""
        if audio_b64:
            # 生成唯一ID
            import time
            audio_id = f"audio_{int(time.time() * 1000)}"
            print(f"[服务端] 生成音频bubble，ID: {audio_id}")
            audio_html = f"""
            <audio id="{audio_id}" controls autoplay
                style="display:block;width:100%;height:32px;margin-top:8px;
                       border-radius:16px;accent-color:#667eea;"
                src="{audio_b64}"
                onplay="console.log('[Audio] 播放 {audio_id}');var iframes=document.querySelectorAll('iframe');console.log('[Audio] 找到iframe数量:',iframes.length);var rootIframes=window.top.document.querySelectorAll('iframe');console.log('[Audio] 顶层iframe数量:',rootIframes.length);try{{rootIframes.forEach(f=>f.contentWindow.postMessage('speaking','*'));console.log('[Audio] 已发送消息')}}catch(e){{console.log('[Audio] 错误:',e)}}"
                onended="console.log('[Audio] 结束 {audio_id}');try{{window.top.document.querySelectorAll('iframe').forEach(f=>f.contentWindow.postMessage('idle','*'))}}catch(e){{}}">
            </audio>"""
        return f"<div style='line-height:1.6;padding:4px 0;'>{text}{audio_html}</div>"

    def chat(self, message: str, history: list, voice_choice: str):
        """处理文本消息"""
        if not message.strip():
            return history, self._format_stats()

        print(f"\n[服务端] ===== 开始处理消息 =====")
        print(f"[服务端] 用户消息: {message}")
        print(f"[服务端] 当前音色: {voice_choice}")

        self.current_voice = voice_choice
        start_time = time.time()

        try:
            # LLM生成回复
            response = self.llm.chat(message)
            print(f"[服务端] LLM回复: {response['speech'][:50]}...")

            # TTS合成语音
            audio_path = self.tts.synthesize(
                text=response['speech'],
                emotion=response['emotion'],
                voice=self.current_voice
            )
            print(f"[服务端] TTS生成音频: {audio_path}")

            # 计算响应时长
            response_time = time.time() - start_time
            self.response_times.append(response_time)

            # 更新历史
            if history is None:
                history = []

            history.append({"role": "user", "content": message})

            bubble_html = self._make_bubble(response['speech'], audio_path)
            print(f"[服务端] 生成bubble HTML，长度: {len(bubble_html)}")

            history.append({
                "role": "assistant",
                "content": bubble_html
            })

            # 保存到完整对话历史
            self.conversation_history.append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "user": message,
                "assistant": response['speech'],
                "emotion": response['emotion'],
                "response_time": round(response_time, 2)
            })

            # 更新统计
            self.stats['conversation_count'] += 1
            self.stats['total_words'] += len(response['speech'])

            # 更新情感分布
            emotion = response['emotion']
            if emotion in self.stats['emotion_distribution']:
                self.stats['emotion_distribution'][emotion] += 1

            if emotion != self.stats['last_emotion']:
                self.stats['emotion_changes'] += 1
                self.stats['last_emotion'] = emotion

            # 更新最长连续对话
            if self.stats['conversation_count'] > self.stats['longest_conversation']:
                self.stats['longest_conversation'] = self.stats['conversation_count']

            # 保存当前情感
            self.current_emotion = emotion
            print(f"[服务端] 当前情感: {self.current_emotion}")

            # 自动保存会话
            self._save_session()

            print(f"[服务端] ===== 消息处理完成 =====\n")
            return history, self._format_stats()

        except Exception as e:
            print(f"聊天错误: {e}")
            if history is None:
                history = []
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": f"❌ 错误: {str(e)}"})
            return history, self._format_stats()

    def process_voice(self, audio_file, history: list, voice_choice: str):
        """处理语音输入"""
        if audio_file is None:
            return history, self._format_stats(), ""

        try:
            # ASR转文字
            transcript = self.asr.transcribe(audio_file)

            # 调用chat处理
            new_history, stats = self.chat(transcript, history, voice_choice)

            return new_history, stats, f"✅ 识别结果: {transcript}"

        except Exception as e:
            print(f"语音识别错误: {e}")
            if history is None:
                history = []
            history.append({"role": "assistant", "content": f"❌ 语音识别失败: {str(e)}"})
            return history, self._format_stats(), f"❌ {str(e)}"

    def _format_memory_summary(self) -> str:
        """格式化记忆摘要"""
        personality = self.soul_memory.personality
        user = self.soul_memory.user_profile
        skills = self.soul_memory.skills
        prefs = self.soul_memory.preferences

        enabled_skills = len(self.soul_memory.get_enabled_skills())

        return f"""
        <div style="background:linear-gradient(135deg,#f5f7fa,#c3cfe2);padding:14px;border-radius:12px;">
            <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:8px;">
                <div style="background:white;padding:10px;border-radius:8px;box-shadow:0 2px 6px rgba(0,0,0,0.06);">
                    <div style="font-size:1.2em;margin-bottom:4px;">🎭</div>
                    <div style="font-size:0.85em;font-weight:700;color:#4338ca;">{personality['name']}</div>
                    <div style="font-size:0.7em;color:#9ca3af;">{personality['role']}</div>
                </div>
                <div style="background:white;padding:10px;border-radius:8px;box-shadow:0 2px 6px rgba(0,0,0,0.06);">
                    <div style="font-size:1.2em;margin-bottom:4px;">👤</div>
                    <div style="font-size:0.85em;font-weight:700;color:#4338ca;">用户画像</div>
                    <div style="font-size:0.7em;color:#9ca3af;">{len(user['interests'])}个兴趣</div>
                </div>
                <div style="background:white;padding:10px;border-radius:8px;box-shadow:0 2px 6px rgba(0,0,0,0.06);">
                    <div style="font-size:1.2em;margin-bottom:4px;">🛠️</div>
                    <div style="font-size:0.85em;font-weight:700;color:#4338ca;">技能系统</div>
                    <div style="font-size:0.7em;color:#9ca3af;">{enabled_skills}个已启用</div>
                </div>
                <div style="background:white;padding:10px;border-radius:8px;box-shadow:0 2px 6px rgba(0,0,0,0.06);">
                    <div style="font-size:1.2em;margin-bottom:4px;">⚙️</div>
                    <div style="font-size:0.85em;font-weight:700;color:#4338ca;">偏好设置</div>
                    <div style="font-size:0.7em;color:#9ca3af;">{prefs['language']} | {prefs['response_style']}</div>
                </div>
            </div>
        </div>
        """

    def _format_skills_display(self) -> str:
        """格式化技能显示"""
        skills = self.soul_memory.get_skills()
        html = """
        <div style="max-height:300px;overflow-y:auto;">
            <div style="font-size:0.9em;font-weight:700;color:#4338ca;margin-bottom:8px;">
                📚 知识领域
            </div>
        """

        for skill in skills["knowledge_domains"]:
            status = "✅" if skill.get("enabled", True) else "❌"
            level_badge = {
                "beginner": "🟢 初级",
                "intermediate": "🟡 中级",
                "expert": "🔴 专家"
            }.get(skill["level"], "⚪ 未知")

            html += f"""
            <div style="background:white;padding:8px;margin-bottom:6px;border-radius:8px;
                box-shadow:0 2px 4px rgba(0,0,0,0.06);display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <span style="font-weight:600;color:#1f2937;">{status} {skill['name']}</span>
                    <span style="margin-left:8px;font-size:0.8em;color:#6b7280;">{level_badge}</span>
                </div>
            </div>
            """

        if skills["custom_skills"]:
            html += """
            <div style="font-size:0.9em;font-weight:700;color:#4338ca;margin:16px 0 8px 0;">
                ⭐ 自定义技能
            </div>
            """
            for skill in skills["custom_skills"]:
                status = "✅" if skill.get("enabled", True) else "❌"
                level_badge = {
                    "beginner": "🟢 初级",
                    "intermediate": "🟡 中级",
                    "expert": "🔴 专家"
                }.get(skill["level"], "⚪ 未知")

                html += f"""
                <div style="background:white;padding:8px;margin-bottom:6px;border-radius:8px;
                    box-shadow:0 2px 4px rgba(0,0,0,0.06);display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <span style="font-weight:600;color:#1f2937;">{status} {skill['name']}</span>
                        <span style="margin-left:8px;font-size:0.8em;color:#6b7280;">{level_badge}</span>
                    </div>
                </div>
                """

        html += "</div>"
        return html

    def update_personality_memory(self, name, role, traits, style):
        """更新人格记忆"""
        try:
            # 支持多种分隔符：英文逗号、中文逗号、顿号
            traits_list = [t.strip() for t in traits.replace("，", ",").replace("、", ",").split(",") if t.strip()]
            self.soul_memory.update_personality(
                name=name,
                role=role,
                traits=traits_list,
                speaking_style=style
            )
            return self._format_memory_summary(), f"✅ 人格设定已保存（{len(traits_list)}个特质）"
        except Exception as e:
            return self._format_memory_summary(), f"❌ 保存失败: {str(e)}"

    def update_user_memory(self, name, interests, habits, background):
        """更新用户记忆"""
        try:
            # 支持多种分隔符：英文逗号、中文逗号、顿号
            interests_list = [i.strip() for i in interests.replace("，", ",").replace("、", ",").split(",") if i.strip()]
            habits_list = [h.strip() for h in habits.replace("，", ",").replace("、", ",").split(",") if h.strip()]
            self.soul_memory.update_user_profile(
                name=name,
                interests=interests_list,
                habits=habits_list,
                background=background
            )
            return self._format_memory_summary(), f"✅ 用户画像已保存（{len(interests_list)}个兴趣，{len(habits_list)}个习惯）"
        except Exception as e:
            return self._format_memory_summary(), f"❌ 保存失败: {str(e)}"

    def add_skill_to_memory(self, skill_name, skill_level):
        """添加技能到记忆"""
        if not skill_name.strip():
            return self._format_skills_display(), "❌ 请输入技能名称"
        try:
            self.soul_memory.add_skill(skill_name.strip(), skill_level)
            return self._format_skills_display(), f"✅ 已添加技能: {skill_name}"
        except Exception as e:
            return self._format_skills_display(), f"❌ 添加失败: {str(e)}"

    def update_preferences_memory(self, language, response_style, emoji, formality):
        """更新偏好设置"""
        try:
            self.soul_memory.update_preferences(
                language=language,
                response_style=response_style,
                emoji_usage=emoji,
                formality=formality
            )
            return self._format_memory_summary(), "✅ 偏好设置已保存"
        except Exception as e:
            return self._format_memory_summary(), f"❌ 保存失败: {str(e)}"

    def export_memory(self):
        """导出记忆"""
        try:
            export_path = MEMORY_DIR / f"soul_memory_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            self.soul_memory.export_all(export_path)
            return f"✅ 记忆已导出到: {export_path}"
        except Exception as e:
            return f"❌ 导出失败: {str(e)}"

    def _format_stats(self) -> str:
        """格式化统计信息"""
        # 找出最常见的情感
        emotion_dist = self.stats['emotion_distribution']
        most_emotion = max(emotion_dist.items(), key=lambda x: x[1])[0] if any(emotion_dist.values()) else "neutral"
        emotion_emoji = {
            "happy": "😊", "sad": "😢", "neutral": "😐", "angry": "😠", "surprised": "😲"
        }

        # 计算平均响应时间
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0

        # 计算会话时长
        session_duration = int(time.time() - self.session_start_time)
        hours = session_duration // 3600
        minutes = (session_duration % 3600) // 60
        seconds = session_duration % 60
        duration_str = f"{hours}h {minutes}m {seconds}s" if hours > 0 else f"{minutes}m {seconds}s"

        # 情感分布条形图
        total_emotions = sum(emotion_dist.values()) or 1
        emotion_bars = ""
        for emotion, count in emotion_dist.items():
            percentage = (count / total_emotions) * 100
            emoji = emotion_emoji[emotion]
            if percentage > 0:
                emotion_bars += f"""
                <div style="margin:4px 0;">
                    <div style="display:flex;align-items:center;gap:6px;">
                        <span style="font-size:1.2em;">{emoji}</span>
                        <div style="flex:1;background:#e5e7eb;border-radius:8px;height:20px;overflow:hidden;">
                            <div style="width:{percentage}%;height:100%;background:linear-gradient(90deg,#667eea,#764ba2);
                                transition:width 0.3s ease;"></div>
                        </div>
                        <span style="font-size:0.8em;color:#6b7280;min-width:40px;">{count}次</span>
                    </div>
                </div>"""

        return f"""
        <div style="background:linear-gradient(135deg,#f5f7fa,#c3cfe2);padding:16px;border-radius:16px;margin-bottom:16px;">
            <div style="text-align:center;font-size:1.3em;font-weight:800;color:#4338ca;margin-bottom:14px;">
                📊 实时统计面板
            </div>

            <!-- 主要统计卡片 -->
            <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-bottom:14px;">
                <div style="background:linear-gradient(135deg,#667eea,#764ba2);padding:12px;
                    border-radius:12px;text-align:center;color:white;
                    box-shadow:0 4px 15px rgba(102,126,234,0.4);position:relative;overflow:hidden;">
                    <div style="position:absolute;top:-20px;right:-20px;width:60px;height:60px;
                        background:rgba(255,255,255,0.1);border-radius:50%;"></div>
                    <div style="font-size:1.5em;margin-bottom:2px;">💬</div>
                    <div style="font-size:2em;font-weight:900;margin:4px 0;position:relative;z-index:1;">
                        {self.stats['conversation_count']}</div>
                    <div style="font-size:0.75em;opacity:0.95;font-weight:600;">对话轮次</div>
                </div>
                <div style="background:linear-gradient(135deg,#f093fb,#f5576c);padding:12px;
                    border-radius:12px;text-align:center;color:white;
                    box-shadow:0 4px 15px rgba(240,147,251,0.4);position:relative;overflow:hidden;">
                    <div style="position:absolute;top:-20px;right:-20px;width:60px;height:60px;
                        background:rgba(255,255,255,0.1);border-radius:50%;"></div>
                    <div style="font-size:1.5em;margin-bottom:2px;">⚡</div>
                    <div style="font-size:2em;font-weight:900;margin:4px 0;position:relative;z-index:1;">
                        {avg_response_time:.1f}s</div>
                    <div style="font-size:0.75em;opacity:0.95;font-weight:600;">平均响应</div>
                </div>
                <div style="background:linear-gradient(135deg,#4facfe,#00f2fe);padding:12px;
                    border-radius:12px;text-align:center;color:white;
                    box-shadow:0 4px 15px rgba(79,172,254,0.4);position:relative;overflow:hidden;">
                    <div style="position:absolute;top:-20px;right:-20px;width:60px;height:60px;
                        background:rgba(255,255,255,0.1);border-radius:50%;"></div>
                    <div style="font-size:1.5em;margin-bottom:2px;">{emotion_emoji[most_emotion]}</div>
                    <div style="font-size:2em;font-weight:900;margin:4px 0;position:relative;z-index:1;">
                        {self.stats['emotion_changes']}</div>
                    <div style="font-size:0.75em;opacity:0.95;font-weight:600;">情感切换</div>
                </div>
                <div style="background:linear-gradient(135deg,#fa709a,#fee140);padding:12px;
                    border-radius:12px;text-align:center;color:white;
                    box-shadow:0 4px 15px rgba(250,112,154,0.4);position:relative;overflow:hidden;">
                    <div style="position:absolute;top:-20px;right:-20px;width:60px;height:60px;
                        background:rgba(255,255,255,0.1);border-radius:50%;"></div>
                    <div style="font-size:1.5em;margin-bottom:2px;">📝</div>
                    <div style="font-size:2em;font-weight:900;margin:4px 0;position:relative;z-index:1;">
                        {self.stats['total_words']}</div>
                    <div style="font-size:0.75em;opacity:0.95;font-weight:600;">总字数</div>
                </div>
            </div>

            <!-- 情感分布图 -->
            <div style="background:white;padding:12px;border-radius:12px;margin-bottom:10px;
                box-shadow:0 2px 8px rgba(0,0,0,0.08);">
                <div style="font-size:0.9em;font-weight:700;color:#4338ca;margin-bottom:8px;text-align:center;">
                    🎭 情感分布
                </div>
                {emotion_bars if emotion_bars else '<div style="text-align:center;color:#9ca3af;font-size:0.85em;">暂无数据</div>'}
            </div>

            <!-- 会话信息 -->
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
                <div style="background:white;padding:10px;border-radius:10px;text-align:center;
                    box-shadow:0 2px 6px rgba(0,0,0,0.06);">
                    <div style="font-size:1.2em;margin-bottom:4px;">⏱️</div>
                    <div style="font-size:0.9em;font-weight:700;color:#4338ca;">{duration_str}</div>
                    <div style="font-size:0.7em;color:#9ca3af;">会话时长</div>
                </div>
                <div style="background:white;padding:10px;border-radius:10px;text-align:center;
                    box-shadow:0 2px 6px rgba(0,0,0,0.06);">
                    <div style="font-size:1.2em;margin-bottom:4px;">🔧</div>
                    <div style="font-size:0.9em;font-weight:700;color:#4338ca;">{self.stats['tool_calls']}</div>
                    <div style="font-size:0.7em;color:#9ca3af;">工具调用</div>
                </div>
            </div>
        </div>"""

    def new_session(self):
        """新建会话（保留统计数据）"""
        self.llm.clear_history()

        # 先保存当前会话
        self._save_session()

        # 创建新会话
        self._create_new_session()

        return [], self._format_stats()

    def clear_history(self):
        """清空对话历史和统计数据"""
        self.llm.clear_history()

        # 保存当前会话后创建新会话
        self._save_session()

        self.session_start_time = time.time()
        self.response_times = []
        self.stats = {
            "conversation_count": 0,
            "tool_calls": 0,
            "emotion_changes": 0,
            "last_emotion": "neutral",
            "total_words": 0,
            "avg_response_length": 0,
            "most_used_tool": "无",
            "tool_usage": {},
            "emotion_distribution": {
                "happy": 0,
                "sad": 0,
                "neutral": 0,
                "angry": 0,
                "surprised": 0
            },
            "longest_conversation": 0,
            "total_audio_duration": 0,
        }
        self.conversation_history = []

        # 创建新会话
        self._create_new_session()

        return [], self._format_stats()

    def export_history(self):
        """导出对话历史为JSON"""
        if not self.conversation_history:
            return "<div style='text-align:center;color:#9ca3af;padding:20px;'>❌ 没有可导出的历史</div>"

        export_data = {
            "export_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "session_id": self.current_session_id,
            "total_conversations": len(self.conversation_history),
            "stats": self.stats,
            "conversations": self.conversation_history
        }

        filename = f"aivo_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = Path("/tmp") / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

        return f"<div style='text-align:center;color:#10b981;padding:20px;'>✅ 已导出到: {filepath}</div>"

    def search_history(self, keyword: str):
        """搜索所有会话的对话历史"""
        if not keyword.strip():
            return "请输入搜索关键词"

        results = []
        session_files = sorted(SESSIONS_DIR.glob("session_*.json"), key=lambda x: x.stat().st_mtime, reverse=True)

        for session_file in session_files:
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)

                session_id = session_data.get('session_id', 'unknown')
                last_updated = session_data.get('last_updated', '')
                conversation_history = session_data.get('conversation_history', [])

                for i, conv in enumerate(conversation_history):
                    if keyword.lower() in conv.get('user', '').lower() or keyword.lower() in conv.get('assistant', '').lower():
                        results.append(f"""
                        <div style="background:white;padding:12px;border-radius:10px;margin:8px 0;
                            box-shadow:0 2px 8px rgba(0,0,0,0.08);border-left:4px solid #667eea;">
                            <div style="font-size:0.75em;color:#9ca3af;margin-bottom:6px;">
                                📁 会话 {session_id} | 💬 对话 #{i+1} | {conv.get('timestamp', '')} | {conv.get('emotion', 'neutral')}
                            </div>
                            <div style="margin-bottom:8px;">
                                <span style="font-weight:700;color:#4338ca;">用户：</span>
                                <span style="color:#1f2937;">{conv.get('user', '')}</span>
                            </div>
                            <div>
                                <span style="font-weight:700;color:#7c3aed;">Aivo：</span>
                                <span style="color:#4b5563;">{conv.get('assistant', '')}</span>
                            </div>
                        </div>
                        """)
            except Exception as e:
                print(f"⚠️ 搜索会话 {session_file} 失败: {e}")

        if not results:
            return f"<div style='text-align:center;color:#9ca3af;padding:20px;'>未找到包含 '{keyword}' 的对话</div>"

        return f"""
        <div style="max-height:400px;overflow-y:auto;padding:4px;">
            <div style="text-align:center;font-weight:700;color:#4338ca;margin-bottom:12px;">
                🔍 找到 {len(results)} 条相关对话
            </div>
            {''.join(results)}
        </div>
        """

    def _get_live2d_html(self) -> str:
        """使用iframe srcdoc嵌入Live2D"""
        # 读取 Cubism 4 Core
        cubism4_core_path = STATIC_DIR / "live2dcubismcore.min.js"
        with open(cubism4_core_path, 'r', encoding='utf-8') as f:
            cubism4_core_content = f.read()

        # 读取 pixi-live2d-display 库
        pixi_lib_path = STATIC_DIR / "pixi-live2d-display.min.js"
        with open(pixi_lib_path, 'r', encoding='utf-8') as f:
            pixi_lib_content = f.read()

        # 读取 HTML 文件
        with open(LIVE2D_HTML, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # 替换本地脚本引用为内联脚本
        html_content = html_content.replace(
            '<script src="/file=/Users/kk/Aivo-v2/src/static/live2dcubismcore.min.js"></script>',
            f'<script>{cubism4_core_content}</script>'
        ).replace(
            '<script src="/file=/Users/kk/Aivo-v2/src/static/pixi-live2d-display.min.js"></script>',
            f'<script>{pixi_lib_content}</script>'
        )

        print(f"[服务端] Live2D HTML 长度: {len(html_content)} 字符")

        # 使用srcdoc直接嵌入
        return f"""
        <div style="width:100%;height:460px;border-radius:20px;overflow:hidden;
            box-shadow:0 10px 35px rgba(102,126,234,0.25);
            background:linear-gradient(135deg,#e0e7ff,#f3e8ff);
            border:3px solid #c7d2fe;position:relative;">
            <iframe srcdoc='{html_content.replace("'", "&#39;")}'
                style="width:100%;height:100%;border:none;"
                sandbox="allow-scripts allow-same-origin"
                allow="autoplay">
            </iframe>
            <div style="position:absolute;top:12px;right:12px;
                background:rgba(255,255,255,0.9);padding:6px 12px;
                border-radius:20px;font-size:0.75em;font-weight:600;
                color:#5b21b6;box-shadow:0 2px 8px rgba(0,0,0,0.1);
                backdrop-filter:blur(10px);">
                🎀 Live2D
            </div>
        </div>
        <div style="text-align:center;color:#6b7280;font-size:0.85em;
            margin-top:10px;padding:8px;background:#f9fafb;
            border-radius:8px;font-weight:500;">
            💡 点击Live2D可切换模型<br>
            <span style="font-size:0.9em;color:#9ca3af;">shizuku → hijiki → tororo</span>
        </div>"""

    def build_interface(self):
        """构建Gradio界面"""

        self.custom_css = """
        .gradio-container {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            max-width: 1400px !important;
        }
        /* 移除高度限制，允许正常滚动 */
        body {
            overflow-y: auto !important;
        }
        /* Chatbot样式优化 */
        .chatbot {
            border-radius: 16px !important;
            border: 2px solid #e5e7eb !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
        }
        /* 按钮悬停效果 */
        button {
            transition: all 0.2s ease !important;
        }
        button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 12px rgba(102,126,234,0.3) !important;
        }
        /* 输入框优化 */
        textarea, input {
            border-radius: 12px !important;
            border: 2px solid #e5e7eb !important;
            transition: border-color 0.2s ease !important;
        }
        textarea:focus, input:focus {
            border-color: #667eea !important;
            box-shadow: 0 0 0 3px rgba(102,126,234,0.1) !important;
        }
        /* 滚动条美化 */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #f1f5f9;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #667eea, #764ba2);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #5568d3, #6a3f8f);
        }
        /* 动画效果 */
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        @keyframes glow {
            0%, 100% { box-shadow: 0 0 5px rgba(102,126,234,0.5); }
            50% { box-shadow: 0 0 20px rgba(102,126,234,0.8); }
        }
        .float-animation {
            animation: float 3s ease-in-out infinite;
        }
        .pulse-animation {
            animation: pulse 2s ease-in-out infinite;
        }
        .glow-animation {
            animation: glow 2s ease-in-out infinite;
        }
        /* 渐变文字 */
        .gradient-text {
            background: linear-gradient(135deg, #667eea, #764ba2, #f093fb);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        /* 卡片悬停效果 */
        .hover-card {
            transition: all 0.3s ease;
        }
        .hover-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }
        /* 渐变边框 */
        .gradient-border {
            border: 2px solid transparent;
            background-clip: padding-box;
            position: relative;
        }
        .gradient-border::before {
            content: '';
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            background: linear-gradient(135deg, #667eea, #764ba2, #f093fb);
            border-radius: inherit;
            z-index: -1;
        }
        """

        with gr.Blocks(title="Aivo V6 - 智能数字人系统") as interface:

            # ============================================
            # 顶部横幅 - 项目主题展示
            # ============================================
            gr.HTML("""
            <div style="text-align:center;padding:50px 30px;margin-bottom:30px;
                background:linear-gradient(135deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%);
                border-radius:24px;box-shadow:0 15px 50px rgba(0,0,0,0.4);
                position:relative;overflow:hidden;">
                <!-- 背景装饰 -->
                <div style="position:absolute;top:-50%;right:-10%;width:400px;height:400px;
                    background:radial-gradient(circle,rgba(102,126,234,0.3),transparent);
                    border-radius:50%;"></div>
                <div style="position:absolute;bottom:-40%;left:-5%;width:350px;height:350px;
                    background:radial-gradient(circle,rgba(118,75,162,0.2),transparent);
                    border-radius:50%;"></div>
                <div style="position:absolute;top:20%;left:10%;width:200px;height:200px;
                    background:radial-gradient(circle,rgba(240,147,251,0.15),transparent);
                    border-radius:50%;"></div>

                <div style="position:relative;z-index:1;">
                    <!-- Logo 和标题 -->
                    <div style="font-size:4em;font-weight:900;color:white;
                        text-shadow:4px 4px 12px rgba(0,0,0,0.5);
                        letter-spacing:-2px;margin-bottom:15px;">
                        <span style="background:linear-gradient(135deg,#667eea,#764ba2,#f093fb);
                            -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                            🎀 Aivo
                        </span>
                        <span style="color:white;margin-left:10px;">数字人 V6</span>
                    </div>

                    <!-- 副标题 -->
                    <div style="color:rgba(255,255,255,0.9);margin-top:15px;
                        font-size:1.3em;font-weight:500;letter-spacing:1px;">
                        基于 MiMo API 的智能数字人系统
                    </div>

                    <!-- 技术栈标签 -->
                    <div style="margin-top:25px;display:flex;gap:15px;justify-content:center;flex-wrap:wrap;">
                        <div style="padding:10px 24px;background:linear-gradient(135deg,rgba(102,126,234,0.8),rgba(118,75,162,0.8));
                            border-radius:25px;backdrop-filter:blur(10px);
                            box-shadow:0 6px 20px rgba(0,0,0,0.3);
                            border:1px solid rgba(255,255,255,0.2);">
                            <span style="color:white;font-size:0.95em;font-weight:600;">
                                🎀 Live2D 数字人
                            </span>
                        </div>
                        <div style="padding:10px 24px;background:linear-gradient(135deg,rgba(240,147,251,0.8),rgba(245,87,108,0.8));
                            border-radius:25px;backdrop-filter:blur(10px);
                            box-shadow:0 6px 20px rgba(0,0,0,0.3);
                            border:1px solid rgba(255,255,255,0.2);">
                            <span style="color:white;font-size:0.95em;font-weight:600;">
                                🎵 气泡语音
                            </span>
                        </div>
                        <div style="padding:10px 24px;background:linear-gradient(135deg,rgba(79,172,254,0.8),rgba(0,242,254,0.8));
                            border-radius:25px;backdrop-filter:blur(10px);
                            box-shadow:0 6px 20px rgba(0,0,0,0.3);
                            border:1px solid rgba(255,255,255,0.2);">
                            <span style="color:white;font-size:0.95em;font-weight:600;">
                                🛠️ 10+ 工具
                            </span>
                        </div>
                        <div style="padding:10px 24px;background:linear-gradient(135deg,rgba(250,112,154,0.8),rgba(254,225,64,0.8));
                            border-radius:25px;backdrop-filter:blur(10px);
                            box-shadow:0 6px 20px rgba(0,0,0,0.3);
                            border:1px solid rgba(255,255,255,0.2);">
                            <span style="color:white;font-size:0.95em;font-weight:600;">
                                🎤 8 种音色
                            </span>
                        </div>
                        <div style="padding:10px 24px;background:linear-gradient(135deg,rgba(67,56,202,0.8),rgba(139,92,246,0.8));
                            border-radius:25px;backdrop-filter:blur(10px);
                            box-shadow:0 6px 20px rgba(0,0,0,0.3);
                            border:1px solid rgba(255,255,255,0.2);">
                            <span style="color:white;font-size:0.95em;font-weight:600;">
                                🧠 Soul Memory
                            </span>
                        </div>
                    </div>

                    <!-- 系统状态指示 -->
                    <div style="margin-top:20px;display:flex;gap:20px;justify-content:center;flex-wrap:wrap;">
                        <div style="display:flex;align-items:center;gap:8px;">
                            <div style="width:10px;height:10px;background:#10b981;border-radius:50%;
                                box-shadow:0 0 10px rgba(16,185,129,0.8);"></div>
                            <span style="color:rgba(255,255,255,0.8);font-size:0.85em;">系统运行中</span>
                        </div>
                        <div style="display:flex;align-items:center;gap:8px;">
                            <div style="width:10px;height:10px;background:#3b82f6;border-radius:50%;
                                box-shadow:0 0 10px rgba(59,130,246,0.8);"></div>
                            <span style="color:rgba(255,255,255,0.8);font-size:0.85em;">MiMo API 已连接</span>
                        </div>
                        <div style="display:flex;align-items:center;gap:8px;">
                            <div style="width:10px;height:10px;background:#8b5cf6;border-radius:50%;
                                box-shadow:0 0 10px rgba(139,92,246,0.8);"></div>
                            <span style="color:rgba(255,255,255,0.8);font-size:0.85em;">Live2D 已就绪</span>
                        </div>
                    </div>

                    <!-- GitHub 链接 -->
                    <div style="margin-top:20px;">
                        <a href="https://github.com/Baituhao/Aivo-v2" target="_blank"
                            style="display:inline-block;padding:10px 24px;
                            background:linear-gradient(135deg,rgba(255,255,255,0.15),rgba(255,255,255,0.05));
                            border-radius:25px;color:white;text-decoration:none;font-size:0.95em;
                            border:1px solid rgba(255,255,255,0.3);
                            backdrop-filter:blur(10px);
                            transition:all 0.3s ease;">
                            ⭐ GitHub 仓库
                        </a>
                    </div>
                </div>
            </div>
            """)

            # ============================================
            # 技术架构展示
            # ============================================
            gr.HTML("""
            <div style="background:linear-gradient(135deg,#f8fafc,#e2e8f0);
                padding:30px;border-radius:20px;margin-bottom:25px;
                border:1px solid #e2e8f0;">
                <div style="text-align:center;margin-bottom:25px;">
                    <div style="font-size:1.8em;font-weight:800;color:#1e293b;margin-bottom:8px;">
                        🏗️ 系统架构
                    </div>
                    <div style="color:#64748b;font-size:0.95em;">
                        分层架构设计 · 模块化组件 · 数据流驱动
                    </div>
                </div>

                <!-- 架构图 - 双路径数据流 -->
                <div style="background:white;padding:25px;border-radius:16px;
                    box-shadow:0 4px 20px rgba(0,0,0,0.08);margin-bottom:20px;">
                    <div style="font-weight:700;color:#4338ca;margin-bottom:20px;font-size:1.1em;">
                        📊 数据流架构
                    </div>

                    <!-- 文本输入路径 -->
                    <div style="margin-bottom:20px;padding:15px;background:linear-gradient(135deg,#f0f9ff,#e0f2fe);
                        border-radius:12px;border-left:4px solid #3b82f6;">
                        <div style="font-weight:600;color:#1e40af;margin-bottom:10px;font-size:0.9em;">
                            📝 文本输入路径
                        </div>
                        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
                            <div style="text-align:center;flex:1;min-width:100px;">
                                <div style="background:linear-gradient(135deg,#667eea,#764ba2);
                                    padding:12px;border-radius:10px;color:white;">
                                    <div style="font-size:1.3em;margin-bottom:3px;">📝</div>
                                    <div style="font-weight:600;font-size:0.8em;">文本输入</div>
                                </div>
                            </div>
                            <div style="font-size:1.2em;color:#94a3b8;">→</div>
                            <div style="text-align:center;flex:1;min-width:100px;">
                                <div style="background:linear-gradient(135deg,#f59e0b,#d97706);
                                    padding:12px;border-radius:10px;color:white;">
                                    <div style="font-size:1.3em;margin-bottom:3px;">🧠</div>
                                    <div style="font-weight:600;font-size:0.8em;">LLM 推理</div>
                                </div>
                            </div>
                            <div style="font-size:1.2em;color:#94a3b8;">→</div>
                            <div style="text-align:center;flex:1;min-width:100px;">
                                <div style="background:linear-gradient(135deg,#8b5cf6,#7c3aed);
                                    padding:12px;border-radius:10px;color:white;">
                                    <div style="font-size:1.3em;margin-bottom:3px;">🛠️</div>
                                    <div style="font-weight:600;font-size:0.8em;">工具调用</div>
                                </div>
                            </div>
                            <div style="font-size:1.2em;color:#94a3b8;">→</div>
                            <div style="text-align:center;flex:1;min-width:100px;">
                                <div style="background:linear-gradient(135deg,#ec4899,#db2777);
                                    padding:12px;border-radius:10px;color:white;">
                                    <div style="font-size:1.3em;margin-bottom:3px;">🎵</div>
                                    <div style="font-weight:600;font-size:0.8em;">TTS 合成</div>
                                </div>
                            </div>
                            <div style="font-size:1.2em;color:#94a3b8;">→</div>
                            <div style="text-align:center;flex:1;min-width:100px;">
                                <div style="background:linear-gradient(135deg,#3b82f6,#2563eb);
                                    padding:12px;border-radius:10px;color:white;">
                                    <div style="font-size:1.3em;margin-bottom:3px;">🎀</div>
                                    <div style="font-weight:600;font-size:0.8em;">数字人</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- 语音输入路径 -->
                    <div style="padding:15px;background:linear-gradient(135deg,#fef3c7,#fde68a);
                        border-radius:12px;border-left:4px solid #f59e0b;">
                        <div style="font-weight:600;color:#92400e;margin-bottom:10px;font-size:0.9em;">
                            🎤 语音输入路径
                        </div>
                        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
                            <div style="text-align:center;flex:1;min-width:100px;">
                                <div style="background:linear-gradient(135deg,#667eea,#764ba2);
                                    padding:12px;border-radius:10px;color:white;">
                                    <div style="font-size:1.3em;margin-bottom:3px;">🎤</div>
                                    <div style="font-weight:600;font-size:0.8em;">语音输入</div>
                                </div>
                            </div>
                            <div style="font-size:1.2em;color:#94a3b8;">→</div>
                            <div style="text-align:center;flex:1;min-width:100px;">
                                <div style="background:linear-gradient(135deg,#10b981,#059669);
                                    padding:12px;border-radius:10px;color:white;">
                                    <div style="font-size:1.3em;margin-bottom:3px;">🔤</div>
                                    <div style="font-weight:600;font-size:0.8em;">ASR 识别</div>
                                </div>
                            </div>
                            <div style="font-size:1.2em;color:#94a3b8;">→</div>
                            <div style="text-align:center;flex:1;min-width:100px;">
                                <div style="background:linear-gradient(135deg,#f59e0b,#d97706);
                                    padding:12px;border-radius:10px;color:white;">
                                    <div style="font-size:1.3em;margin-bottom:3px;">🧠</div>
                                    <div style="font-weight:600;font-size:0.8em;">LLM 推理</div>
                                </div>
                            </div>
                            <div style="font-size:1.2em;color:#94a3b8;">→</div>
                            <div style="text-align:center;flex:1;min-width:100px;">
                                <div style="background:linear-gradient(135deg,#8b5cf6,#7c3aed);
                                    padding:12px;border-radius:10px;color:white;">
                                    <div style="font-size:1.3em;margin-bottom:3px;">🛠️</div>
                                    <div style="font-weight:600;font-size:0.8em;">工具调用</div>
                                </div>
                            </div>
                            <div style="font-size:1.2em;color:#94a3b8;">→</div>
                            <div style="text-align:center;flex:1;min-width:100px;">
                                <div style="background:linear-gradient(135deg,#ec4899,#db2777);
                                    padding:12px;border-radius:10px;color:white;">
                                    <div style="font-size:1.3em;margin-bottom:3px;">🎵</div>
                                    <div style="font-weight:600;font-size:0.8em;">TTS 合成</div>
                                </div>
                            </div>
                            <div style="font-size:1.2em;color:#94a3b8;">→</div>
                            <div style="text-align:center;flex:1;min-width:100px;">
                                <div style="background:linear-gradient(135deg,#3b82f6,#2563eb);
                                    padding:12px;border-radius:10px;color:white;">
                                    <div style="font-size:1.3em;margin-bottom:3px;">🎀</div>
                                    <div style="font-weight:600;font-size:0.8em;">数字人</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 技术栈 -->
                <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:15px;">
                    <div style="background:linear-gradient(135deg,#1a1a2e,#16213e);padding:15px;border-radius:12px;
                        box-shadow:0 2px 10px rgba(0,0,0,0.2);border-left:4px solid #667eea;">
                        <div style="font-weight:700;color:#ffffff;margin-bottom:8px;">🤖 AI 模型</div>
                        <div style="font-size:0.85em;">
                            <div style="color:#ffffff;">• MiMo v2.5 Pro (1T 参数)</div>
                            <div style="color:#ffffff;">• Function Calling 支持</div>
                            <div style="color:#ffffff;">• 结构化 JSON 响应</div>
                        </div>
                    </div>
                    <div style="background:linear-gradient(135deg,#1a1a2e,#16213e);padding:15px;border-radius:12px;
                        box-shadow:0 2px 10px rgba(0,0,0,0.2);border-left:4px solid #10b981;">
                        <div style="font-weight:700;color:#ffffff;margin-bottom:8px;">🎨 数字人渲染</div>
                        <div style="font-size:0.85em;">
                            <div style="color:#ffffff;">• Live2D Cubism SDK 4</div>
                            <div style="color:#ffffff;">• PixiJS 渲染引擎</div>
                            <div style="color:#ffffff;">• iframe 隔离渲染</div>
                        </div>
                    </div>
                    <div style="background:linear-gradient(135deg,#1a1a2e,#16213e);padding:15px;border-radius:12px;
                        box-shadow:0 2px 10px rgba(0,0,0,0.2);border-left:4px solid #f59e0b;">
                        <div style="font-weight:700;color:#ffffff;margin-bottom:8px;">🔧 工具系统</div>
                        <div style="font-size:0.85em;">
                            <div style="color:#ffffff;">• 9 种实用工具</div>
                            <div style="color:#ffffff;">• 自动意图识别</div>
                            <div style="color:#ffffff;">• 统一注册管理</div>
                        </div>
                    </div>
                    <div style="background:linear-gradient(135deg,#1a1a2e,#16213e);padding:15px;border-radius:12px;
                        box-shadow:0 2px 10px rgba(0,0,0,0.2);border-left:4px solid #8b5cf6;">
                        <div style="font-weight:700;color:#ffffff;margin-bottom:8px;">💾 数据存储</div>
                        <div style="font-size:0.85em;">
                            <div style="color:#ffffff;">• JSON 文件持久化</div>
                            <div style="color:#ffffff;">• 会话历史保存</div>
                            <div style="color:#ffffff;">• Soul Memory 记忆</div>
                        </div>
                    </div>
                </div>
            </div>
            """)

            gr.Markdown("""
            <div style="text-align:center;margin:15px 0;">
                <span style="font-size:1.3em;font-weight:700;
                    background:linear-gradient(135deg,#667eea,#764ba2);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                    💬 智能对话
                </span>
                <span style="color:#6b7280;font-size:0.9em;margin-left:10px;">
                    与数字人实时交互
                </span>
            </div>
            """)

            with gr.Row(equal_height=False):
                # 左侧：对话区
                with gr.Column(scale=3):
                    # 对话框上方的会话选择器
                    with gr.Row():
                        with gr.Column(scale=5):
                            chatbot_session_selector = gr.Dropdown(
                                choices=self._get_initial_session_choices(),
                                label="💬 对话历史 - 切换会话",
                                info="当前会话 | 点击选择其他会话",
                                value=None,
                                interactive=True,
                                show_label=True
                            )
                        with gr.Column(scale=1):
                            quick_load_btn = gr.Button("📂 加载", size="sm", variant="secondary")

                    chatbot = gr.Chatbot(
                        label="",
                        height=480,
                        show_label=False,
                        avatar_images=(None, None)
                    )

                    # 文本输入区
                    with gr.Row():
                        msg_input = gr.Textbox(
                            label="",
                            placeholder="💭 输入消息或使用语音输入...",
                            scale=6,
                            show_label=False,
                            container=False
                        )
                        send_btn = gr.Button("📤 发送", variant="primary", scale=1)
                        new_session_btn = gr.Button("🆕 新会话", size="sm", scale=1)
                        clear_btn = gr.Button("🗑️", size="sm", scale=1)

                    # 语音输入区
                    with gr.Row():
                        audio_input = gr.Audio(
                            label="🎤 语音输入",
                            sources=["microphone", "upload"],
                            type="filepath",
                            show_label=True,
                            scale=4
                        )
                        with gr.Column(scale=1):
                            voice_btn = gr.Button("🎙️ 识别语音", variant="secondary", size="sm")
                            recognized_text = gr.Textbox(
                                label="识别结果",
                                placeholder="识别文本...",
                                interactive=False,
                                show_label=False,
                                max_lines=2
                            )

                    # 工具面板 - 水平排列
                    with gr.Row():
                        # 历史管理功能
                        with gr.Accordion("📜 会话管理", open=False):
                            gr.Markdown("""
                            <div style="padding:6px;background:linear-gradient(135deg,#fef3c7,#fde68a);
                                border-radius:8px;margin-bottom:8px;text-align:center;">
                                <span style="font-weight:600;color:#92400e;font-size:0.85em;">
                                    💾 管理您的对话记录
                                </span>
                            </div>
                            """)

                            # 会话选择
                            session_selector = gr.Dropdown(
                                choices=self._get_initial_session_choices(),
                                label="📂 选择会话",
                                info="💡 显示第一条消息以便识别",
                                interactive=True
                            )
                            with gr.Row():
                                refresh_sessions_btn = gr.Button("🔄 刷新列表", size="sm")
                                load_session_btn = gr.Button("📂 加载会话", size="sm", variant="primary")

                            session_status = gr.Textbox(
                                label="状态",
                                interactive=False,
                                show_label=False
                            )

                            gr.Markdown("---")

                            # 导出和搜索
                            with gr.Row():
                                export_btn = gr.Button("💾 导出当前会话", size="sm")
                            with gr.Row():
                                search_input = gr.Textbox(
                                    placeholder="🔍 搜索所有会话...",
                                    show_label=False,
                                    scale=3
                                )
                                search_btn = gr.Button("🔎", size="sm", scale=1)
                            search_results = gr.HTML("")

                            gr.Markdown("""
                            <div style="margin-top:8px;padding:8px;background:rgba(249,250,251,0.8);
                                border-radius:6px;font-size:0.75em;color:#6b7280;">
                                💡 <b>提示：</b><br>
                                • 🆕 新建会话：保存当前会话并创建新对话<br>
                                • 🗑️ 清空所有：保存后重置所有数据<br>
                                • 📂 加载会话：从历史中恢复会话<br>
                                • 💾 导出：保存对话为JSON文件<br>
                                • 🔍 搜索：查找所有会话内容
                            </div>
                            """)

                        # 音色选择 - 更醒目的样式
                        with gr.Accordion("🎵 音色选择", open=True):
                            gr.Markdown("""
                            <div style="padding:8px;background:linear-gradient(135deg,#ffecd2,#fcb69f);
                                border-radius:8px;margin-bottom:10px;text-align:center;">
                                <span style="font-weight:600;color:#8B4513;">
                                    选择您喜欢的音色
                                </span>
                            </div>
                            """)
                            voice_selector = gr.Dropdown(
                                choices=[
                                    "冰糖", "茉莉", "苏打", "白桦",
                                    "Mia", "Chloe", "Milo", "Dean"
                                ],
                                value="冰糖",
                                label="当前音色",
                                info="✨ 8种专业音色任您选择"
                            )

                        # 快速示例 - 可点击按钮（一键发送）
                        with gr.Accordion("💡 快速示例", open=False):
                            gr.Markdown("""
                            <div style="padding:8px;background:linear-gradient(135deg,#e0f2fe,#dbeafe);
                                border-radius:8px;margin-bottom:10px;text-align:center;">
                                <span style="font-weight:600;color:#0369a1;">
                                    点击下方按钮立即发送
                                </span>
                            </div>
                            """)
                            with gr.Row():
                                example_btn1 = gr.Button("🌤️ 北京天气", size="sm")
                                example_btn2 = gr.Button("🔍 AI最新进展", size="sm")
                            with gr.Row():
                                example_btn3 = gr.Button("📰 科技新闻", size="sm")
                                example_btn4 = gr.Button("🌐 翻译Hello", size="sm")
                            with gr.Row():
                                example_btn5 = gr.Button("📅 今天星期几", size="sm")
                                example_btn6 = gr.Button("💬 讲个笑话", size="sm")
                            with gr.Row():
                                example_btn7 = gr.Button("🧮 1+1等于几", size="sm")
                                example_btn8 = gr.Button("🎵 推荐歌曲", size="sm")

                        # 可用工具展示
                        with gr.Accordion("🛠️ 可用工具", open=False):
                            gr.Markdown("""
                            <div style="padding:10px;background:linear-gradient(135deg,#fef3c7,#fde68a);
                                border-radius:8px;margin-bottom:10px;text-align:center;">
                                <span style="font-weight:700;color:#92400e;">
                                    🚀 强大的工具库
                                </span>
                            </div>
                            """)
                            with gr.Row():
                                tool_btn1 = gr.Button("🌤️ 天气查询", size="sm")
                                tool_btn2 = gr.Button("🔍 网络搜索", size="sm")
                            with gr.Row():
                                tool_btn3 = gr.Button("🌐 文本翻译", size="sm")
                                tool_btn4 = gr.Button("🧮 数学计算", size="sm")
                            with gr.Row():
                                tool_btn5 = gr.Button("📅 日期时间", size="sm")
                                tool_btn6 = gr.Button("📰 新闻资讯", size="sm")
                            with gr.Row():
                                tool_btn7 = gr.Button("💱 汇率换算", size="sm")
                                tool_btn8 = gr.Button("🎲 随机数生成", size="sm")
                            with gr.Row():
                                tool_btn9 = gr.Button("📝 文本处理", size="sm")
                                tool_btn10 = gr.Button("🎨 创意灵感", size="sm")

                        # Soul Memory 管理
                        with gr.Accordion("🧠 Soul Memory", open=False):
                            gr.Markdown("""
                            <div style="padding:10px;background:linear-gradient(135deg,#e0c3fc,#8ec5fc);
                                border-radius:8px;margin-bottom:10px;text-align:center;">
                                <span style="font-weight:700;color:#4338ca;">
                                    🌟 灵魂记忆与技能系统
                                </span>
                            </div>
                            """)

                            # 记忆摘要显示
                            memory_summary = gr.HTML(
                                value=self._format_memory_summary(),
                                label="记忆摘要"
                            )

                            with gr.Tabs():
                                # 人格设定
                                with gr.Tab("🎭 人格"):
                                    personality_name = gr.Textbox(
                                        label="名称",
                                        value=self.soul_memory.personality["name"]
                                    )
                                    personality_role = gr.Textbox(
                                        label="角色",
                                        value=self.soul_memory.personality["role"]
                                    )
                                    personality_traits = gr.Textbox(
                                        label="特质",
                                        placeholder="可用逗号、顿号分隔多个特质，如：友好，专业，高效",
                                        value="，".join(self.soul_memory.personality["traits"])
                                    )
                                    personality_style = gr.Textbox(
                                        label="说话风格",
                                        value=self.soul_memory.personality["speaking_style"]
                                    )
                                    update_personality_btn = gr.Button("💾 保存人格设定", variant="primary")

                                # 用户画像
                                with gr.Tab("👤 用户"):
                                    user_name = gr.Textbox(
                                        label="用户名称",
                                        value=self.soul_memory.user_profile.get("name", "")
                                    )
                                    user_interests = gr.Textbox(
                                        label="兴趣爱好",
                                        placeholder="可用逗号、顿号分隔多个兴趣，如：编程，音乐，运动",
                                        value="，".join(self.soul_memory.user_profile["interests"])
                                    )
                                    user_habits = gr.Textbox(
                                        label="使用习惯",
                                        placeholder="可用逗号、顿号分隔多个习惯，如：晚上工作，喜欢语音交互",
                                        value="，".join(self.soul_memory.user_profile["habits"])
                                    )
                                    user_background = gr.Textbox(
                                        label="背景信息",
                                        value=self.soul_memory.user_profile.get("background", "")
                                    )
                                    update_user_btn = gr.Button("💾 保存用户画像", variant="primary")

                                # 技能管理
                                with gr.Tab("🛠️ 技能"):
                                    skills_display = gr.HTML(
                                        value=self._format_skills_display()
                                    )
                                    new_skill_name = gr.Textbox(
                                        label="新技能名称",
                                        placeholder="例如：Python编程"
                                    )
                                    new_skill_level = gr.Dropdown(
                                        label="技能等级",
                                        choices=["beginner", "intermediate", "expert"],
                                        value="intermediate"
                                    )
                                    with gr.Row():
                                        add_skill_btn = gr.Button("➕ 添加技能", size="sm")
                                        refresh_skills_btn = gr.Button("🔄 刷新列表", size="sm")

                                # 偏好设置
                                with gr.Tab("⚙️ 偏好"):
                                    pref_language = gr.Dropdown(
                                        label="语言",
                                        choices=["中文", "English", "日本語"],
                                        value=self.soul_memory.preferences["language"]
                                    )
                                    pref_response_style = gr.Dropdown(
                                        label="回复风格",
                                        choices=["简洁", "适中", "详细"],
                                        value=self.soul_memory.preferences["response_style"]
                                    )
                                    pref_emoji = gr.Dropdown(
                                        label="表情符号使用",
                                        choices=["少", "适中", "多"],
                                        value=self.soul_memory.preferences["emoji_usage"]
                                    )
                                    pref_formality = gr.Dropdown(
                                        label="正式程度",
                                        choices=["随意", "友好", "正式"],
                                        value=self.soul_memory.preferences["formality"]
                                    )
                                    update_preferences_btn = gr.Button("💾 保存偏好设置", variant="primary")

                            # 导入导出
                            with gr.Row():
                                export_memory_btn = gr.Button("💾 导出记忆", size="sm")
                                import_memory_btn = gr.Button("📂 导入记忆", size="sm")

                            memory_status = gr.Textbox(
                                label="状态",
                                interactive=False,
                                show_label=False
                            )

                # 右侧：Live2D和统计
                with gr.Column(scale=1):
                    # Live2D - 更突出的展示
                    gr.Markdown("""
                    <div style="text-align:center;margin-bottom:12px;">
                        <span style="font-size:1.4em;font-weight:800;
                            background:linear-gradient(135deg,#667eea,#764ba2);
                            -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                            💫 Live2D数字人
                        </span>
                    </div>
                    """)
                    live2d_html = gr.HTML(self._get_live2d_html())

                    # 隐藏的触发器组件
                    speaking_trigger = gr.Textbox(
                        value="idle",
                        visible=False,
                        elem_id="speaking_trigger"
                    )

                    # 统计信息
                    stats_display = gr.HTML(self._format_stats())

            # ============================================
            # 底部信息 - 技术栈和实现路径
            # ============================================
            gr.HTML("""
            <div style="margin-top:30px;padding:35px;
                background:linear-gradient(135deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%);
                border-radius:20px;color:#ffffff;">
                <!-- 标题 -->
                <div style="text-align:center;margin-bottom:30px;">
                    <div style="font-size:2em;font-weight:900;margin-bottom:10px;
                        background:linear-gradient(135deg,#667eea,#764ba2,#f093fb);
                        -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                        🚀 技术实现
                    </div>
                    <div style="color:rgba(255,255,255,0.8);font-size:1em;">
                        完整的技术栈和实现路径
                    </div>
                </div>

                <!-- 实现路径 -->
                <div style="background:rgba(255,255,255,0.12);padding:25px;border-radius:16px;
                    margin-bottom:25px;backdrop-filter:blur(10px);
                    border:1px solid rgba(255,255,255,0.15);">
                    <div style="font-weight:800;margin-bottom:18px;font-size:1.2em;color:#ffffff;">
                        📍 实现路径
                    </div>
                    <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px;">
                        <div style="text-align:center;flex:1;min-width:100px;">
                            <div style="background:linear-gradient(135deg,#667eea,#764ba2);
                                padding:12px;border-radius:10px;margin-bottom:8px;">
                                <div style="font-size:1.3em;">1️⃣</div>
                            </div>
                            <div style="font-weight:700;font-size:0.9em;color:#ffffff;">需求分析</div>
                            <div style="font-size:0.75em;color:rgba(255,255,255,0.8);">功能规划</div>
                        </div>
                        <div style="font-size:1.4em;color:rgba(255,255,255,0.6);align-self:center;">→</div>
                        <div style="text-align:center;flex:1;min-width:100px;">
                            <div style="background:linear-gradient(135deg,#10b981,#059669);
                                padding:12px;border-radius:10px;margin-bottom:8px;">
                                <div style="font-size:1.3em;">2️⃣</div>
                            </div>
                            <div style="font-weight:700;font-size:0.9em;color:#ffffff;">架构设计</div>
                            <div style="font-size:0.75em;color:rgba(255,255,255,0.8);">分层设计</div>
                        </div>
                        <div style="font-size:1.4em;color:rgba(255,255,255,0.6);align-self:center;">→</div>
                        <div style="text-align:center;flex:1;min-width:100px;">
                            <div style="background:linear-gradient(135deg,#f59e0b,#d97706);
                                padding:12px;border-radius:10px;margin-bottom:8px;">
                                <div style="font-size:1.3em;">3️⃣</div>
                            </div>
                            <div style="font-weight:700;font-size:0.9em;color:#ffffff;">核心开发</div>
                            <div style="font-size:0.75em;color:rgba(255,255,255,0.8);">模块实现</div>
                        </div>
                        <div style="font-size:1.4em;color:rgba(255,255,255,0.6);align-self:center;">→</div>
                        <div style="text-align:center;flex:1;min-width:100px;">
                            <div style="background:linear-gradient(135deg,#8b5cf6,#7c3aed);
                                padding:12px;border-radius:10px;margin-bottom:8px;">
                                <div style="font-size:1.3em;">4️⃣</div>
                            </div>
                            <div style="font-weight:700;font-size:0.9em;color:#ffffff;">集成测试</div>
                            <div style="font-size:0.75em;color:rgba(255,255,255,0.8);">功能验证</div>
                        </div>
                        <div style="font-size:1.4em;color:rgba(255,255,255,0.6);align-self:center;">→</div>
                        <div style="text-align:center;flex:1;min-width:100px;">
                            <div style="background:linear-gradient(135deg,#ec4899,#db2777);
                                padding:12px;border-radius:10px;margin-bottom:8px;">
                                <div style="font-size:1.3em;">5️⃣</div>
                            </div>
                            <div style="font-weight:700;font-size:0.9em;color:#ffffff;">UI 优化</div>
                            <div style="font-size:0.75em;color:rgba(255,255,255,0.8);">用户体验</div>
                        </div>
                        <div style="font-size:1.4em;color:rgba(255,255,255,0.6);align-self:center;">→</div>
                        <div style="text-align:center;flex:1;min-width:100px;">
                            <div style="background:linear-gradient(135deg,#3b82f6,#2563eb);
                                padding:12px;border-radius:10px;margin-bottom:8px;">
                                <div style="font-size:1.3em;">6️⃣</div>
                            </div>
                            <div style="font-weight:700;font-size:0.9em;color:#ffffff;">部署上线</div>
                            <div style="font-size:0.75em;color:rgba(255,255,255,0.8);">生产就绪</div>
                        </div>
                    </div>
                </div>

                <!-- 技术栈详情 -->
                <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:18px;margin-bottom:25px;">
                    <div style="background:rgba(255,255,255,0.12);padding:20px;border-radius:14px;
                        border:1px solid rgba(255,255,255,0.15);
                        transition:transform 0.3s ease,box-shadow 0.3s ease;">
                        <div style="font-weight:800;margin-bottom:12px;font-size:1.1em;color:#ffffff;">
                            🐍 后端技术
                        </div>
                        <div style="font-size:0.9em;line-height:2;">
                            <div style="color:#ffffff;">• <b style="color:#60a5fa;">Python 3.8+</b> - 核心语言</div>
                            <div style="color:#ffffff;">• <b style="color:#60a5fa;">OpenAI SDK</b> - API 调用</div>
                            <div style="color:#ffffff;">• <b style="color:#60a5fa;">Gradio</b> - Web 界面</div>
                            <div style="color:#ffffff;">• <b style="color:#60a5fa;">PyAudio</b> - 音频处理</div>
                            <div style="color:#ffffff;">• <b style="color:#60a5fa;">Pillow</b> - 图像处理</div>
                        </div>
                    </div>
                    <div style="background:rgba(255,255,255,0.12);padding:20px;border-radius:14px;
                        border:1px solid rgba(255,255,255,0.15);
                        transition:transform 0.3s ease,box-shadow 0.3s ease;">
                        <div style="font-weight:800;margin-bottom:12px;font-size:1.1em;color:#ffffff;">
                            🤖 AI 服务
                        </div>
                        <div style="font-size:0.9em;line-height:2;">
                            <div style="color:#ffffff;">• <b style="color:#a78bfa;">MiMo v2.5 Pro</b> - LLM 推理</div>
                            <div style="color:#ffffff;">• <b style="color:#a78bfa;">MiMo TTS</b> - 语音合成</div>
                            <div style="color:#ffffff;">• <b style="color:#a78bfa;">MiMo ASR</b> - 语音识别</div>
                            <div style="color:#ffffff;">• <b style="color:#a78bfa;">Function Calling</b> - 工具调用</div>
                            <div style="color:#ffffff;">• <b style="color:#a78bfa;">情感分析</b> - 情感识别</div>
                        </div>
                    </div>
                    <div style="background:rgba(255,255,255,0.12);padding:20px;border-radius:14px;
                        border:1px solid rgba(255,255,255,0.15);
                        transition:transform 0.3s ease,box-shadow 0.3s ease;">
                        <div style="font-weight:800;margin-bottom:12px;font-size:1.1em;color:#ffffff;">
                            🎨 前端技术
                        </div>
                        <div style="font-size:0.9em;line-height:2;">
                            <div style="color:#ffffff;">• <b style="color:#f472b6;">Live2D Cubism 4</b> - 数字人渲染</div>
                            <div style="color:#ffffff;">• <b style="color:#f472b6;">PixiJS</b> - 2D 渲染引擎</div>
                            <div style="color:#ffffff;">• <b style="color:#f472b6;">HTML/CSS/JS</b> - 界面开发</div>
                            <div style="color:#ffffff;">• <b style="color:#f472b6;">Gradio Blocks</b> - 组件系统</div>
                            <div style="color:#ffffff;">• <b style="color:#f472b6;">postMessage</b> - 跨窗口通信</div>
                        </div>
                    </div>
                    <div style="background:rgba(255,255,255,0.12);padding:20px;border-radius:14px;
                        border:1px solid rgba(255,255,255,0.15);
                        transition:transform 0.3s ease,box-shadow 0.3s ease;">
                        <div style="font-weight:800;margin-bottom:12px;font-size:1.1em;color:#ffffff;">
                            💾 数据存储
                        </div>
                        <div style="font-size:0.9em;line-height:2;">
                            <div style="color:#ffffff;">• <b style="color:#34d399;">JSON 文件</b> - 持久化存储</div>
                            <div style="color:#ffffff;">• <b style="color:#34d399;">Soul Memory</b> - 记忆系统</div>
                            <div style="color:#ffffff;">• <b style="color:#34d399;">会话管理</b> - 历史保存</div>
                            <div style="color:#ffffff;">• <b style="color:#34d399;">导出/导入</b> - 数据备份</div>
                            <div style="color:#ffffff;">• <b style="color:#34d399;">隐私保护</b> - 本地存储</div>
                        </div>
                    </div>
                </div>

                <!-- 核心特性 -->
                <div style="background:rgba(255,255,255,0.12);padding:25px;border-radius:16px;
                    border:1px solid rgba(255,255,255,0.15);">
                    <div style="font-weight:800;margin-bottom:18px;font-size:1.2em;color:#ffffff;">
                        ✨ 核心特性
                    </div>
                    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:15px;">
                        <div style="display:flex;align-items:center;gap:12px;
                            padding:10px 14px;background:rgba(255,255,255,0.08);border-radius:10px;">
                            <div style="width:10px;height:10px;background:#10b981;border-radius:50%;
                                box-shadow:0 0 8px rgba(16,185,129,0.5);"></div>
                            <span style="font-size:0.95em;color:rgba(255,255,255,0.95);">完全云端化架构，0 显存占用</span>
                        </div>
                        <div style="display:flex;align-items:center;gap:12px;
                            padding:10px 14px;background:rgba(255,255,255,0.08);border-radius:10px;">
                            <div style="width:10px;height:10px;background:#3b82f6;border-radius:50%;
                                box-shadow:0 0 8px rgba(59,130,246,0.5);"></div>
                            <span style="font-size:0.95em;color:rgba(255,255,255,0.95);">Live2D 数字人，真实口型同步</span>
                        </div>
                        <div style="display:flex;align-items:center;gap:12px;
                            padding:10px 14px;background:rgba(255,255,255,0.08);border-radius:10px;">
                            <div style="width:10px;height:10px;background:#8b5cf6;border-radius:50%;
                                box-shadow:0 0 8px rgba(139,92,246,0.5);"></div>
                            <span style="font-size:0.95em;color:rgba(255,255,255,0.95);">9 种工具，自动意图识别</span>
                        </div>
                        <div style="display:flex;align-items:center;gap:12px;
                            padding:10px 14px;background:rgba(255,255,255,0.08);border-radius:10px;">
                            <div style="width:10px;height:10px;background:#ec4899;border-radius:50%;
                                box-shadow:0 0 8px rgba(236,72,153,0.5);"></div>
                            <span style="font-size:0.95em;color:rgba(255,255,255,0.95);">8 种音色，情感智能匹配</span>
                        </div>
                        <div style="display:flex;align-items:center;gap:12px;
                            padding:10px 14px;background:rgba(255,255,255,0.08);border-radius:10px;">
                            <div style="width:10px;height:10px;background:#f59e0b;border-radius:50%;
                                box-shadow:0 0 8px rgba(245,158,11,0.5);"></div>
                            <span style="font-size:0.95em;color:rgba(255,255,255,0.95);">会话持久化，多会话管理</span>
                        </div>
                        <div style="display:flex;align-items:center;gap:12px;
                            padding:10px 14px;background:rgba(255,255,255,0.08);border-radius:10px;">
                            <div style="width:10px;height:10px;background:#14b8a6;border-radius:50%;
                                box-shadow:0 0 8px rgba(20,184,166,0.5);"></div>
                            <span style="font-size:0.95em;color:rgba(255,255,255,0.95);">Soul Memory，个性化定制</span>
                        </div>
                        <div style="display:flex;align-items:center;gap:12px;
                            padding:10px 14px;background:rgba(255,255,255,0.08);border-radius:10px;">
                            <div style="width:10px;height:10px;background:#f97316;border-radius:50%;
                                box-shadow:0 0 8px rgba(249,115,22,0.5);"></div>
                            <span style="font-size:0.95em;color:rgba(255,255,255,0.95);">实时统计，数据可视化</span>
                        </div>
                        <div style="display:flex;align-items:center;gap:12px;
                            padding:10px 14px;background:rgba(255,255,255,0.08);border-radius:10px;">
                            <div style="width:10px;height:10px;background:#06b6d4;border-radius:50%;
                                box-shadow:0 0 8px rgba(6,182,212,0.5);"></div>
                            <span style="font-size:0.95em;color:rgba(255,255,255,0.95);">成本可控，约 ¥1.5/小时</span>
                        </div>
                    </div>
                </div>

                <!-- 版权信息 -->
                <div style="text-align:center;margin-top:30px;padding-top:25px;
                    border-top:1px solid rgba(255,255,255,0.2);">
                    <div style="color:rgba(255,255,255,0.85);font-size:0.95em;">
                        <b style="background:linear-gradient(135deg,#667eea,#764ba2);
                            -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                            Aivo V6
                        </b>
                        <span style="color:rgba(255,255,255,0.7);"> - 基于小米 MiMo API 的智能数字人系统</span>
                    </div>
                    <div style="color:rgba(255,255,255,0.6);font-size:0.85em;margin-top:10px;">
                        Powered by MiMo API · Live2D Cubism SDK · Gradio
                    </div>
                    <div style="color:rgba(255,255,255,0.5);font-size:0.8em;margin-top:8px;">
                        Version 6.0 | 最后更新：2026-06-21 | MIT License
                    </div>
                </div>
            </div>
            """)

            # 事件绑定
            send_btn.click(
                fn=self.chat,
                inputs=[msg_input, chatbot, voice_selector],
                outputs=[chatbot, stats_display]
            ).then(
                fn=lambda: f"speaking_{self.current_emotion}_{int(__import__('time').time() * 1000)}",  # 包含情感
                outputs=speaking_trigger
            ).then(
                fn=lambda: "",
                outputs=msg_input
            )

            msg_input.submit(
                fn=self.chat,
                inputs=[msg_input, chatbot, voice_selector],
                outputs=[chatbot, stats_display]
            ).then(
                fn=lambda: f"speaking_{self.current_emotion}_{int(__import__('time').time() * 1000)}",  # 包含情感
                outputs=speaking_trigger
            ).then(
                fn=lambda: "",
                outputs=msg_input
            )

            voice_btn.click(
                fn=self.process_voice,
                inputs=[audio_input, chatbot, voice_selector],
                outputs=[chatbot, stats_display, recognized_text]
            )

            new_session_btn.click(
                fn=self.new_session,
                outputs=[chatbot, stats_display]
            )

            clear_btn.click(
                fn=self.clear_history,
                outputs=[chatbot, stats_display]
            )

            # 历史管理事件
            def refresh_sessions():
                """刷新会话列表"""
                sessions = self._get_sessions_list()
                choices = []
                for s in sessions:
                    choice = f"💬 \"{s['first_message']}\" ({s['conversation_count']}条) - {s['last_updated']} [ID:{s['id']}]"
                    choices.append(choice)
                return gr.Dropdown(choices=choices)

            def refresh_both_session_selectors():
                """同时刷新两个会话选择器"""
                sessions = self._get_sessions_list()
                choices = []
                for s in sessions:
                    choice = f"💬 \"{s['first_message']}\" ({s['conversation_count']}条) - {s['last_updated']} [ID:{s['id']}]"
                    choices.append(choice)
                return gr.Dropdown(choices=choices), gr.Dropdown(choices=choices)

            refresh_sessions_btn.click(
                fn=refresh_both_session_selectors,
                outputs=[session_selector, chatbot_session_selector]
            )

            def load_session_from_choice(choice):
                """从选择中加载会话"""
                if not choice:
                    return None, self._format_stats(), "请先选择会话", None

                # 从显示文本中提取 session_id
                # 格式：💬 "消息..." (5条) - 2025-06-21 14:30:25 [ID:20250621_143025]
                try:
                    # 提取 [ID:xxx] 中的 session_id
                    if "[ID:" in choice:
                        session_id = choice.split("[ID:")[1].rstrip("]")
                    else:
                        # 备用方案：从时间推导
                        time_part = choice.split(" - ")[-1]
                        session_id = time_part.replace("-", "").replace(":", "").replace(" ", "_")

                    # 尝试加载
                    result = self.load_session(session_id)
                    # result 包含: history, stats, status, current_display
                    return result[0], result[1], result[2], result[3] if len(result) > 3 else choice
                except Exception as e:
                    print(f"解析会话失败: {e}")
                    return None, self._format_stats(), "❌ 无法加载会话", None

            # 右侧面板的加载按钮 - 同步更新两个选择器
            load_session_btn.click(
                fn=load_session_from_choice,
                inputs=[session_selector],
                outputs=[chatbot, stats_display, session_status, chatbot_session_selector]
            )

            # 对话框上方的快速加载按钮 - 同步更新两个选择器
            quick_load_btn.click(
                fn=load_session_from_choice,
                inputs=[chatbot_session_selector],
                outputs=[chatbot, stats_display, session_status, session_selector]
            )

            export_btn.click(
                fn=self.export_history,
                outputs=[search_results]
            )

            search_btn.click(
                fn=self.search_history,
                inputs=[search_input],
                outputs=[search_results]
            )

            # 快速示例按钮 - 直接发送消息
            def quick_send(prompt_text):
                """快速发送示例消息"""
                return prompt_text

            example_btn1.click(
                fn=lambda: "北京今天天气怎么样？",
                outputs=msg_input
            ).then(
                fn=self.chat,
                inputs=[msg_input, chatbot, voice_selector],
                outputs=[chatbot, stats_display]
            ).then(
                fn=lambda: f"speaking_{self.current_emotion}_{int(__import__('time').time() * 1000)}",
                outputs=speaking_trigger
            )

            example_btn2.click(
                fn=lambda: "帮我搜索一下人工智能的最新进展",
                outputs=msg_input
            ).then(
                fn=self.chat,
                inputs=[msg_input, chatbot, voice_selector],
                outputs=[chatbot, stats_display]
            ).then(
                fn=lambda: f"speaking_{self.current_emotion}_{int(__import__('time').time() * 1000)}",
                outputs=speaking_trigger
            )

            example_btn3.click(
                fn=lambda: "给我看看今天的科技新闻",
                outputs=msg_input
            ).then(
                fn=self.chat,
                inputs=[msg_input, chatbot, voice_selector],
                outputs=[chatbot, stats_display]
            ).then(
                fn=lambda: f"speaking_{self.current_emotion}_{int(__import__('time').time() * 1000)}",
                outputs=speaking_trigger
            )

            example_btn4.click(
                fn=lambda: "把'Hello World'翻译成中文",
                outputs=msg_input
            ).then(
                fn=self.chat,
                inputs=[msg_input, chatbot, voice_selector],
                outputs=[chatbot, stats_display]
            ).then(
                fn=lambda: f"speaking_{self.current_emotion}_{int(__import__('time').time() * 1000)}",
                outputs=speaking_trigger
            )

            example_btn5.click(
                fn=lambda: "今天是星期几？现在几点了？",
                outputs=msg_input
            ).then(
                fn=self.chat,
                inputs=[msg_input, chatbot, voice_selector],
                outputs=[chatbot, stats_display]
            ).then(
                fn=lambda: f"speaking_{self.current_emotion}_{int(__import__('time').time() * 1000)}",
                outputs=speaking_trigger
            )

            example_btn6.click(
                fn=lambda: "给我讲个笑话吧",
                outputs=msg_input
            ).then(
                fn=self.chat,
                inputs=[msg_input, chatbot, voice_selector],
                outputs=[chatbot, stats_display]
            ).then(
                fn=lambda: f"speaking_{self.current_emotion}_{int(__import__('time').time() * 1000)}",
                outputs=speaking_trigger
            )

            example_btn7.click(
                fn=lambda: "1加1等于几？帮我算一下",
                outputs=msg_input
            ).then(
                fn=self.chat,
                inputs=[msg_input, chatbot, voice_selector],
                outputs=[chatbot, stats_display]
            ).then(
                fn=lambda: f"speaking_{self.current_emotion}_{int(__import__('time').time() * 1000)}",
                outputs=speaking_trigger
            )

            example_btn8.click(
                fn=lambda: "推荐几首好听的歌曲给我",
                outputs=msg_input
            ).then(
                fn=self.chat,
                inputs=[msg_input, chatbot, voice_selector],
                outputs=[chatbot, stats_display]
            ).then(
                fn=lambda: f"speaking_{self.current_emotion}_{int(__import__('time').time() * 1000)}",
                outputs=speaking_trigger
            )

            # 工具按钮 - 填充到输入框
            tool_btn1.click(lambda: "帮我查询一下上海今天的天气", outputs=msg_input)
            tool_btn2.click(lambda: "搜索一下最近有什么重大新闻", outputs=msg_input)
            tool_btn3.click(lambda: "把'Thank you'翻译成法语", outputs=msg_input)
            tool_btn4.click(lambda: "帮我计算 123 * 456", outputs=msg_input)
            tool_btn5.click(lambda: "现在是什么时间？今天几号？", outputs=msg_input)
            tool_btn6.click(lambda: "给我看看今天的头条新闻", outputs=msg_input)
            tool_btn7.click(lambda: "100美元等于多少人民币？", outputs=msg_input)
            tool_btn8.click(lambda: "给我生成一个1到100之间的随机数", outputs=msg_input)
            tool_btn9.click(lambda: "帮我把这段文字转换成大写：hello world", outputs=msg_input)
            tool_btn10.click(lambda: "给我一些关于写作的创意灵感", outputs=msg_input)

            # Soul Memory 事件绑定
            update_personality_btn.click(
                fn=self.update_personality_memory,
                inputs=[personality_name, personality_role, personality_traits, personality_style],
                outputs=[memory_summary, memory_status]
            )

            update_user_btn.click(
                fn=self.update_user_memory,
                inputs=[user_name, user_interests, user_habits, user_background],
                outputs=[memory_summary, memory_status]
            )

            add_skill_btn.click(
                fn=self.add_skill_to_memory,
                inputs=[new_skill_name, new_skill_level],
                outputs=[skills_display, memory_status]
            )

            refresh_skills_btn.click(
                fn=lambda: self._format_skills_display(),
                outputs=[skills_display]
            )

            update_preferences_btn.click(
                fn=self.update_preferences_memory,
                inputs=[pref_language, pref_response_style, pref_emoji, pref_formality],
                outputs=[memory_summary, memory_status]
            )

            export_memory_btn.click(
                fn=self.export_memory,
                outputs=[memory_status]
            )

            import_memory_btn.click(
                fn=lambda: "💡 请使用文件管理器手动导入 memory/ 目录下的 JSON 文件",
                outputs=[memory_status]
            )

            # 监听 speaking_trigger 的变化，触发 JavaScript
            speaking_trigger.change(
                fn=None,
                inputs=[speaking_trigger],
                outputs=None,
                js="""
                function(value) {
                    console.log('[Trigger] 状态变化:', value);
                    const iframes = document.querySelectorAll('iframe');
                    console.log('[Trigger] 找到iframe数量:', iframes.length);

                    iframes.forEach(function(iframe) {
                        try {
                            iframe.contentWindow.postMessage(value, '*');
                            console.log('[Trigger] 发送消息到iframe:', value);
                        } catch(e) {
                            console.log('[Trigger] 发送失败:', e);
                        }
                    });

                    // 如果是speaking状态，5秒后自动发送idle
                    if (value && value.toString().startsWith('speaking')) {
                        console.log('[Trigger] 设置5秒后自动停止');
                        setTimeout(function() {
                            console.log('[Trigger] 自动发送idle消息');
                            iframes.forEach(function(iframe) {
                                try {
                                    iframe.contentWindow.postMessage('idle', '*');
                                    console.log('[Trigger] 已发送idle消息');
                                } catch(e) {
                                    console.log('[Trigger] 发送idle失败:', e);
                                }
                            });
                        }, 5000);
                    }

                    return value;
                }
                """
            )

        return interface


def main():
    """启动Web界面"""
    print("=" * 70)
    print("🎀 Aivo V6 - 智能数字人系统")
    print("   基于小米 MiMo API 的智能数字人系统")
    print("=" * 70)
    print("\n🏗️ 系统架构：")
    print("  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐")
    print("  │  用户输入   │ → │  ASR 识别   │ → │  LLM 推理   │")
    print("  └─────────────┘    └─────────────┘    └─────────────┘")
    print("                                            ↓")
    print("  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐")
    print("  │   输出展示   │ ← │  TTS 合成   │ ← │  工具调用   │")
    print("  └─────────────┘    └─────────────┘    └─────────────┘")
    print("\n✨ 核心特性：")
    print("  🎀 Live2D 数字人  │ 3 个模型可切换，语音同步动画")
    print("  🎵 气泡语音       │ 音频嵌入对话气泡，自动播放")
    print("  🛠️ 9 种工具       │ 天气、搜索、翻译、计算、新闻等")
    print("  🎤 8 种音色       │ 中英文男女声，情感智能匹配")
    print("  📊 实时统计       │ 对话轮次、响应时间、情感分布")
    print("  📜 会话管理       │ 持久化存储、多会话切换、历史搜索")
    print("  🧠 Soul Memory   │ 人格设定、用户画像、技能管理")
    print("\n🔧 技术栈：")
    print("  • Python 3.8+    │ 后端开发语言")
    print("  • Gradio         │ Web 界面框架")
    print("  • MiMo API       │ AI 模型服务")
    print("  • Live2D         │ 数字人渲染")
    print("  • PixiJS         │ 2D 渲染引擎")
    print("\n💡 使用提示：")
    print("  • Live2D 在右侧显示，点击可切换模型")
    print("  • 播放语音时 Live2D 会自动说话")
    print("  • 点击\"快速示例\"按钮立即发送")
    print("  • 支持语音输入和文本输入")
    print("  • 可导出对话历史为 JSON 文件")
    print("  • Soul Memory 可自定义 AI 人格")
    print("\n🚀 启动中...")
    print("=" * 70)

    ui = AivoWebUIV6()
    interface = ui.build_interface()

    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True,
        show_error=True,
        allowed_paths=[str(STATIC_DIR)],
        css=ui.custom_css
    )


if __name__ == "__main__":
    main()
