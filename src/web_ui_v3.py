#!/usr/bin/env python3
"""
Aivo Web界面 V3 - 完整版
特性：
1. 2D数字人动画（口型+表情）
2. 8种音色选择
3. 语音输入功能
4. 9个工具支持
"""

import os
import sys
import gradio as gr
import json
import base64
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from llm_service_v2 import LLMServiceWithTools
from tts_service import TTSService
from voice_manager import VoiceManager
from asr_service import ASRService


class AivoWebUIV3:
    def __init__(self):
        """初始化Web UI"""
        self.llm = LLMServiceWithTools()
        self.tts = TTSService()
        self.voice_manager = VoiceManager()
        self.asr = ASRService()

        # 当前选择的音色
        self.current_voice = "冰糖"

        # 统计信息
        self.stats = {
            "conversation_count": 0,
            "tool_calls": 0,
            "emotion_changes": 0,
            "last_emotion": "neutral"
        }

        # 录音状态
        self.is_recording = False

    def chat(self, message: str, history: list, voice_choice: str):
        """处理聊天消息"""
        if not message.strip():
            return history, None, self._get_avatar_svg("neutral", False), self._format_stats()

        try:
            # 更新当前音色
            self.current_voice = voice_choice

            # 1. LLM生成回复
            response = self.llm.chat(message)

            # 2. TTS合成语音（使用指定音色）
            audio_path = self.tts.synthesize(
                text=response['speech'],
                emotion=response['emotion'],
                voice=self.current_voice
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

            # 5. 生成数字人动画
            avatar_svg = self._get_avatar_svg(response['emotion'], True)
            stats_md = self._format_stats()

            return history, audio_path, avatar_svg, stats_md

        except Exception as e:
            error_msg = f"❌ 错误: {str(e)}"
            if history is None:
                history = []
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": error_msg})
            return history, None, self._get_avatar_svg("sad", False), self._format_stats()

    def process_audio_input(self, audio_file, history: list, voice_choice: str):
        """处理语音输入"""
        if audio_file is None:
            return history, None, self._get_avatar_svg("neutral", False), self._format_stats(), ""

        try:
            # ASR识别
            transcript = self.asr.transcribe(audio_file)

            # 调用聊天函数
            return self.chat(transcript, history, voice_choice) + (transcript,)

        except Exception as e:
            error_msg = f"❌ 语音识别失败: {str(e)}"
            if history is None:
                history = []
            history.append({"role": "assistant", "content": error_msg})
            return history, None, self._get_avatar_svg("sad", False), self._format_stats(), ""

    def _get_avatar_svg(self, emotion: str, is_speaking: bool) -> str:
        """生成2D数字人SVG动画"""

        # 表情配置
        emotions_config = {
            "happy": {
                "face_color": "#FFE4B5",
                "eye": "M60,80 Q70,75 80,80",  # 笑眯眯的眼睛
                "mouth": "M60,110 Q80,120 100,110",  # 笑脸嘴巴
                "cheek_color": "#FFB6C1"
            },
            "sad": {
                "face_color": "#E6E6FA",
                "eye": "M60,80 Q70,85 80,80",  # 下垂的眼睛
                "mouth": "M60,115 Q80,105 100,115",  # 难过嘴巴
                "cheek_color": "#B0C4DE"
            },
            "neutral": {
                "face_color": "#FFDAB9",
                "eye": "M60,80 L80,80",  # 平静的眼睛
                "mouth": "M60,110 L100,110",  # 平嘴
                "cheek_color": "#FFC0CB"
            },
            "surprised": {
                "face_color": "#FFF0F5",
                "eye": "M70,80 m-5,0 a 5,5 0 1,0 10,0 a 5,5 0 1,0 -10,0",  # 圆眼睛
                "mouth": "M70,110 m-8,0 a 8,8 0 1,0 16,0 a 8,8 0 1,0 -16,0",  # O型嘴
                "cheek_color": "#FFE4E1"
            }
        }

        config = emotions_config.get(emotion, emotions_config["neutral"])

        # 口型动画（说话时嘴巴动）
        mouth_animation = ""
        if is_speaking:
            mouth_animation = f"""
            <animate attributeName="d"
                values="{config['mouth']};M60,110 Q80,115 100,110;{config['mouth']}"
                dur="0.3s" repeatCount="indefinite"/>
            """

        # 眨眼动画
        eye_animation = """
        <animate attributeName="opacity"
            values="1;0;1" dur="3s" repeatCount="indefinite"/>
        """

        svg = f"""
        <svg width="300" height="300" viewBox="0 0 160 180" xmlns="http://www.w3.org/2000/svg">
            <!-- 背景光晕 -->
            <defs>
                <radialGradient id="glow" cx="50%" cy="50%">
                    <stop offset="0%" style="stop-color:#667eea;stop-opacity:0.3" />
                    <stop offset="100%" style="stop-color:#764ba2;stop-opacity:0" />
                </radialGradient>
            </defs>
            <circle cx="80" cy="90" r="70" fill="url(#glow)"/>

            <!-- 头部 -->
            <ellipse cx="80" cy="90" rx="50" ry="60" fill="{config['face_color']}"
                stroke="#333" stroke-width="2"/>

            <!-- 头发 -->
            <path d="M30,70 Q40,30 80,25 Q120,30 130,70"
                fill="#8B4513" stroke="#654321" stroke-width="2"/>

            <!-- 左眼 -->
            <g opacity="1">
                <path d="{config['eye']}" stroke="#333" stroke-width="3"
                    fill="none" stroke-linecap="round"/>
                {eye_animation}
            </g>

            <!-- 右眼 -->
            <g opacity="1" transform="translate(30,0)">
                <path d="{config['eye']}" stroke="#333" stroke-width="3"
                    fill="none" stroke-linecap="round"/>
                {eye_animation}
            </g>

            <!-- 腮红 -->
            <ellipse cx="45" cy="95" rx="8" ry="6" fill="{config['cheek_color']}" opacity="0.6"/>
            <ellipse cx="115" cy="95" rx="8" ry="6" fill="{config['cheek_color']}" opacity="0.6"/>

            <!-- 嘴巴 -->
            <path d="{config['mouth']}" stroke="#333" stroke-width="3"
                fill="none" stroke-linecap="round">
                {mouth_animation}
            </path>

            <!-- 身体（简化） -->
            <path d="M50,145 Q80,155 110,145" stroke="#667eea" stroke-width="25"
                fill="none" stroke-linecap="round"/>

            <!-- 音波效果（说话时） -->
            {"" if not is_speaking else """
            <g opacity="0.6">
                <circle cx="140" cy="90" r="3" fill="#667eea">
                    <animate attributeName="r" values="3;8;3" dur="1s" repeatCount="indefinite"/>
                    <animate attributeName="opacity" values="0.6;0;0.6" dur="1s" repeatCount="indefinite"/>
                </circle>
                <circle cx="20" cy="90" r="3" fill="#667eea">
                    <animate attributeName="r" values="3;8;3" dur="1s" begin="0.3s" repeatCount="indefinite"/>
                    <animate attributeName="opacity" values="0.6;0;0.6" dur="1s" begin="0.3s" repeatCount="indefinite"/>
                </circle>
            </g>
            """}
        </svg>
        """

        return svg

    def _format_stats(self) -> str:
        """格式化统计信息"""
        return f"""
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 20px 0;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px; border-radius: 15px; text-align: center; color: white; box-shadow: 0 4px 15px rgba(102,126,234,0.3);">
                <div style="font-size: 2.5em;">💬</div>
                <div style="font-size: 2em; font-weight: 800; margin: 10px 0;">{self.stats['conversation_count']}</div>
                <div style="font-size: 0.9em; opacity: 0.9;">对话轮数</div>
            </div>
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                padding: 20px; border-radius: 15px; text-align: center; color: white; box-shadow: 0 4px 15px rgba(240,147,251,0.3);">
                <div style="font-size: 2.5em;">🔧</div>
                <div style="font-size: 2em; font-weight: 800; margin: 10px 0;">{self.stats['tool_calls']}</div>
                <div style="font-size: 0.9em; opacity: 0.9;">工具调用</div>
            </div>
            <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                padding: 20px; border-radius: 15px; text-align: center; color: white; box-shadow: 0 4px 15px rgba(79,172,254,0.3);">
                <div style="font-size: 2.5em;">🎭</div>
                <div style="font-size: 2em; font-weight: 800; margin: 10px 0;">{self.stats['emotion_changes']}</div>
                <div style="font-size: 0.9em; opacity: 0.9;">情感切换</div>
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
        return [], None, self._get_avatar_svg("neutral", False), self._format_stats()

    def build_interface(self):
        """构建Gradio界面"""

        custom_css = """
        .gradio-container {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            max-width: 1400px !important;
        }

        .hero-section {
            text-align: center;
            padding: 40px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 25px;
            margin-bottom: 30px;
            box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
        }

        .hero-title {
            font-size: 3.5em;
            font-weight: 900;
            color: white;
            margin: 0;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.2);
        }

        .hero-subtitle {
            font-size: 1.2em;
            color: rgba(255,255,255,0.95);
            margin-top: 15px;
            font-weight: 500;
        }

        .avatar-container {
            background: white;
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.12);
            margin-bottom: 20px;
        }

        .tool-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            margin: 15px 0;
        }

        .tool-item {
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            padding: 12px;
            border-radius: 12px;
            text-align: center;
            font-weight: 600;
            color: #8B4513;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            transition: transform 0.2s ease;
        }

        .tool-item:hover {
            transform: translateY(-3px);
        }
        """

        with gr.Blocks(title="Aivo数字人 V3", css=custom_css) as interface:

            # 顶部横幅
            gr.HTML("""
            <div class="hero-section">
                <div class="hero-title">🤖 Aivo 数字人 V3</div>
                <div class="hero-subtitle">
                    智能对话 · 2D动画 · 9种工具 · 8种音色 · 语音输入
                </div>
            </div>
            """)

            with gr.Row():
                # 左侧：对话区
                with gr.Column(scale=2):
                    chatbot = gr.Chatbot(
                        label="💬 对话历史",
                        height=500,
                        show_label=True,
                        avatar_images=("🧑", "🤖")
                    )

                    # 文本输入区
                    with gr.Row():
                        msg_input = gr.Textbox(
                            label="",
                            placeholder="💭 输入消息或使用语音输入...",
                            scale=5,
                            show_label=False,
                            container=False
                        )
                        send_btn = gr.Button("📤 发送", variant="primary", scale=1)

                    # 语音输入区
                    with gr.Row():
                        audio_input = gr.Audio(
                            label="🎤 语音输入",
                            sources=["microphone", "upload"],
                            type="filepath",
                            show_label=False
                        )
                        process_audio_btn = gr.Button("🎙️ 识别语音", variant="secondary")

                    # 控制按钮
                    with gr.Row():
                        clear_btn = gr.Button("🗑️ 清空历史", size="sm")
                        recognized_text = gr.Textbox(
                            label="识别结果",
                            placeholder="语音识别的文本会显示在这里...",
                            interactive=False,
                            scale=3
                        )

                    # 语音输出
                    audio_output = gr.Audio(
                        label="🔊 Aivo的语音回复",
                        autoplay=True,
                        show_label=True
                    )

                # 右侧：数字人和设置
                with gr.Column(scale=1):
                    # 数字人动画
                    gr.Markdown("### 💫 数字人")
                    avatar_display = gr.HTML(
                        self._get_avatar_svg("neutral", False),
                        elem_classes="avatar-container"
                    )

                    # 统计面板
                    stats_display = gr.HTML(self._format_stats())

                    # 音色选择
                    with gr.Accordion("🎵 音色选择", open=True):
                        voice_selector = gr.Dropdown(
                            choices=[
                                "冰糖 (女声-活泼)",
                                "茉莉 (女声-温柔)",
                                "苏打 (男声-沉稳)",
                                "白桦 (男声-阳光)",
                                "Mia (英文女声)",
                                "Chloe (英文女声)",
                                "Milo (英文男声)",
                                "Dean (英文男声)"
                            ],
                            value="冰糖 (女声-活泼)",
                            label="选择音色",
                            info="不同场景使用不同音色"
                        )

                    # 工具列表
                    with gr.Accordion("🛠️ 可用工具 (9个)", open=False):
                        gr.HTML("""
                        <div class="tool-grid">
                            <div class="tool-item">🌤️ 天气</div>
                            <div class="tool-item">⏰ 时间</div>
                            <div class="tool-item">🔢 计算</div>
                            <div class="tool-item">🔍 搜索</div>
                            <div class="tool-item">⏱️ 提醒</div>
                            <div class="tool-item">📰 新闻</div>
                            <div class="tool-item">🌐 翻译</div>
                            <div class="tool-item">📚 维基</div>
                            <div class="tool-item">📝 笔记</div>
                        </div>
                        <div style="margin-top: 15px; padding: 12px; background: #f0f0f0; border-radius: 10px;">
                            <b>使用示例：</b><br>
                            • "北京今天天气怎么样？"<br>
                            • "提醒我明天开会"<br>
                            • "帮我翻译 hello world"<br>
                            • "搜索人工智能的最新进展"
                        </div>
                        """)

                    # 快速示例
                    with gr.Accordion("💡 快速示例", open=False):
                        examples = gr.Examples(
                            examples=[
                                ["你好，我是小明"],
                                ["北京今天天气怎么样？"],
                                ["帮我翻译：人工智能"],
                                ["提醒我1小时后开会"],
                                ["搜索一下机器学习"],
                                ["现在几点了？"],
                                ["帮我记笔记：明天交报告"]
                            ],
                            inputs=msg_input,
                            label=""
                        )

            # 底部信息
            gr.Markdown("""
            <div style="text-align: center; margin-top: 30px; padding: 20px; background: linear-gradient(135deg, #667eea22 0%, #764ba222 100%); border-radius: 15px;">
                <b>✨ 特性</b>：9个实用工具 | 8种音色选择 | 实时2D动画 | 语音输入输出<br>
                <small style="color: #666;">Powered by MiMo API | Built with ❤️ by Aivo Team</small>
            </div>
            """)

            # 事件绑定
            def extract_voice_name(voice_choice):
                """从选择中提取音色名称"""
                return voice_choice.split(" (")[0]

            # 文本消息发送
            send_btn.click(
                fn=lambda msg, hist, voice: self.chat(msg, hist, extract_voice_name(voice)),
                inputs=[msg_input, chatbot, voice_selector],
                outputs=[chatbot, audio_output, avatar_display, stats_display]
            ).then(
                fn=lambda: "",
                outputs=msg_input
            )

            msg_input.submit(
                fn=lambda msg, hist, voice: self.chat(msg, hist, extract_voice_name(voice)),
                inputs=[msg_input, chatbot, voice_selector],
                outputs=[chatbot, audio_output, avatar_display, stats_display]
            ).then(
                fn=lambda: "",
                outputs=msg_input
            )

            # 语音输入处理
            process_audio_btn.click(
                fn=lambda audio, hist, voice: self.process_audio_input(audio, hist, extract_voice_name(voice)),
                inputs=[audio_input, chatbot, voice_selector],
                outputs=[chatbot, audio_output, avatar_display, stats_display, recognized_text]
            )

            # 清空历史
            clear_btn.click(
                fn=self.clear_history,
                outputs=[chatbot, audio_output, avatar_display, stats_display]
            )

        return interface


def main():
    """启动Web界面"""
    print("=" * 60)
    print("🚀 Aivo Web界面 V3 启动中...")
    print("=" * 60)
    print("\n特性：")
    print("  ✓ 2D数字人动画（口型+表情）")
    print("  ✓ 9个实用工具")
    print("  ✓ 8种音色选择")
    print("  ✓ 语音输入输出")
    print("\n" + "=" * 60)

    # 创建UI实例
    ui = AivoWebUIV3()
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
