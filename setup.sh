#!/bin/bash
# 初始化脚本 - 首次设置时使用

echo "========================================="
echo "资产监控系统 - 首次配置脚本"
echo "========================================="
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 未安装，请先安装 Python 3.8+"
    exit 1
fi

echo "✓ Python 3 已安装"
echo ""

# 安装依赖
echo "📦 正在安装 Python 依赖..."
pip3 install -r requirements.txt

echo ""
echo "========================================="
echo "✓ 初始化完成！"
echo "========================================="
echo ""
echo "📖 后续步骤："
echo ""
echo "1️⃣  配置环境变量（选择一种方式）："
echo "   - 本地运行：创建 .env 文件，参考 config.example.json"
echo "   - GitHub Actions：在 Settings → Secrets 中配置"
echo ""
echo "2️⃣  修改配置文件："
echo "   - usd1_push.py：修改 WALLETS 和 SHEET_URL"
echo "   - update_apy.py：修改 WALLETS 和 SHEET_URL"
echo ""
echo "3️⃣  本地测试："
echo "   - python3 usd1_push.py"
echo "   - python3 update_apy.py"
echo ""
echo "4️⃣  上传到 GitHub："
echo "   - git init"
echo "   - git add ."
echo "   - git commit -m 'Initial commit'"
echo "   - git push"
echo ""
echo "📝 详细说明请查看 README.md"
echo ""
