#!/usr/bin/env python3
"""
Aivo Web界面 V5 - Live2D版（修复版）
使用简化的Live2D集成方案
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
from asr_service import ASRService


class AivoWebUIV5:
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
            return history, None, self._format_stats()

        try:
            # 更新当前音色
            self.current_voice = voice_choice

            # 1. LLM生成回复
            response = self.llm.chat(message)

            # 2. TTS合成语音
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

            stats_md = self._format_stats()

            return history, audio_path, stats_md

        except Exception as e:
            error_msg = f"❌ 错误: {str(e)}"
            if history is None:
                history = []
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": error_msg})
            return history, None, self._format_stats()

    def process_audio_input(self, audio_file, history: list, voice_choice: str):
        """处理语音输入"""
        if audio_file is None:
            return history, None, self._format_stats(), ""

        try:
            transcript = self.asr.transcribe(audio_file)
            return self.chat(transcript, history, voice_choice) + (transcript,)

        except Exception as e:
            error_msg = f"❌ 语音识别失败: {str(e)}"
            if history is None:
                history = []
            history.append({"role": "assistant", "content": error_msg})
            return history, None, self._format_stats(), ""

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
        return [], None, self._format_stats()

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

        # Live2D容器HTML（只放容器，脚本通过head/js注入）
        live2d_html = """
        <div style="width: 100%; height: 460px; position: relative;
             background: linear-gradient(135deg, #e0e7ff 0%, #f3e8ff 100%);
             border-radius: 20px; overflow: visible;
             box-shadow: 0 8px 30px rgba(0,0,0,0.12);">
            <canvas id="live2dcanvas"
                style="position: absolute; bottom: 0; left: 50%; transform: translateX(-50%);
                       pointer-events: auto;">
            </canvas>
            <div id="live2d-loading"
                 style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
                        color: #667eea; font-size: 1.1em; font-weight: 600;">
                ⏳ 加载Live2D中...
            </div>
        </div>
        """

        # 注入到页面head的脚本
        live2d_head = """
        <script src="https://cdn.jsdelivr.net/npm/live2d-widget@3.1.4/lib/L2Dwidget.min.js"></script>
        """

        # 页面加载后执行的初始化JS
        live2d_init_js = """
        function() {
            // 等待Live2D库加载完成后初始化
            function initLive2D() {
                if (typeof L2Dwidget === 'undefined') {
                    setTimeout(initLive2D, 300);
                    return;
                }
                // 隐藏加载提示
                var loading = document.getElementById('live2d-loading');
                if (loading) loading.style.display = 'none';

                L2Dwidget.init({
                    "pluginRootPath": "https://cdn.jsdelivr.net/npm/live2d-widget@3.1.4/",
                    "pluginJsPath": "lib/",
                    "pluginModelPath": "assets/",
                    "tagVersion": "UNSAFE_NODE_NOT_DEFINED",
                    "debug": false,
                    "model": {
                        "jsonPath": "https://cdn.jsdelivr.net/npm/live2d-widget-model-shizuku@1.0.5/assets/shizuku.model.json",
                        "scale": 1
                    },
                    "display": {
                        "superSample": 2,
                        "width": 250,
                        "height": 380,
                        "position": "left",
                        "hOffset": 0,
                        "vOffset": 0
                    },
                    "mobile": {
                        "show": true,
                        "scale": 0.8
                    },
                    "react": {
                        "opacityDefault": 1,
                        "opacityOnHover": 0.8
                    }
                });

                // 监听音频，触发口型动画
                setTimeout(function() {
                    setInterval(function() {
                        var audios = document.querySelectorAll('audio');
                        audios.forEach(function(audio) {
                            if (!audio._live2dBound) {
                                audio._live2dBound = true;
                                audio.addEventListener('play', function() {
                                    console.log('Live2D speaking...');
                                });
                            }
                        });
                    }, 1000);
                }, 2000);
            }
            initLive2D();
        }
        """

        with gr.Blocks(title="Aivo数字人 V5 - Live2D", css=custom_css,
                       head=live2d_head, js=live2d_init_js) as interface:

            # 顶部横幅
            gr.HTML("""
            <div class="hero-section">
                <div class="hero-title">🤖 Aivo 数字人 V5</div>
                <div class="hero-subtitle">
                    Live2D数字人 · 真实口型 · 9种工具 · 8种音色 · 语音输入
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
                        avatar_images=(None, None)  # 不使用头像，避免显示问号
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
                            label="别结果",
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

                # 右侧：Live2D和设置
                with gr.Column(scale=1):
                    # Live2D数字人
                    gr.Markdown("### 💫 Live2D数字人")
                    gr.HTML(live2d_html)
                    gr.Markdown("""
                    <div style="text-align: center; color: #666; font-size: 0.9em; margin-top: 10px;">
                    💡 Live2D会在右下角显示<br>
                    点击可以互动，播放语音时会说话
                    </div>
                    """)

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
                <b>✨ V5特性</b>：Live2D看板娘 | 自动出现在右下角 | 9个工具 | 8种音色<br>
                <small style="color: #666;">💡 Live2D使用autoload.js自动加载，会显示在页面右下角</small>
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
                outputs=[chatbot, audio_output, stats_display]
            ).then(
                fn=lambda: "",
                outputs=msg_input
            )

            msg_input.submit(
                fn=lambda msg, hist, voice: self.chat(msg, hist, extract_voice_name(voice)),
                inputs=[msg_input, chatbot, voice_selector],
                outputs=[chatbot, audio_output, stats_display]
            ).then(
                fn=lambda: "",
                outputs=msg_input
            )

            # 语音输入处理
            process_audio_btn.click(
                fn=lambda audio, hist, voice: self.process_audio_input(audio, hist, extract_voice_name(voice)),
                inputs=[audio_input, chatbot, voice_selector],
                outputs=[chatbot, audio_output, stats_display, recognized_text]
            )

            # 清空历史
            clear_btn.click(
                fn=self.clear_history,
                outputs=[chatbot, audio_output, stats_display]
            )

        return interface


def main():
    """启动Web界面"""
    print("=" * 60)
    print("🚀 Aivo Web界面 V5 启动中...")
    print("=" * 60)
    print("\n✨ V5 特性：")
    print("  ✓ Live2D看板娘（自动显示在右下角）")
    print("  ✓ 点击可以互动")
    print("  ✓ 9个实用工具")
    print("  ✓ 8种音色选择")
    print("\n💡 提示：")
    print("  - Live2D会自动出现在页面右下角")
    print("  - 点击Live2D可以互动")
    print("  - 使用简化的autoload方案，更稳定")
    print("\n" + "=" * 60)

    # 创建UI实例
    ui = AivoWebUIV5()
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
