#!/bin/bash
# 快速启动脚本 V6

echo "╔══════════════════════════════════════════════════════════╗"
echo "║          Aivo 数字人系统 V6                              ║"
echo "║  🎀 Live2D | 🎵 气泡语音 | 🎤 豆包录音 | 🔴 实时对话   ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "选择运行模式："
echo "1. 🌟 Web界面V6（最新）- 气泡语音+豆包录音+实时对话"
echo "2. 🎀 Web界面V5 - Live2D版"
echo "3. 🎨 Web界面V4 - 精美卡通"
echo "4. 🌐 Web界面V3 - SVG动画"
echo "5. 💬 文本对话（9个工具）"
echo "6. 🎤 语音对话（9个工具）"
echo "7. 🧪 运行测试"
echo "8. 🆕 测试新工具"
echo ""
read -p "请输入选项 (1-8): " choice

case $choice in
    1)
        echo ""
        echo "🚀 启动Web界面V6..."
        echo "  ✓ 语音回复内嵌在对话气泡"
        echo "  ✓ 豆包风格录音按钮"
        echo "  ✓ 实时对话模式"
        echo "  ✓ Live2D数字人"
        echo ""
        python src/web_ui_v6.py
        ;;
    2)
        echo ""
        echo "🚀 启动Web界面V5（Live2D版）..."
        python src/web_ui_v5_live2d.py
        ;;
    3)
        echo ""
        echo "🚀 启动Web界面V4（卡通版）..."
        python src/web_ui_v4.py
        ;;
    4)
        echo ""
        echo "🚀 启动Web界面V3（SVG版）..."
        python src/web_ui_v3.py
        ;;
    5)
        echo ""
        echo "启动文本对话模式..."
        python src/main_v2.py --mode text
        ;;
    6)
        read -p "录音时长（秒，默认5）: " duration
        duration=${duration:-5}
        python src/main_v2.py --mode voice --duration $duration
        ;;
    7)
        echo "运行测试..."
        python tests/test_tools.py
        echo ""
        python tests/test_mimo_llm.py
        ;;
    8)
        echo "测试新工具..."
        python tests/test_new_tools.py
        ;;
    *)
        echo "❌ 无效选项"
        ;;
esac

echo "╔══════════════════════════════════════════════════════════╗"
echo "║          Aivo 数字人系统 V5                              ║"
echo "║  🎀 Live2D | 👄 口型同步 | 🛠️ 9工具 | 🎵 8音色         ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "选择运行模式："
echo "1. 🌟 Web界面V5（推荐）- 专业Live2D模型"
echo "2. 🎨 Web界面V4 - 精美卡通+对口型"
echo "3. 🌐 Web界面V3 - SVG动画版"
echo "4. 📱 Web界面V2 - 经典版"
echo "5. 💬 文本对话（支持9个工具）"
echo "6. 🎤 语音对话（支持9个工具）"
echo "7. 🧪 运行测试"
echo "8. 🆕 测试新工具"
echo ""
read -p "请输入选项 (1-8): " choice

case $choice in
    1)
        echo ""
        echo "🚀 启动Web界面V5（Live2D版）..."
        echo "✨ 特性："
        echo "  ✓ 专业Live2D模型（开源）"
        echo "  ✓ 自动口型同步"
        echo "  ✓ 丰富的表情和动作"
        echo "  ✓ 可点击互动"
        echo "  ✓ 9个实用工具"
        echo "  ✓ 8种音色选择"
        echo ""
        echo "💡 提示："
        echo "  - 播放语音时，Live2D会自动说话"
        echo "  - 点击Live2D可以触发互动"
        echo ""
        echo "浏览器将自动打开 http://localhost:7860"
        echo ""
        python src/web_ui_v5_live2d.py
        ;;
    2)
        echo ""
        echo "🚀 启动Web界面V4（卡通版）..."
        echo "浏览器将自动打开 http://localhost:7860"
        echo ""
        python src/web_ui_v4.py
        ;;
    3)
        echo ""
        echo "🚀 启动Web界面V3（SVG动画版）..."
        echo "浏览器将自动打开 http://localhost:7860"
        echo ""
        python src/web_ui_v3.py
        ;;
    4)
        echo ""
        echo "🚀 启动Web界面V2（经典版）..."
        echo "浏览器将自动打开 http://localhost:7860"
        echo ""
        python src/web_ui.py
        ;;
    5)
        echo ""
        echo "启动文本对话模式..."
        echo "可用工具：天气、时间、计算、搜索、提醒、新闻、翻译、维基、笔记"
        echo ""
        python src/main_v2.py --mode text
        ;;
    6)
        read -p "录音时长（秒，默认5）: " duration
        duration=${duration:-5}
        echo "启动语音对话模式（支持9个工具）..."
        python src/main_v2.py --mode voice --duration $duration
        ;;
    7)
        echo "运行测试..."
        echo ""
        echo "【测试1：工具系统】"
        python tests/test_tools.py
        echo ""
        echo "【测试2：LLM能力】"
        python tests/test_mimo_llm.py
        ;;
    8)
        echo "测试新工具（提醒、翻译、维基、笔记、新闻）..."
        python tests/test_new_tools.py
        ;;
    *)
        echo "❌ 无效选项"
        ;;
esac
