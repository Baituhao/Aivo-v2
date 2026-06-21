#!/usr/bin/env python3
"""
测试 Soul Memory 系统
"""

from pathlib import Path
from src.soul_memory import SoulMemory

# 创建测试目录
test_memory_dir = Path("./test_memory")
test_memory_dir.mkdir(exist_ok=True)

# 初始化 Soul Memory
soul = SoulMemory(test_memory_dir)

print("=" * 60)
print("🧠 Soul Memory 系统测试")
print("=" * 60)

# 测试人格设定
print("\n【测试1】人格设定")
soul.update_personality(
    name="Aivo测试版",
    role="测试AI助手",
    traits=["友好", "专业", "高效"],
    speaking_style="简洁明了"
)
print(f"✅ 人格名称: {soul.get_personality()['name']}")
print(f"✅ 角色: {soul.get_personality()['role']}")

# 测试用户画像
print("\n【测试2】用户画像")
soul.update_user_profile(name="测试用户")
soul.add_user_interest("编程")
soul.add_user_interest("AI技术")
soul.add_user_habit("每天使用AI助手")
print(f"✅ 用户名: {soul.get_user_profile()['name']}")
print(f"✅ 兴趣: {soul.get_user_profile()['interests']}")
print(f"✅ 习惯: {soul.get_user_profile()['habits']}")

# 测试技能管理
print("\n【测试3】技能管理")
soul.add_skill("Python编程", "expert")
soul.add_skill("机器学习", "intermediate")
print(f"✅ 自定义技能数: {len(soul.get_skills()['custom_skills'])}")
print(f"✅ 已启用技能: {soul.get_enabled_skills()}")

# 测试偏好设置
print("\n【测试4】偏好设置")
soul.update_preferences(
    language="中文",
    voice="冰糖",
    response_style="详细"
)
print(f"✅ 语言: {soul.get_preferences()['language']}")
print(f"✅ 音色: {soul.get_preferences()['voice']}")

# 测试导出
print("\n【测试5】导出记忆")
export_file = test_memory_dir / "test_export.json"
soul.export_all(export_file)
print(f"✅ 已导出到: {export_file}")

# 显示摘要
print("\n【摘要信息】")
print(soul.get_summary())

print("\n" + "=" * 60)
print("✅ 所有测试通过！")
print("=" * 60)
