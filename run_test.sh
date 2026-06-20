#!/bin/bash
# 快速测试脚本

echo "=== 安装依赖 ==="
pip install -q python-dotenv requests

echo ""
echo "=== 运行MiMo API测试 ==="
python tests/test_mimo_api.py

echo ""
echo "测试完成！请查看上面的结果。"
