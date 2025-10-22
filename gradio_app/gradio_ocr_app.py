#!/usr/bin/env python3
"""
DeepSeek-OCR Gradio应用
基于DeepSeek-OCR模型的Web OCR应用
"""

import gradio as gr
import logging
import os
import sys
from datetime import datetime
from typing import Tuple, Optional

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules import (
    ModelManager,
    ImageProcessor,
    build_prompt,
    get_task_description,
    get_all_tasks,
    OCREngine,
    ResultProcessor
)

# 配置日志
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, f'ocr_app_{datetime.now().strftime("%Y%m%d")}.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 全局变量
model_manager = None
image_processor = None
ocr_engine = None
result_processor = None
output_dir = os.path.join(os.path.dirname(__file__), 'outputs')
os.makedirs(output_dir, exist_ok=True)


def initialize_components():
    """初始化所有组件"""
    global model_manager, image_processor, ocr_engine, result_processor
    
    logger.info("=" * 60)
    logger.info("初始化DeepSeek-OCR应用组件")
    logger.info("=" * 60)
    
    try:
        # 初始化模型管理器
        logger.info("1. 初始化模型管理器...")
        model_manager = ModelManager()
        
        # 初始化图像处理器
        logger.info("2. 初始化图像处理器...")
        image_processor = ImageProcessor()
        
        # 初始化结果处理器
        logger.info("3. 初始化结果处理器...")
        result_processor = ResultProcessor()
        
        logger.info("✅ 组件初始化完成")
        return True
        
    except Exception as e:
        logger.error(f"❌ 组件初始化失败: {e}")
        return False


def load_model_if_needed():
    """按需加载模型"""
    global model_manager, ocr_engine
    
    if model_manager is None:
        raise RuntimeError("模型管理器未初始化")
    
    if not model_manager.is_loaded():
        logger.info("开始加载模型...")
        model_manager.load_model()
        logger.info("模型加载完成")
    
    # 初始化OCR引擎
    if ocr_engine is None:
        ocr_engine = OCREngine(model_manager)


def ocr_inference(
    image,
    task: str,
    custom_prompt: str,
    resolution_mode: str,
    save_visualization: bool
) -> Tuple[str, Optional[str], Optional[str], Optional[str], str]:
    """
    执行OCR推理的主函数
    
    Args:
        image: 上传的图像
        task: OCR任务类型
        custom_prompt: 自定义prompt
        resolution_mode: 分辨率模式
        save_visualization: 是否保存可视化结果
        
    Returns:
        (识别结果文本, 可视化图像, 下载文本路径, 下载图像路径, 状态信息)
    """
    try:
        logger.info("\n" + "=" * 60)
        logger.info("开始OCR推理流程")
        logger.info("=" * 60)
        
        # 1. 验证输入
        if image is None:
            return "", None, None, None, "❌ 错误：请先上传图像"
        
        # 2. 验证图像
        is_valid, error_msg = image_processor.validate_image(image)
        if not is_valid:
            return "", None, None, None, f"❌ 图像验证失败：{error_msg}"
        
        # 3. 预处理图像
        image = image_processor.preprocess_image(image)
        
        # 4. 构建Prompt
        prompt = build_prompt(task, custom_prompt)
        logger.info(f"任务类型: {task}")
        logger.info(f"Prompt: {prompt}")
        
        # 5. 获取分辨率参数
        base_size, image_size, crop_mode = image_processor.get_resolution_params(resolution_mode)
        
        # 6. 加载模型（如果尚未加载）
        status_msg = "⏳ 正在加载模型..."
        yield "", None, None, None, status_msg
        
        load_model_if_needed()
        
        # 7. 执行推理
        status_msg = "⏳ 正在执行OCR推理..."
        yield "", None, None, None, status_msg
        
        result_text, inference_time, num_tokens = ocr_engine.infer(
            image=image,
            prompt=prompt,
            base_size=base_size,
            image_size=image_size,
            crop_mode=crop_mode,
            save_results=False
        )
        
        # 8. 处理结果
        status_msg = "⏳ 正在处理结果..."
        yield "", None, None, None, status_msg
        
        parsed_result = result_processor.parse_result(result_text)
        clean_text = parsed_result["clean_text"]
        bounding_boxes = parsed_result["bounding_boxes"]
        
        # 9. 生成可视化（如果有边界框）
        visualization_image = None
        if save_visualization and bounding_boxes:
            visualization_image = result_processor.draw_bounding_boxes(
                image=image,
                boxes=bounding_boxes,
                show_text=True
            )
        
        # 10. 保存结果文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        text_path, image_path = result_processor.save_results(
            text=clean_text,
            image=visualization_image,
            output_dir=output_dir,
            prefix=f"ocr_{timestamp}"
        )
        
        # 11. 生成状态信息
        status_msg = f"""✅ 识别完成！
⏱ 推理时间: {inference_time:.2f}秒
📊 生成Token数: {num_tokens}
📝 文本长度: {len(clean_text)}字符
🎯 检测到边界框: {len(bounding_boxes)}个
"""
        
        logger.info("OCR推理流程完成")
        logger.info("=" * 60)
        
        yield clean_text, visualization_image, text_path, image_path, status_msg
        
    except Exception as e:
        error_msg = f"❌ 推理失败：{str(e)}"
        logger.error(error_msg, exc_info=True)
        yield "", None, None, None, error_msg


def update_custom_prompt_visibility(task: str):
    """根据任务类型更新自定义Prompt输入框的可见性"""
    return gr.update(visible=(task == "自定义Prompt"))


def update_crop_option(mode: str):
    """根据分辨率模式更新裁剪选项"""
    is_gundam = "Gundam" in mode
    return gr.update(value=is_gundam, interactive=not is_gundam)


def create_gradio_interface():
    """创建Gradio界面"""
    
    # 定义CSS样式
    custom_css = """
    .main-title {
        text-align: center;
        color: #2c3e50;
        margin-bottom: 20px;
    }
    .status-box {
        background-color: #f8f9fa;
        border-radius: 5px;
        padding: 10px;
        margin-top: 10px;
    }
    """
    
    with gr.Blocks(css=custom_css, title="DeepSeek-OCR 应用") as demo:
        # 标题和说明
        gr.Markdown(
            """
            # 🔍 DeepSeek-OCR 应用
            
            基于 DeepSeek-OCR 模型的智能文字识别应用，支持文档、图表、通用图像等多种OCR场景。
            
            ### 📖 使用说明
            1. 📤 上传图像或粘贴截图
            2. 🎯 选择OCR任务类型
            3. ⚙️ 配置分辨率模式（推荐使用Base模式）
            4. 🚀 点击"开始识别"按钮
            5. 📥 查看结果并下载
            """,
            elem_classes="main-title"
        )
        
        with gr.Row():
            # 左侧面板：输入区
            with gr.Column(scale=1):
                gr.Markdown("## 📤 输入配置")
                
                # 图像上传
                image_input = gr.Image(
                    label="上传图像",
                    type="pil",
                    sources=["upload", "clipboard"],
                    height=400
                )
                
                # OCR任务选择
                task_selector = gr.Radio(
                    choices=get_all_tasks(),
                    value="文档转Markdown",
                    label="选择OCR任务",
                    info="选择要执行的OCR任务类型"
                )
                
                # 自定义Prompt
                custom_prompt = gr.Textbox(
                    label="自定义Prompt",
                    placeholder="例如：识别图片中的所有数字",
                    visible=False,
                    lines=2
                )
                
                # 分辨率模式
                resolution_mode = gr.Dropdown(
                    choices=[
                        "Tiny (512×512) - 快速",
                        "Small (640×640) - 中等",
                        "Base (1024×1024) - 推荐",
                        "Large (1280×1280) - 高质量",
                        "Gundam (动态) - 大图像"
                    ],
                    value="Base (1024×1024) - 推荐",
                    label="分辨率模式",
                    info="选择合适的分辨率模式"
                )
                
                # 高级选项
                save_visualization = gr.Checkbox(
                    label="保存可视化结果（边界框标注）",
                    value=True
                )
                
                # 开始识别按钮
                submit_btn = gr.Button("🚀 开始识别", variant="primary", size="lg")
            
            # 右侧面板：输出区
            with gr.Column(scale=1):
                gr.Markdown("## 📊 识别结果")
                
                # 识别结果文本
                result_text = gr.Markdown(
                    label="识别结果",
                    value="*识别结果将显示在这里*"
                )
                
                # 可视化结果
                result_image = gr.Image(
                    label="可视化结果（边界框标注）",
                    type="pil",
                    height=300
                )
                
                # 状态信息
                status_info = gr.Textbox(
                    label="状态信息",
                    value="等待开始...",
                    interactive=False,
                    lines=6,
                    elem_classes="status-box"
                )
                
                # 下载按钮
                with gr.Row():
                    download_text = gr.File(label="📥 下载识别文本")
                    download_image = gr.File(label="📥 下载标注图像")
        
        # 事件绑定
        task_selector.change(
            fn=update_custom_prompt_visibility,
            inputs=[task_selector],
            outputs=[custom_prompt]
        )
        
        resolution_mode.change(
            fn=update_crop_option,
            inputs=[resolution_mode],
            outputs=[save_visualization]
        )
        
        submit_btn.click(
            fn=ocr_inference,
            inputs=[
                image_input,
                task_selector,
                custom_prompt,
                resolution_mode,
                save_visualization
            ],
            outputs=[
                result_text,
                result_image,
                download_text,
                download_image,
                status_info
            ]
        )
        
        # 页脚
        gr.Markdown(
            """
            ---
            💡 **提示**: 
            - 首次运行需要下载模型，请耐心等待
            - Mac M2设备使用MPS加速，推理速度较快
            - 建议使用Base或Small模式以获得最佳性能
            
            📚 **项目地址**: [DeepSeek-OCR](https://github.com/deepseek-ai/DeepSeek-OCR)
            """
        )
    
    return demo


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("启动DeepSeek-OCR Gradio应用")
    logger.info("=" * 60)
    
    # 初始化组件
    if not initialize_components():
        logger.error("组件初始化失败，退出程序")
        return
    
    # 创建Gradio界面
    demo = create_gradio_interface()
    
    # 启动应用
    logger.info("启动Gradio服务...")
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True,
        show_error=True
    )


if __name__ == "__main__":
    main()

