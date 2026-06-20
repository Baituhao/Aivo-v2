#!/usr/bin/env python3
"""
Aivo Web界面 V4 - 优化版
特性：
1. 更漂亮的2D数字人（卡通风格）
2. 真正的口型同步（跟随音频播放）
3. 8种音色选择
4. 9个工具支持
5. 语音输入功能
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


class AivoWebUIV4:
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

    def chat(self, message: str, history: list, voice_choice: str):
        """处理聊天消息"""
        if not message.strip():
            return history, None, self._get_avatar_html("neutral"), self._format_stats()

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

            # 5. 生成数字人HTML（带口型同步）
            avatar_html = self._get_avatar_html(response['emotion'])
            stats_md = self._format_stats()

            return history, audio_path, avatar_html, stats_md

        except Exception as e:
            error_msg = f"❌ 错误: {str(e)}"
            if history is None:
                history = []
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": error_msg})
            return history, None, self._get_avatar_html("sad"), self._format_stats()

    def process_audio_input(self, audio_file, history: list, voice_choice: str):
        """处理语音输入"""
        if audio_file is None:
            return history, None, self._get_avatar_html("neutral"), self._format_stats(), ""

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
            return history, None, self._get_avatar_html("sad"), self._format_stats(), ""

    def _get_avatar_html(self, emotion: str) -> str:
        """生成更漂亮的2D数字人HTML（带口型同步JS）"""

        # 表情配置
        emotions_config = {
            "happy": {
                "face_color": "#FFE5CC",
                "face_shadow": "#FFD4A3",
                "eye_color": "#8B4513",
                "mouth_path": "M80,120 Q90,128 100,120",
                "cheek_color": "#FFB6C1",
                "eyebrow_path": "M60,68 Q70,65 80,68"
            },
            "sad": {
                "face_color": "#E8D5C4",
                "face_shadow": "#D4BFA8",
                "eye_color": "#6B4423",
                "mouth_path": "M80,125 Q90,118 100,125",
                "cheek_color": "#D4A5A5",
                "eyebrow_path": "M60,70 Q70,73 80,70"
            },
            "neutral": {
                "face_color": "#FFE0B2",
                "face_shadow": "#FFCC80",
                "eye_color": "#5D4037",
                "mouth_path": "M80,120 L100,120",
                "cheek_color": "#FFCDD2",
                "eyebrow_path": "M60,68 L80,68"
            },
            "surprised": {
                "face_color": "#FFF3E0",
                "face_shadow": "#FFE0B2",
                "eye_color": "#4E342E",
                "mouth_path": "M90,125 m-8,0 a 8,8 0 1,0 16,0 a 8,8 0 1,0 -16,0",
                "cheek_color": "#FFCCBC",
                "eyebrow_path": "M60,62 Q70,58 80,62"
            }
        }

        config = emotions_config.get(emotion, emotions_config["neutral"])

        html = f"""
        <div style="position: relative; width: 100%; max-width: 350px; margin: 0 auto;">
            <svg id="aivoAvatar" width="100%" height="400" viewBox="0 0 200 240" xmlns="http://www.w3.org/2000/svg" style="filter: drop-shadow(0 10px 25px rgba(0,0,0,0.15));">
                <defs>
                    <!-- 渐变定义 -->
                    <radialGradient id="faceGradient" cx="50%" cy="40%">
                        <stop offset="0%" style="stop-color:{config['face_color']};stop-opacity:1" />
                        <stop offset="100%" style="stop-color:{config['face_shadow']};stop-opacity:1" />
                    </radialGradient>
                    <radialGradient id="hairGradient" cx="50%" cy="30%">
                        <stop offset="0%" style="stop-color:#6B4423;stop-opacity:1" />
                        <stop offset="100%" style="stop-color:#4A2C1A;stop-opacity:1" />
                    </radialGradient>
                    <linearGradient id="bodyGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
                        <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
                    </linearGradient>
                </defs>

                <!-- 背景光晕 -->
                <circle cx="100" cy="110" r="90" fill="url(#bodyGradient)" opacity="0.2"/>

                <!-- 身体 -->
                <ellipse cx="100" cy="200" rx="60" ry="40" fill="url(#bodyGradient)" opacity="0.9"/>
                <path d="M40,200 Q60,210 80,200" stroke="url(#bodyGradient)" stroke-width="20" fill="none" stroke-linecap="round"/>
                <path d="M120,200 Q140,210 160,200" stroke="url(#bodyGradient)" stroke-width="20" fill="none" stroke-linecap="round"/>

                <!-- 脖子 -->
                <rect x="85" y="165" width="30" height="35" fill="{config['face_shadow']}" rx="8"/>

                <!-- 头部 -->
                <ellipse cx="100" cy="100" rx="55" ry="65" fill="url(#faceGradient)" stroke="#D4A373" stroke-width="2"/>

                <!-- 头发 -->
                <path d="M45,85 Q50,35 100,30 Q150,35 155,85 Q155,60 145,50 Q135,40 125,35 Q115,32 100,30 Q85,32 75,35 Q65,40 55,50 Q45,60 45,85 Z"
                    fill="url(#hairGradient)" stroke="#3E2A1A" stroke-width="2"/>

                <!-- 刘海 -->
                <path d="M60,65 Q65,55 70,60 Q75,55 80,60 Q85,55 90,60 Q95,55 100,60 Q105,55 110,60 Q115,55 120,60 Q125,55 130,60 Q135,55 140,65"
                    fill="url(#hairGradient)" stroke="none"/>

                <!-- 耳朵 -->
                <ellipse cx="45" cy="105" rx="12" ry="18" fill="{config['face_shadow']}" stroke="#D4A373" stroke-width="1.5"/>
                <ellipse cx="155" cy="105" rx="12" ry="18" fill="{config['face_shadow']}" stroke="#D4A373" stroke-width="1.5"/>
                <ellipse cx="47" cy="108" rx="5" ry="7" fill="{config['face_color']}" opacity="0.6"/>
                <ellipse cx="153" cy="108" rx="5" ry="7" fill="{config['face_color']}" opacity="0.6"/>

                <!-- 眉毛 -->
                <g id="leftEyebrow">
                    <path d="{config['eyebrow_path']}" stroke="#4A2C1A" stroke-width="3.5" fill="none" stroke-linecap="round"/>
                </g>
                <g id="rightEyebrow" transform="translate(40,0)">
                    <path d="{config['eyebrow_path']}" stroke="#4A2C1A" stroke-width="3.5" fill="none" stroke-linecap="round"/>
                </g>

                <!-- 眼睛（左） -->
                <g id="leftEye">
                    <ellipse cx="75" cy="90" rx="12" ry="15" fill="white"/>
                    <circle cx="77" cy="92" r="8" fill="{config['eye_color']}"/>
                    <circle cx="79" cy="89" r="3" fill="black"/>
                    <circle cx="81" cy="87" r="2" fill="white" opacity="0.8"/>
                    <!-- 眨眼动画 -->
                    <animate attributeName="ry" values="15;0;15" dur="3s" repeatCount="indefinite"/>
                </g>

                <!-- 眼睛（右） -->
                <g id="rightEye">
                    <ellipse cx="125" cy="90" rx="12" ry="15" fill="white"/>
                    <circle cx="123" cy="92" r="8" fill="{config['eye_color']}"/>
                    <circle cx="121" cy="89" r="3" fill="black"/>
                    <circle cx="119" cy="87" r="2" fill="white" opacity="0.8"/>
                    <!-- 眨眼动画 -->
                    <animate attributeName="ry" values="15;0;15" dur="3s" begin="0.1s" repeatCount="indefinite"/>
                </g>

                <!-- 腮红 -->
                <ellipse cx="55" cy="110" rx="12" ry="8" fill="{config['cheek_color']}" opacity="0.5"/>
                <ellipse cx="145" cy="110" rx="12" ry="8" fill="{config['cheek_color']}" opacity="0.5"/>

                <!-- 鼻子 -->
                <ellipse cx="100" cy="108" rx="4" ry="6" fill="{config['face_shadow']}" opacity="0.3"/>
                <path d="M98,110 L95,115" stroke="{config['face_shadow']}" stroke-width="1.5" stroke-linecap="round"/>

                <!-- 嘴巴（会动画） -->
                <g id="mouth">
                    <path id="mouthPath" d="{config['mouth_path']}" stroke="#D2691E" stroke-width="3" fill="none" stroke-linecap="round"/>
                </g>

                <!-- 说话时的音波效果（默认隐藏） -->
                <g id="soundWaves" opacity="0">
                    <circle cx="170" cy="100" r="3" fill="#667eea">
                        <animate attributeName="r" values="3;12;3" dur="1s" repeatCount="indefinite"/>
                        <animate attributeName="opacity" values="0.7;0;0.7" dur="1s" repeatCount="indefinite"/>
                    </circle>
                    <circle cx="30" cy="100" r="3" fill="#667eea">
                        <animate attributeName="r" values="3;12;3" dur="1s" begin="0.3s" repeatCount="indefinite"/>
                        <animate attributeName="opacity" values="0.7;0;0.7" dur="1s" begin="0.3s" repeatCount="indefinite"/>
                    </circle>
                </g>
            </svg>
        </div>

        <script>
        // 口型同步JavaScript代码
        (function() {{
            let mouthOpenPath = "M80,120 Q90,135 100,120 Q100,130 90,135 Q90,130 80,120 Z";
            let mouthClosePath = "{config['mouth_path']}";
            let isAnimating = false;
            let animationInterval = null;

            // 监听页面上的audio元素
            function setupAudioListener() {{
                const audioElements = document.querySelectorAll('audio');
                audioElements.forEach(audio => {{
                    if (!audio.dataset.listenerAdded) {{
                        audio.dataset.listenerAdded = 'true';

                        audio.addEventListener('play', function() {{
                            startMouthAnimation();
                        }});

                        audio.addEventListener('pause', function() {{
                            stopMouthAnimation();
                        }});

                        audio.addEventListener('ended', function() {{
                            stopMouthAnimation();
                        }});
                    }}
                }});
            }}

            function startMouthAnimation() {{
                if (isAnimating) return;
                isAnimating = true;

                const mouthPath = document.getElementById('mouthPath');
                const soundWaves = document.getElementById('soundWaves');

                if (soundWaves) {{
                    soundWaves.setAttribute('opacity', '1');
                }}

                let isOpen = false;
                animationInterval = setInterval(() => {{
                    if (mouthPath) {{
                        isOpen = !isOpen;
                        mouthPath.setAttribute('d', isOpen ? mouthOpenPath : mouthClosePath);
                    }}
                }}, 150); // 每150ms切换一次（模拟说话）
            }}

            function stopMouthAnimation() {{
                isAnimating = false;
                if (animationInterval) {{
                    clearInterval(animationInterval);
                    animationInterval = null;
                }}

                const mouthPath = document.getElementById('mouthPath');
                const soundWaves = document.getElementById('soundWaves');

                if (mouthPath) {{
                    mouthPath.setAttribute('d', mouthClosePath);
                }}
                if (soundWaves) {{
                    soundWaves.setAttribute('opacity', '0');
                }}
            }}

            // 定期检查新的audio元素
            setInterval(setupAudioListener, 500);
            setupAudioListener();
        }})();
        </script>
        """

        return html

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
        return [], None, self._get_avatar_html("neutral"), self._format_stats()

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

        with gr.Blocks(title="Aivo数人 V4", css=custom_css) as interface:

            # 顶部横幅
            gr.HTML("""
            <div class="hero-section">
                <div class="hero-title">🤖 Aivo 数字人 V4</div>
                <div class="hero-subtitle">
                    精美卡通 · 口型同步 · 9种工具 · 8种音色 · 语音输入
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
                        label="🔊 Aivo的语音回复（播放时会自动对口型）",
                        autoplay=True,
                        show_label=True
                    )

                # 右侧：数字人和设置
                with gr.Column(scale=1):
                    # 数字人动画
                    gr.Markdown("### 💫 数字人（自动对口型）")
                    avatar_display = gr.HTML(
                        self._get_avatar_html("neutral"),
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
                <b>✨ V4特性</b>：精美卡通数字人 | 自动对口型 | 9个实用工具 | 8种音色<br>
                <small style="color: #666;">💡 播放语音时，数字人会自动张嘴说话哦！</small>
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
    print("🚀 Aivo Web界面 V4 启动中...")
    print("=" * 60)
    print("\n✨ V4 新特性：")
    print("  ✓ 精美卡通数字人（更好看）")
    print("  ✓ 自动对口型（跟随语音播放）")
    print("  ✓ 9个实用工具")
    print("  ✓ 8种音色选择")
    print("  ✓ 语音输入输出")
    print("\n💡 提示：播放语音时，数字人会自动张嘴说话！")
    print("\n" + "=" * 60)

    # 创建UI实例
    ui = AivoWebUIV4()
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
