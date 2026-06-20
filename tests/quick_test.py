#!/usr/bin/env python3
"""
快速测试：验证MiMo API是否可用
"""

import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("MIMO_API_KEY"),
    base_url="https://token-plan-cn.xiaomimimo.com/v1"
)

print("测试MiMo API连接...")

try:
    completion = client.chat.completions.create(
        model="mimo-v2.5-pro",
        messages=[
            {
                "role": "system",
                "content": "You are MiMo, an AI assistant developed by Xiaomi."
            },
            {
                "role": "user",
                "content": "请用一句话介绍你自己"
            }
        ],
        max_completion_tokens=1024,
        temperature=1.0,
        top_p=0.95
    )

    print("✓ 连接成功！")
    print(f"回复: {completion.choices[0].message.content}")

except Exception as e:
    print(f"✗ 连接失败: {e}")
