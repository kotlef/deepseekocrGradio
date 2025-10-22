#!/bin/bash

# DeepSeek-OCR Gradio应用启动脚本

echo "=========================================="
echo "DeepSeek-OCR Gradio应用启动脚本"
echo "=========================================="

# 检查conda环境
if ! command -v conda &> /dev/null; then
    echo "❌ 错误: 未找到conda命令"
    echo "请先安装Anaconda或Miniconda"
    exit 1
fi

# 激活conda环境
echo "激活conda环境: deepseek-ocr"
source $(conda info --base)/etc/profile.d/conda.sh
conda activate deepseek-ocr

if [ $? -ne 0 ]; then
    echo "❌ 错误: 无法激活conda环境 deepseek-ocr"
    echo "请先创建环境: conda create -n deepseek-ocr python=3.12"
    exit 1
fi

# 检查Python版本
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo "Python版本: $PYTHON_VERSION"

# 检查必要的包
echo "检查必要的Python包..."
python -c "import gradio" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ 错误: 未安装gradio"
    echo "请运行: pip install gradio"
    exit 1
fi

python -c "import torch" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ 错误: 未安装torch"
    echo "请运行: pip install torch"
    exit 1
fi

python -c "import transformers" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ 错误: 未安装transformers"
    echo "请运行: pip install transformers"
    exit 1
fi

echo "✅ 环境检查通过"
echo ""

# 启动应用
echo "启动Gradio应用..."
echo "应用将在浏览器中自动打开"
echo "访问地址: http://localhost:7860"
echo ""
echo "按 Ctrl+C 停止应用"
echo "=========================================="
echo ""

cd "$(dirname "$0")"
python gradio_ocr_app.py

echo ""
echo "应用已停止"

