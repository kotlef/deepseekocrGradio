#!/bin/bash

# DeepSeek-OCR Agent API 启动脚本

echo "======================================"
echo "  DeepSeek-OCR Agent API 服务"
echo "======================================"

# 检查 conda 环境
if ! command -v conda &> /dev/null; then
    echo "❌ 错误: 未找到 conda 命令"
    echo "请先安装 Anaconda 或 Miniconda"
    exit 1
fi

# 激活环境
echo "激活 conda 环境: deepseek-ocr"
eval "$(conda shell.bash hook)"
conda activate deepseek-ocr

if [ $? -ne 0 ]; then
    echo "❌ 错误: 无法激活 conda 环境 deepseek-ocr"
    exit 1
fi

# 检查依赖
echo "检查依赖..."
python -c "import fastapi, uvicorn" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ 错误: 缺少依赖包"
    echo "请运行: pip install fastapi uvicorn python-multipart"
    exit 1
fi

echo "✅ 依赖检查通过"

# 进入应用目录
cd "$(dirname "$0")"

# 启动 API 服务
echo ""
echo "======================================"
echo "  启动 API 服务"
echo "======================================"
echo "地址: http://localhost:8000"
echo "文档: http://localhost:8000/docs"
echo "======================================"
echo ""

python api_server.py

