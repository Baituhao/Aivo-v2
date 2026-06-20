#!/usr/bin/env python3
"""
Aivo Web界面 - 现代化重新设计

使用Gradio构建美观的交互式Web界面
"""

import os
import sys
import gradio as gr
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from llm_service_v2 import LLMServiceWithTools
from tts_service import TTSService
from voice_manager import VoiceManager


class AivoWebUI:
    def __init__(self):
        """初始化Web UI"""
        self.llm = LLMServiceWithTools()
        self.tts = TTSService()
        self.voice_manager = VoiceManager()

        # 统计信息
        self.stats = {
            "conversation_count": 0,
            "tool_calls": 0,
            "emotion_changes": 0,
            "last_emotion": "neutral"
        }

        # 表情图片映射
        self.emotion_images = {
            "happy": "assets/emotions/happy.png",
            "sad": "assets/emotions/sad.png",
            "neutral": "assets/emotions/neutral.png",
            "surprised": "assets/emotions/surprised.png"
        }

    def chat(self, message: str, history: list):
        """处理聊天消息"""
        if not message.strip():
            return history, None, self._format_status("neutral", "none"), self.emotion_images['neutral'], self._format_stats()

        try:
            # 1. LLM生成回复
            response = self.llm.chat(message)

            # 2. TTS合成语音
            audio_path = self.tts.synthesize(
                text=response['speech'],
                emotion=response['emotion']
            )

            # 3. 更新对话历史
            if history is None:
                history = []

            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": response['speech']})

            # 4. 更新统计
            self.stats['conversation_count'] += 1
            if response['emotion'] != self.stats['last_emotion']:
                self.stats['emotion_changes'] += 1
                self.stats['last_emotion'] = response['emotion']

            # 5. 格式化状态和统计
            status = self._format_status(response['emotion'], response['action'])
            emotion_img = self.emotion_images.get(response['emotion'], self.emotion_images['neutral'])
            stats_md = self._format_stats()

            return history, audio_path, status, emotion_img, stats_md

        except Exception as e:
            error_status = f"""
            <div class="status-box error">
                <span class="status-icon">⚠️</span>
                <span class="status-text">错误: {str(e)}</span>
            </div>
            """
            return history, None, error_status, self.emotion_images['sad'], self._format_stats()

    def _format_status(self, emotion: str, action: str) -> str:
        """格式化状态显示"""
        emotion_data = {
            "happy": {"emoji": "😊", "text": "开心", "color": "#FFD700"},
            "sad": {"emoji": "😢", "text": "难过", "color": "#6495ED"},
            "neutral": {"emoji": "😐", "text": "平静", "color": "#A9A9A9"},
            "surprised": {"emoji": "😲", "text": "惊讶", "color": "#FF69B4"}
        }

        action_data = {
            "nod": {"emoji": "👍", "text": "点头"},
            "shake": {"emoji": "👎", "text": "摇头"},
            "wave": {"emoji": "👋", "text": "挥手"},
            "none": {"emoji": "🤚", "text": "无动作"}
        }

        e = emotion_data.get(emotion, emotion_data['neutral'])
        a = action_data.get(action, action_data['none'])

        return f"""
        <div class="status-container">
            <div class="status-card" style="border-left: 4px solid {e['color']}">
                <div class="status-item">
                    <span class="status-label">情感状态</span>
                    <span class="status-value">{e['emoji']} {e['text']}</span>
                </div>
            </div>
            <div class="status-card">
                <div class="status-item">
                    <span class="status-label">动作反馈</span>
                    <span class="status-value">{a['emoji']} {a['text']}</span>
                </div>
            </div>
        </div>
        """

    def _format_stats(self) -> str:
        """格式化统计信息"""
        return f"""
        <div class="stats-container">
            <div class="stat-card">
                <div class="stat-icon">💬</div>
                <div class="stat-content">
                    <div class="stat-value">{self.stats['conversation_count']}</div>
                    <div class="stat-label">对话轮数</div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">🔧</div>
                <div class="stat-content">
                    <div class="stat-value">{self.stats['tool_calls']}</div>
                    <div class="stat-label">工具调用</div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">🎭</div>
                <div class="stat-content">
                    <div class="stat-value">{self.stats['emotion_changes']}</div>
                    <div class="stat-label">情感切换</div>
                </div>
            </div>
        </div>
        """

    def clear_history(self):
        """清空对话历史"""
        self.llm.clear_history()
        self.stats = {
            "conversation_count": 0,
            "tool_calls": 0,
            "emotion_changes": 0,
            "last_emotion": "neutral"
        }
        success_status = """
        <div class="status-box success">
            <span class="status-icon">✨</span>
            <span class="status-text">对话历史已清空</span>
        </div>
        """
        return [], None, success_status, self.emotion_images['neutral'], self._format_stats()

    def change_voice(self, gender: str):
        """切换音色"""
        self.voice_manager.update_settings(gender_preference=gender)
        voice_names = {"female": "女声", "male": "男声"}
        return f"""
        <div class="status-box info">
            <span class="status-icon">🎵</span>
            <span class="status-text">已切换到 {voice_names[gender]}</span>
        </div>
        """

    def build_interface(self):
        """构建Gradio界面"""

        # 现代化CSS样式
        custom_css = """
        /* 全局样式 */
        .gradio-container {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* 标题样式 */
        .hero-section {
            text-align: center;
            padding: 30px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }

        .hero-title {
            font-size: 3em;
            font-weight: 800;
            color: white;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }

        .hero-subtitle {
            font-size: 1.1em;
            color: rgba(255,255,255,0.9);
            margin-top: 10px;
        }

        /* 状态卡片 */
        .status-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin: 15px 0;
        }

        .status-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        .status-item {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .status-label {
            font-size: 0.85em;
            color: #666;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .status-value {
            font-size: 1.5em;
            font-weight: 700;
            color: #2c3e50;
        }

        /* 统计卡片 */
        .stats-container {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin: 20px 0;
        }

        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            text-align: center;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }

        .stat-icon {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .stat-value {
            font-size: 2em;
            font-weight: 800;
            color: #667eea;
            margin: 5px 0;
        }

        .stat-label {
            font-size: 0.9em;
            color: #666;
            font-weight: 500;
        }

        /* 状态提示框 */
        .status-box {
            padding: 15px 20px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            gap: 12px;
            margin: 10px 0;
            font-size: 1.1em;
            font-weight: 600;
        }

        .status-box.success {
            background: #d4edda;
            color: #155724;
        }

        .status-box.error {
            background: #f8d7da;
            color: #721c24;
        }

        .status-box.info {
            background: #d1ecf1;
            color: #0c5460;
        }

        .status-icon {
            font-size: 1.5em;
        }

        /* 表情图片 */
        .emotion-display {
            border-radius: 20px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);
            transition: transform 0.3s ease;
        }

        .emotion-display:hover {
            transform: scale(1.05);
        }

        /* 工具卡片 */
        .tool-card {
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            padding: 15px;
            border-radius: 12px;
            margin: 10px 0;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }

        .tool-title {
            font-weight: 700;
            font-size: 1.1em;
            margin-bottom: 5px;
            color: #8b4513;
        }

        .tool-example {
            font-style: italic;
            color: #666;
            font-size: 0.95em;
        }

        /* 按钮样式 */
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 12px 24px !important;
            font-weight: 600 !important;
            transition: transform 0.2s ease !important;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(102, 126, 234, 0.4) !important;
        }
        """

        with gr.Blocks(title="Aivo数字人", css=custom_css) as interface:

            # 顶部横幅
            gr.HTML("""
            <div class="hero-section">
                <div class="hero-title">🤖 Aivo 数字人</div>
                <div class="hero-subtitle">
                    智能对话 · 情感表达 · 工具调用 · 实时语音
                </div>
            </div>
            """)

            with gr.Row():
                # 左侧：对话区
                with gr.Column(scale=3):
                    chatbot = gr.Chatbot(
                        label="💬 对话区",
                        height=500,
                        show_label=True,
                        avatar_images=("🧑", "🤖")
                    )

                    with gr.Row():
                        msg_input = gr.Textbox(
                            label="",
                            placeholder="💭 输入你想说的话...",
                            scale=5,
                            show_label=False,
                            container=False
                        )
                        send_btn = gr.Button("📤 发送", variant="primary", scale=1)

                    with gr.Row():
                        clear_btn = gr.Button("🗑️ 清空历史", size="sm")

                    status_display = gr.HTML(
                        """
                        <div class="status-box info">
                            <span class="status-icon">✨</span>
                            <span class="status-text">系统就绪，可以开始对话</span>
                        </div>
                        """
                    )

                    audio_output = gr.Audio(
                        label="🔊 语音回复",
                        autoplay=True,
                        show_label=True
                    )

                # 右侧：数字人展示区
                with gr.Column(scale=2):

                    # 数字人表情
                    emotion_display = gr.Image(
                        label="💫 数字人状态",
                        value=self.emotion_images['neutral'],
                        height=320,
                        show_label=True,
                        elem_classes="emotion-display"
                    )

                    # 统计面板
                    stats_display = gr.HTML(self._format_stats())

                    # 设置
                    with gr.Accordion("⚙️ 设置", open=False):
                        voice_gender = gr.Radio(
                            choices=[("👩 女声", "female"), ("👨 男声", "male")],
                            value="female",
                            label="音色选择",
                            info="选择数字人的声音"
                        )

                    # 工具说明
                    with gr.Accordion("🛠️ 可用工具", open=False):
                        gr.HTML("""
                        <div class="tool-card">
                            <div class="tool-title">🌤️ 天气查询</div>
                            <div class="tool-example">"北京今天天气怎么样？"</div>
                        </div>
                        <div class="tool-card">
                            <div class="tool-title">⏰ 时间日期</div>
                            <div class="tool-example">"现在几点了？"</div>
                        </div>
                        <div class="tool-card">
                            <div class="tool-title">🔢 计算器</div>
                            <div class="tool-example">"帮我算 25 × 4"</div>
                        </div>
                        """)

                    # 快速示例
                    with gr.Accordion("💡 快速开始", open=False):
                        examples = gr.Examples(
                            examples=[
                                ["你好，我是小明"],
                                ["北京今天天气怎么样？"],
                                ["现在几点了？"],
                                ["帮我算 (100 + 50) ÷ 3"],
                                ["我今天很开心！"],
                                ["谢谢你的帮助"]
                            ],
                            inputs=msg_input,
                            label=""
                        )

            # 底部信息
            gr.Markdown("""
            <div style="text-align: center; margin-top: 20px; color: #666; font-size: 0.9em;">
                Powered by MiMo API | Built with ❤️ by Aivo Team
            </div>
            """)

            # 事件绑定
            send_btn.click(
                fn=self.chat,
                inputs=[msg_input, chatbot],
                outputs=[chatbot, audio_output, status_display, emotion_display, stats_display]
            ).then(
                fn=lambda: "",
                outputs=msg_input
            )

            msg_input.submit(
                fn=self.chat,
                inputs=[msg_input, chatbot],
                outputs=[chatbot, audio_output, status_display, emotion_display, stats_display]
            ).then(
                fn=lambda: "",
                outputs=msg_input
            )

            clear_btn.click(
                fn=self.clear_history,
                outputs=[chatbot, audio_output, status_display, emotion_display, stats_display]
            )

            voice_gender.change(
                fn=self.change_voice,
                inputs=voice_gender,
                outputs=status_display
            )

        return interface


def main():
    """启动Web界面"""
    print("=" * 60)
    print("🚀 Aivo Web界面启动中...")
    print("=" * 60)

    # 创建UI实例
    ui = AivoWebUI()
    interface = ui.build_interface()

    # 启动服务
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True,
        show_error=True
    )


if __name__ == "__main__":
    main()
