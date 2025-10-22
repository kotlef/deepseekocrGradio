# DeepSeek-OCR Gradio 应用

基于 DeepSeek-OCR 模型的智能文字识别 Web 应用，提供友好的图形界面，支持多种 OCR 场景。

## 📋 目录

- [功能特性](#功能特性)
- [系统要求](#系统要求)
- [安装步骤](#安装步骤)
- [使用方法](#使用方法)
- [项目结构](#项目结构)
- [常见问题](#常见问题)
- [开发说明](#开发说明)

## ✨ 功能特性

### 核心功能

- **多种 OCR 任务**
  - 📄 文档转 Markdown：结构化文档识别，保留格式
  - 🔍 通用 OCR：普通图像文字识别，包含位置信息
  - 📝 纯文本提取：忽略布局，仅提取文字
  - 📊 图表解析：识别图表、图形内容
  - 🖼️ 图像描述：生成图像的详细描述
  - ⚙️ 自定义 Prompt：用户自定义识别任务

- **多种分辨率模式**
  - Tiny (512×512)：快速处理小图像
  - Small (640×640)：中等图像
  - Base (1024×1024)：标准文档（推荐）
  - Large (1280×1280)：高分辨率文档
  - Gundam (动态)：大尺寸文档自适应

- **可视化功能**
  - 边界框标注：显示文字位置
  - 结果下载：支持文本和图像下载
  - 实时状态：显示推理进度和统计信息

### 技术特性

- ✅ Mac M2 优化：支持 MPS 加速
- ✅ 中文界面：完全中文化
- ✅ 模块化设计：代码结构清晰
- ✅ 完整日志：详细的运行日志
- ✅ 错误处理：友好的错误提示

## 💻 系统要求

### 硬件要求

- **推荐配置**：
  - Mac M2 或更高版本（支持 MPS 加速）
  - 16GB+ 内存
  - 10GB+ 可用磁盘空间

- **最低配置**：
  - 任何支持 Python 3.12 的设备
  - 8GB+ 内存
  - 10GB+ 可用磁盘空间

### 软件要求

- macOS 12.0+（推荐 macOS 13.0+）
- Python 3.12+
- Conda 或 Miniconda

## 🚀 安装步骤

### 1. 克隆项目

```bash
cd /path/to/your/workspace
git clone https://github.com/kotlef/deepseekocrGradio.git
cd deepseekocrGradio
```

### 2. 创建 Conda 环境

```bash
conda create -n deepseek-ocr python=3.12
conda activate deepseek-ocr
```

### 3. 安装依赖

```bash
# 安装基础依赖
pip install -r requirements.txt

# 安装 Gradio
pip install gradio

# 替换 huggingface的modeling_deepseekocr.py
cp gradio_app/modeling_deepseekocr_fixed.py /[YourPath]/.cache/huggingface/modules/transformers_modules/deepseek-ai/DeepSeek-OCR/[968c903185ba632ccc137b22d78ba01d14611ee1]/modeling_deepseekocr.py
```


### 4. 验证安装

```bash
cd gradio_app
python test_modules.py
```

如果看到所有测试通过，说明安装成功！

## 📖 使用方法

### 方式一：使用启动脚本（推荐）

```bash
cd gradio_app
./start_app.sh
```

### 方式二：直接运行 Python 脚本

```bash
cd gradio_app
conda activate deepseek-ocr
python gradio_ocr_app.py
```

### 方式三：指定端口运行

```bash
cd gradio_app
conda activate deepseek-ocr
python gradio_ocr_app.py --port 8080
```

### 访问应用

启动后，应用会自动在浏览器中打开，或手动访问：

```
http://localhost:7860
```

### 使用流程

1. **上传图像**
   - 点击上传按钮选择图片
   - 或直接拖拽图片到上传区域
   - 或粘贴剪贴板中的图片

2. **选择 OCR 任务**
   - 根据需求选择合适的任务类型
   - 如选择"自定义 Prompt"，需输入自定义指令

3. **配置分辨率模式**
   - 推荐使用 Base 模式
   - 大图像可使用 Gundam 模式
   - 追求速度可使用 Tiny 或 Small 模式

4. **开始识别**
   - 点击"🚀 开始识别"按钮
   - 首次运行会自动下载模型（约 5-10 分钟）
   - 等待推理完成

5. **查看结果**
   - 识别结果会显示在右侧面板
   - 可视化图像显示文字边界框
   - 点击下载按钮保存结果

## 📁 项目结构

```
gradio_app/
├── gradio_ocr_app.py          # Gradio 主应用
├── start_app.sh               # 启动脚本
├── test_modules.py            # 模块测试脚本
├── README.md                  # 使用说明
├── modules/                   # 核心模块
│   ├── __init__.py           # 模块初始化
│   ├── model_manager.py      # 模型管理
│   ├── image_processor.py    # 图像处理
│   ├── prompt_builder.py     # Prompt 构建
│   ├── ocr_engine.py         # OCR 推理
│   └── result_processor.py   # 结果处理
├── outputs/                   # 输出文件目录
├── logs/                      # 日志文件目录
└── examples/                  # 示例图片目录
```

## ❓ 常见问题

### Q1: 首次运行很慢？

**A**: 首次运行需要下载 DeepSeek-OCR 模型（约 5GB），请耐心等待。模型会缓存到本地，后续运行会很快。

### Q2: 推理速度慢？

**A**: 
- 确保使用 Mac M2 设备以启用 MPS 加速
- 尝试使用较小的分辨率模式（Tiny 或 Small）
- 关闭动态裁剪（crop_mode）

### Q3: 内存不足？

**A**:
- 使用较小的分辨率模式
- 关闭其他占用内存的应用
- 处理较小的图像

### Q4: 模型加载失败？

**A**:
- 检查网络连接
- 确保有足够的磁盘空间
- 查看日志文件获取详细错误信息

### Q5: 识别结果不准确？

**A**:
- 尝试使用更高的分辨率模式（Base 或 Large）
- 确保图像清晰、光线充足
- 对于大图像，使用 Gundam 模式
- 尝试不同的 OCR 任务类型

## 🛠️ 开发说明

### 运行测试

```bash
cd gradio_app
python test_modules.py
```

### 查看日志

```bash
cd gradio_app/logs
tail -f ocr_app_YYYYMMDD.log
```

### 修改配置

主要配置在 `gradio_ocr_app.py` 中：

```python
# 修改默认端口
demo.launch(server_port=8080)

# 修改模型路径
model_manager = ModelManager(model_name='path/to/your/model')
```

### 添加新功能

1. 在 `modules/` 目录下创建新模块
2. 在 `modules/__init__.py` 中导出
3. 在 `gradio_ocr_app.py` 中集成

## 📊 性能指标

基于 Mac M2 设备的测试结果：

| 分辨率模式 | 图像尺寸 | 推理时间 | 内存占用 |
|-----------|---------|---------|---------|
| Tiny      | 512×512 | ~5秒    | ~2GB    |
| Small     | 640×640 | ~8秒    | ~3GB    |
| Base      | 1024×1024 | ~15秒  | ~4GB    |
| Large     | 1280×1280 | ~25秒  | ~5GB    |
| Gundam    | 动态     | ~20-40秒 | ~4-6GB  |

*注：实际性能取决于图像内容和设备配置*

## 📝 更新日志

### v1.0.0 (2025-10-22)

- ✅ 初始版本发布
- ✅ 支持 6 种 OCR 任务
- ✅ 支持 5 种分辨率模式
- ✅ Mac M2 MPS 加速
- ✅ 完整的 Gradio Web 界面
- ✅ 边界框可视化
- ✅ 结果下载功能

## 🙏 致谢

- [DeepSeek-OCR](https://github.com/deepseek-ai/DeepSeek-OCR) - 核心 OCR 模型
- [Gradio](https://gradio.app/) - Web 界面框架
- [HuggingFace Transformers](https://huggingface.co/transformers/) - 模型推理框架

## 📄 许可证

本项目遵循 DeepSeek-OCR 的许可证。

## 🔗 相关链接

- [DeepSeek-OCR GitHub](https://github.com/deepseek-ai/DeepSeek-OCR)
- [DeepSeek-OCR 模型](https://huggingface.co/deepseek-ai/DeepSeek-OCR)
- [Gradio 文档](https://gradio.app/docs/)

---

**如有问题或建议，欢迎提交 Issue！**

