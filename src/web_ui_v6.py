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

sys.path.insert(0, os.path.dirname(__file__))

from llm_service_v2 import LLMServiceWithTools
from tts_service import TTSService
from voice_manager import VoiceManager
from asr_service import ASRService

# live2d.html的绝对路径
STATIC_DIR = Path(__file__).parent / "static"
LIVE2D_HTML = STATIC_DIR / "live2d.html"


class AivoWebUIV6:
    def __init__(self):
        self.llm = LLMServiceWithTools()
        self.tts = TTSService()
        self.voice_manager = VoiceManager()
        self.asr = ASRService()
        self.current_voice = "冰糖"
        self.stats = {
            "conversation_count": 0,
            "tool_calls": 0,
            "emotion_changes": 0,
            "last_emotion": "neutral"
        }

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

            # 更新统计
            self.stats['conversation_count'] += 1
            if response['emotion'] != self.stats['last_emotion']:
                self.stats['emotion_changes'] += 1
                self.stats['last_emotion'] = response['emotion']

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

    def _format_stats(self) -> str:
        """格式化统计信息"""
        return f"""
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:16px 0;">
            <div style="background:linear-gradient(135deg,#667eea,#764ba2);padding:16px;
                border-radius:16px;text-align:center;color:white;
                box-shadow:0 6px 20px rgba(102,126,234,0.3);
                transform:perspective(1000px) rotateX(2deg);
                transition:transform 0.3s ease;">
                <div style="font-size:2em;margin-bottom:4px;">💬</div>
                <div style="font-size:2em;font-weight:900;margin:8px 0;
                    text-shadow:2px 2px 4px rgba(0,0,0,0.2);">{self.stats['conversation_count']}</div>
                <div style="font-size:0.8em;opacity:0.95;font-weight:600;">对话轮数</div>
            </div>
            <div style="background:linear-gradient(135deg,#f093fb,#f5576c);padding:16px;
                border-radius:16px;text-align:center;color:white;
                box-shadow:0 6px 20px rgba(240,147,251,0.3);
                transform:perspective(1000px) rotateX(2deg);
                transition:transform 0.3s ease;">
                <div style="font-size:2em;margin-bottom:4px;">🔧</div>
                <div style="font-size:2em;font-weight:900;margin:8px 0;
                    text-shadow:2px 2px 4px rgba(0,0,0,0.2);">{self.stats['tool_calls']}</div>
                <div style="font-size:0.8em;opacity:0.95;font-weight:600;">工具调用</div>
            </div>
            <div style="background:linear-gradient(135deg,#4facfe,#00f2fe);padding:16px;
                border-radius:16px;text-align:center;color:white;
                box-shadow:0 6px 20px rgba(79,172,254,0.3);
                transform:perspective(1000px) rotateX(2deg);
                transition:transform 0.3s ease;">
                <div style="font-size:2em;margin-bottom:4px;">🎭</div>
                <div style="font-size:2em;font-weight:900;margin:8px 0;
                    text-shadow:2px 2px 4px rgba(0,0,0,0.2);">{self.stats['emotion_changes']}</div>
                <div style="font-size:0.8em;opacity:0.95;font-weight:600;">情感切换</div>
            </div>
        </div>"""

    def clear_history(self):
        """清空对话历史"""
        self.llm.clear_history()
        self.stats = {
            "conversation_count": 0,
            "tool_calls": 0,
            "emotion_changes": 0,
            "last_emotion": "neutral"
        }
        return [], self._format_stats()

    def _get_live2d_html(self) -> str:
        """使用iframe srcdoc嵌入Live2D"""
        # 读取完整的HTML文件
        with open(LIVE2D_HTML, 'r', encoding='utf-8') as f:
            html_content = f.read()

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
        """

        with gr.Blocks(title="Aivo V6") as interface:

            # 顶部横幅 - V6版本特色
            gr.HTML("""
            <div style="text-align:center;padding:40px 20px;margin-bottom:30px;
                background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
                border-radius:24px;box-shadow:0 12px 40px rgba(102,126,234,0.5);
                position:relative;overflow:hidden;">
                <div style="position:absolute;top:-50%;right:-5%;width:300px;height:300px;
                    background:radial-gradient(circle,rgba(255,255,255,0.1),transparent);
                    border-radius:50%;"></div>
                <div style="position:relative;z-index:1;">
                    <div style="font-size:3.2em;font-weight:900;color:white;
                        text-shadow:3px 3px 8px rgba(0,0,0,0.3);
                        letter-spacing:-1px;">
                        🎀 Aivo 数字人 V6
                    </div>
                    <div style="color:rgba(255,255,255,0.95);margin-top:12px;
                        font-size:1.2em;font-weight:600;letter-spacing:0.5px;">
                        ✨ Live2D交互 · 🎵 气泡语音 · 🛠️ 9种工具 · 🎤 8种音色
                    </div>
                    <div style="margin-top:16px;padding:8px 20px;
                        background:rgba(255,255,255,0.2);border-radius:20px;
                        display:inline-block;backdrop-filter:blur(10px);">
                        <span style="color:white;font-size:0.95em;font-weight:500;">
                            🆕 语音内嵌对话气泡 | 点击Live2D切换模型
                        </span>
                    </div>
                </div>
            </div>
            """)

            with gr.Row():
                # 左侧：对话区
                with gr.Column(scale=2):
                    chatbot = gr.Chatbot(
                        label="💬 对话历史",
                        height=520,
                        show_label=True,
                        avatar_images=(None, None)
                    )

                    # 文本输入
                    with gr.Row():
                        msg_input = gr.Textbox(
                            label="",
                            placeholder="💭 输入消息或使用语音输入...",
                            scale=5,
                            show_label=False,
                            container=False
                        )
                        send_btn = gr.Button("📤 发送", variant="primary", scale=1)

                    # 语音输入
                    with gr.Row():
                        audio_input = gr.Audio(
                            label="🎤 语音输入",
                            sources=["microphone", "upload"],
                            type="filepath",
                            show_label=True
                        )
                        voice_btn = gr.Button("🎙️ 识别语音", variant="secondary")

                    # 识别结果和清空按钮
                    with gr.Row():
                        recognized_text = gr.Textbox(
                            label="识别结果",
                            placeholder="语音识别的文本会显示在这里...",
                            interactive=False,
                            scale=4
                        )
                        clear_btn = gr.Button("🗑️ 清空历史", size="sm", scale=1)

                # 右侧：Live2D和设置
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

                    # 工具列表
                    with gr.Accordion("🛠️ 可用工具", open=False):
                        gr.HTML("""
                        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;">
                            <div style="background:linear-gradient(135deg,#ffecd2,#fcb69f);
                                padding:10px;border-radius:10px;text-align:center;font-weight:600;color:#8B4513;">
                                🌤️ 天气
                            </div>
                            <div style="background:linear-gradient(135deg,#ffecd2,#fcb69f);
                                padding:10px;border-radius:10px;text-align:center;font-weight:600;color:#8B4513;">
                                ⏰ 时间
                            </div>
                            <div style="background:linear-gradient(135deg,#ffecd2,#fcb69f);
                                padding:10px;border-radius:10px;text-align:center;font-weight:600;color:#8B4513;">
                                🔢 计算
                            </div>
                            <div style="background:linear-gradient(135deg,#ffecd2,#fcb69f);
                                padding:10px;border-radius:10px;text-align:center;font-weight:600;color:#8B4513;">
                                🔍 搜索
                            </div>
                            <div style="background:linear-gradient(135deg,#ffecd2,#fcb69f);
                                padding:10px;border-radius:10px;text-align:center;font-weight:600;color:#8B4513;">
                                ⏱️ 提醒
                            </div>
                            <div style="background:linear-gradient(135deg,#ffecd2,#fcb69f);
                                padding:10px;border-radius:10px;text-align:center;font-weight:600;color:#8B4513;">
                                📰 新闻
                            </div>
                            <div style="background:linear-gradient(135deg,#ffecd2,#fcb69f);
                                padding:10px;border-radius:10px;text-align:center;font-weight:600;color:#8B4513;">
                                🌐 翻译
                            </div>
                            <div style="background:linear-gradient(135deg,#ffecd2,#fcb69f);
                                padding:10px;border-radius:10px;text-align:center;font-weight:600;color:#8B4513;">
                                📚 维基
                            </div>
                            <div style="background:linear-gradient(135deg,#ffecd2,#fcb69f);
                                padding:10px;border-radius:10px;text-align:center;font-weight:600;color:#8B4513;">
                                📝 笔记
                            </div>
                        </div>
                        """)

                    # 快速示例
                    with gr.Accordion("💡 快速示例", open=False):
                        gr.Examples(
                            examples=[
                                ["你好，我是小明"],
                                ["北京今天天气怎么样？"],
                                ["帮我翻译：人工智能"],
                                ["提醒我1小时后开会"],
                                ["搜索一下机器学习"],
                                ["现在几点了？"],
                                ["帮我记笔记：明天交报告"]
                            ],
                            inputs=msg_input
                        )

            # 底部信息 - 更有特色
            gr.Markdown("""
            <div style="text-align:center;margin-top:30px;padding:24px;
                background:linear-gradient(135deg,#e0e7ff,#f3e8ff);
                border-radius:20px;border:2px solid #c7d2fe;">
                <div style="font-size:1.2em;font-weight:700;color:#5b21b6;margin-bottom:12px;">
                    ✨ Aivo V6 核心特性
                </div>
                <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-top:16px;">
                    <div style="background:white;padding:12px;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
                        <div style="font-size:1.5em;margin-bottom:4px;">🎀</div>
                        <div style="font-weight:600;color:#4338ca;">Live2D数字人</div>
                        <div style="font-size:0.85em;color:#64748b;">可点击切换模型</div>
                    </div>
                    <div style="background:white;padding:12px;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
                        <div style="font-size:1.5em;margin-bottom:4px;">🎵</div>
                        <div style="font-weight:600;color:#4338ca;">气泡语音</div>
                        <div style="font-size:0.85em;color:#64748b;">音频嵌入对话</div>
                    </div>
                    <div style="background:white;padding:12px;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
                        <div style="font-size:1.5em;margin-bottom:4px;">🛠️</div>
                        <div style="font-weight:600;color:#4338ca;">9种工具</div>
                        <div style="font-size:0.85em;color:#64748b;">天气·搜索·翻译等</div>
                    </div>
                    <div style="background:white;padding:12px;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
                        <div style="font-size:1.5em;margin-bottom:4px;">🎤</div>
                        <div style="font-weight:600;color:#4338ca;">8种音色</div>
                        <div style="font-size:0.85em;color:#64748b;">中英双语支持</div>
                    </div>
                </div>
                <div style="margin-top:16px;padding-top:16px;border-top:1px solid #e0e7ff;">
                    <small style="color:#6b7280;">
                        💡 提示：播放语音时Live2D会自动说话 | 支持语音输入和文本输入
                    </small>
                </div>
            </div>
            """)

            # 事件绑定
            send_btn.click(
                fn=self.chat,
                inputs=[msg_input, chatbot, voice_selector],
                outputs=[chatbot, stats_display]
            ).then(
                fn=lambda: f"speaking_{int(__import__('time').time() * 1000)}",  # 每次生成唯一值
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
                fn=lambda: f"speaking_{int(__import__('time').time() * 1000)}",  # 每次生成唯一值
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

            clear_btn.click(
                fn=self.clear_history,
                outputs=[chatbot, stats_display]
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
                    if (value === 'speaking') {
                        console.log('[Trigger] 设置5秒后自动停止');
                        setTimeout(function() {
                            console.log('[Trigger] 自动发送idle消息');
                            iframes.forEach(function(iframe) {
                                try {
                                    iframe.contentWindow.postMessage('idle', '*');
                                } catch(e) {}
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
    print("=" * 60)
    print("🚀 Aivo V6 启动中...")
    print("=" * 60)
    print("\n✨ V6 特性：")
    print("  ✓ Live2D数字人（iframe加载，可点击切换）")
    print("  ✓ 语音内嵌在对话气泡中（自动播放）")
    print("  ✓ 9个实用工具（天气/搜索/翻译等）")
    print("  ✓ 8种音色选择（中英双语）")
    print("  ✓ 全新UI设计（更美观易用）")
    print("\n💡 提示：")
    print("  - Live2D在右侧显示")
    print("  - 点击Live2D可以切换模型（3个模型循环）")
    print("  - 播放语音时Live2D会自动说话")
    print("  - 支持鼠标滚轮上下滚动浏览")
    print("\n" + "=" * 60)

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
