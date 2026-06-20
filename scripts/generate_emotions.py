#!/usr/bin/env python3
"""
生成简单的表情图片（占位符）

使用PIL生成基础表情图
"""

from PIL import Image, ImageDraw, ImageFont
import os


def create_emotion_image(emotion: str, emoji: str, color: tuple, output_path: str):
    """
    创建表情图片

    Args:
        emotion: 情感名称
        emoji: emoji表情
        color: 背景颜色
        output_path: 输出路径
    """
    # 创建图片
    width, height = 400, 400
    img = Image.new('RGB', (width, height), color=color)
    draw = ImageDraw.Draw(img)

    # 尝试使用系统字体
    try:
        font_large = ImageFont.truetype("/System/Library/Fonts/Apple Color Emoji.ttc", 150)
        font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 30)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # 绘制emoji（居中）
    bbox = draw.textbbox((0, 0), emoji, font=font_large)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) / 2
    y = (height - text_height) / 2 - 30
    draw.text((x, y), emoji, font=font_large, fill='white')

    # 绘制文字标签
    label = emotion.upper()
    bbox = draw.textbbox((0, 0), label, font=font_small)
    text_width = bbox[2] - bbox[0]
    x = (width - text_width) / 2
    y = height - 60
    draw.text((x, y), label, font=font_small, fill='white')

    # 保存
    img.save(output_path)
    print(f"✓ 生成表情图片: {output_path}")


def main():
    """生成所有表情图片"""
    print("=" * 60)
    print("生成表情图片")
    print("=" * 60)

    output_dir = "assets/emotions"
    os.makedirs(output_dir, exist_ok=True)

    emotions = [
        ("happy", "😊", (255, 193, 7)),      # 黄色 - 开心
        ("sad", "😢", (96, 125, 139)),        # 灰蓝 - 悲伤
        ("neutral", "😐", (158, 158, 158)),   # 灰色 - 中性
        ("surprised", "😲", (233, 30, 99))    # 粉红 - 惊讶
    ]

    for emotion, emoji, color in emotions:
        output_path = os.path.join(output_dir, f"{emotion}.png")
        create_emotion_image(emotion, emoji, color, output_path)

    print("\n✓ 所有表情图片生成完成")
    print(f"保存位置: {output_dir}/")


if __name__ == "__main__":
    main()
