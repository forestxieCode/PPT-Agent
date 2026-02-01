#!/bin/bash
# PPT-Agent 快速运行脚本
# Quick start script for PPT-Agent (Linux/macOS)

echo ""
echo "========================================================================"
echo "                    PPT-Agent 快速运行脚本"
echo "========================================================================"
echo ""

# 设置PYTHONPATH
export PYTHONPATH=$(pwd)

echo "[1/4] 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "✗ Python未安装"
    exit 1
fi
python3 --version
echo "✓ Python环境正常"

echo ""
echo "[2/4] 检查依赖包..."
if ! python3 -c "import pptx, click, rich, pydantic, loguru" 2>/dev/null; then
    echo "⚠ 缺少依赖包，正在安装..."
    pip3 install -r requirements.txt
else
    echo "✓ 依赖包完整"
fi

echo ""
echo "[3/4] 可用的命令："
echo ""
echo "  1. 查看所有模板"
echo "  2. 生成PPT（使用Mock LLM演示）"
echo "  3. 运行测试"
echo "  4. 打开CLI帮助"
echo "  5. 退出"
echo ""

read -p "请选择操作 (1-5): " choice

case $choice in
    1)
        echo ""
        echo "提示：此命令需要配置API密钥，当前使用Mock模式"
        echo ""
        python3 -c "from src.template.loader import TemplateLoader; loader = TemplateLoader(); templates = loader.list_templates(); [print(f'• {t[\"template_id\"]}: {t[\"template_name\"]}') for t in templates]"
        ;;
    2)
        echo ""
        echo "正在使用Mock LLM生成演示PPT..."
        echo ""
        python3 examples/full_ppt_generation.py
        echo ""
        echo "✓ PPT已生成到 output/ 目录"
        ;;
    3)
        echo ""
        echo "运行测试套件..."
        pytest tests/ -v
        ;;
    4)
        echo ""
        python3 -m src.cli --help
        ;;
    5)
        echo ""
        echo "再见！"
        exit 0
        ;;
    *)
        echo ""
        echo "✗ 无效选择"
        ;;
esac

echo ""
echo "[4/4] 完成！"
echo ""
echo "提示：配置API密钥后可使用完整功能"
echo "  编辑 .env 文件，添加："
echo "  OPENAI_API_KEY=sk-your-key"
echo "  或 DEEPSEEK_API_KEY=sk-your-key"
echo ""
