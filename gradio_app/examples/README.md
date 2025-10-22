# 示例图片目录

## 📁 目录说明

此目录用于存放示例图片，供 Gradio 应用的 Examples 功能使用。

## 📸 建议的示例图片

### 1. 文档类
- `document.jpg` - 扫描文档或 PDF 截图
- `receipt.jpg` - 收据或发票
- `book_page.jpg` - 书籍页面

### 2. 图表类
- `chart.png` - 柱状图、折线图等
- `table.png` - 表格数据
- `diagram.png` - 流程图、示意图

### 3. 通用类
- `screenshot.png` - 屏幕截图
- `photo.jpg` - 包含文字的照片
- `handwriting.jpg` - 手写文字（可选）

## 📝 使用方法

### 添加示例图片

1. 将图片文件复制到此目录
2. 在 `gradio_ocr_app.py` 中添加示例配置：

```python
gr.Examples(
    examples=[
        ["examples/document.jpg", "文档转Markdown", "Base (1024×1024) - 推荐"],
        ["examples/chart.png", "图表解析", "Small (640×640) - 中等"],
        ["examples/screenshot.png", "通用OCR", "Base (1024×1024) - 推荐"],
    ],
    inputs=[image_input, task_selector, resolution_mode],
    label="示例图片"
)
```

### 图片要求

- **格式**：JPG, PNG, JPEG, WEBP
- **大小**：建议不超过 5MB
- **尺寸**：建议不超过 2000×2000 像素
- **质量**：清晰、光线充足

## 💡 提示

- 示例图片应该具有代表性，展示不同的 OCR 场景
- 建议提供 3-5 个示例图片
- 图片文件名应该简洁明了
- 可以为每个 OCR 任务类型准备一个示例

## 📂 当前状态

此目录当前为空，你可以根据需要添加示例图片。

如果你有合适的示例图片，请将它们复制到此目录，并更新 `gradio_ocr_app.py` 中的示例配置。

