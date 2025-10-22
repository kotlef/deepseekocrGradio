#!/usr/bin/env python3
"""
DeepSeek-OCR Agent API 服务
提供 RESTful API 接口供业务系统调用
"""

import os
import sys

# 设置 MPS fallback 环境变量（必须在导入 torch 之前）
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

import logging
import time
import base64
import io
from typing import Optional, List, Dict
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from PIL import Image
import uvicorn

# 添加模块路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules import (
    ModelManager,
    ImageProcessor,
    build_prompt,
    OCREngine,
    ResultProcessor
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title="DeepSeek-OCR Agent API",
    description="基于 DeepSeek-OCR 的 OCR 服务 API",
    version="1.0.0"
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量
model_manager = None
image_processor = None
ocr_engine = None
result_processor = None


# API 请求/响应模型
class OCRRequest(BaseModel):
    """OCR 请求模型"""
    task: str = Field(default="通用OCR", description="OCR 任务类型")
    custom_prompt: Optional[str] = Field(default=None, description="自定义 Prompt")
    resolution_mode: str = Field(default="Base (1024×1024) - 推荐", description="分辨率模式")
    save_visualization: bool = Field(default=False, description="是否保存可视化结果")


class OCRResponse(BaseModel):
    """OCR 响应模型"""
    success: bool = Field(description="是否成功")
    message: str = Field(description="响应消息")
    data: Optional[Dict] = Field(default=None, description="OCR 结果数据")
    error: Optional[str] = Field(default=None, description="错误信息")


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    model_loaded: bool
    device: str
    timestamp: str


def initialize_components():
    """初始化所有组件"""
    global model_manager, image_processor, ocr_engine, result_processor

    try:
        logger.info("初始化组件...")

        # 创建模型管理器
        model_manager = ModelManager()

        # 创建图像处理器
        image_processor = ImageProcessor()

        # 创建 OCR 引擎
        ocr_engine = OCREngine(model_manager)

        # 创建结果处理器
        result_processor = ResultProcessor()

        logger.info("✅ 组件初始化完成")

    except Exception as e:
        logger.error(f"❌ 组件初始化失败: {e}")
        raise


def load_model_if_needed():
    """如果模型未加载，则加载模型"""
    global model_manager
    
    if not model_manager.is_loaded():
        logger.info("模型未加载，开始加载...")
        model_manager.load_model()
        logger.info("✅ 模型加载完成")


@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    logger.info("=" * 60)
    logger.info("DeepSeek-OCR Agent API 服务启动中...")
    logger.info("=" * 60)
    
    # 初始化组件
    initialize_components()
    
    logger.info("=" * 60)
    logger.info("✅ API 服务启动成功")
    logger.info("=" * 60)


@app.get("/", response_model=Dict)
async def root():
    """根路径"""
    return {
        "service": "DeepSeek-OCR Agent API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "ocr": "/api/v1/ocr",
            "ocr_base64": "/api/v1/ocr/base64",
            "tasks": "/api/v1/tasks",
            "resolutions": "/api/v1/resolutions"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    return HealthResponse(
        status="healthy",
        model_loaded=model_manager.is_loaded() if model_manager else False,
        device=model_manager.device if model_manager else "unknown",
        timestamp=datetime.now().isoformat()
    )


@app.get("/api/v1/tasks", response_model=Dict)
async def get_tasks():
    """获取支持的 OCR 任务类型"""
    tasks = [
        "文档转Markdown",
        "通用OCR",
        "纯文本提取",
        "图表解析",
        "图像描述",
        "自定义Prompt"
    ]
    
    return {
        "success": True,
        "data": {
            "tasks": tasks,
            "count": len(tasks)
        }
    }


@app.get("/api/v1/resolutions", response_model=Dict)
async def get_resolutions():
    """获取支持的分辨率模式"""
    resolutions = [
        "Tiny (512×512) - 快速",
        "Small (640×640) - 中等",
        "Base (1024×1024) - 推荐",
        "Large (1280×1280) - 高质量",
        "Gundam (动态分辨率) - 大图像"
    ]
    
    return {
        "success": True,
        "data": {
            "resolutions": resolutions,
            "count": len(resolutions)
        }
    }


@app.post("/api/v1/ocr", response_model=OCRResponse)
async def ocr_image(
    image: UploadFile = File(..., description="图像文件"),
    task: str = Form(default="通用OCR", description="OCR 任务类型"),
    custom_prompt: Optional[str] = Form(default=None, description="自定义 Prompt"),
    resolution_mode: str = Form(default="Base (1024×1024) - 推荐", description="分辨率模式"),
    save_visualization: bool = Form(default=False, description="是否保存可视化结果")
):
    """
    OCR 图像识别接口（文件上传）
    
    Args:
        image: 图像文件
        task: OCR 任务类型
        custom_prompt: 自定义 Prompt（可选）
        resolution_mode: 分辨率模式
        save_visualization: 是否保存可视化结果
        
    Returns:
        OCR 识别结果
    """
    start_time = time.time()
    
    try:
        # 读取图像
        logger.info(f"接收到 OCR 请求: task={task}, resolution={resolution_mode}")
        image_bytes = await image.read()
        pil_image = Image.open(io.BytesIO(image_bytes))
        
        # 验证图像
        is_valid, error_msg = image_processor.validate_image(pil_image)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"图像验证失败: {error_msg}")
        
        # 预处理图像
        pil_image = image_processor.preprocess_image(pil_image)
        
        # 构建 Prompt
        prompt = build_prompt(task, custom_prompt)
        
        # 获取分辨率参数
        base_size, image_size, crop_mode = image_processor.get_resolution_params(resolution_mode)
        
        # 加载模型
        load_model_if_needed()
        
        # 执行 OCR 推理
        logger.info("开始 OCR 推理...")
        result_text, inference_time, num_tokens = ocr_engine.infer(
            image=pil_image,
            prompt=prompt,
            base_size=base_size,
            image_size=image_size,
            crop_mode=crop_mode
        )
        
        # 处理结果
        parsed_result = result_processor.parse_result(result_text)
        
        # 提取边界框
        bounding_boxes = result_processor.extract_bounding_boxes(result_text)
        
        # 保存结果（可选）
        text_path = None
        image_path = None
        if save_visualization:
            output_dir = os.path.join(os.path.dirname(__file__), 'outputs')

            # 生成文件名前缀
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prefix = f"ocr_{timestamp}"

            # 绘制可视化图像
            visualization_image = None
            if bounding_boxes:
                visualization_image = result_processor.draw_bounding_boxes(
                    pil_image, bounding_boxes
                )

            # 保存结果
            text_path, image_path = result_processor.save_results(
                text=parsed_result['clean_text'],
                image=visualization_image,
                output_dir=output_dir,
                prefix=prefix
            )
        
        total_time = time.time() - start_time
        
        logger.info(f"✅ OCR 完成: 推理时间={inference_time:.2f}s, 总时间={total_time:.2f}s")
        
        return OCRResponse(
            success=True,
            message="OCR 识别成功",
            data={
                "text": parsed_result['clean_text'],
                "raw_text": parsed_result['raw_text'],
                "bounding_boxes": bounding_boxes,
                "bounding_box_count": len(bounding_boxes),
                "inference_time": round(inference_time, 2),
                "total_time": round(total_time, 2),
                "num_tokens": num_tokens,
                "task": task,
                "resolution_mode": resolution_mode,
                "text_file": text_path,
                "visualization_file": image_path
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ OCR 失败: {e}", exc_info=True)
        return OCRResponse(
            success=False,
            message="OCR 识别失败",
            error=str(e)
        )


@app.post("/api/v1/ocr/base64", response_model=OCRResponse)
async def ocr_image_base64(
    image_base64: str = Form(..., description="Base64 编码的图像"),
    task: str = Form(default="通用OCR", description="OCR 任务类型"),
    custom_prompt: Optional[str] = Form(default=None, description="自定义 Prompt"),
    resolution_mode: str = Form(default="Base (1024×1024) - 推荐", description="分辨率模式"),
    save_visualization: bool = Form(default=False, description="是否保存可视化结果")
):
    """
    OCR 图像识别接口（Base64 编码）
    
    Args:
        image_base64: Base64 编码的图像
        task: OCR 任务类型
        custom_prompt: 自定义 Prompt（可选）
        resolution_mode: 分辨率模式
        save_visualization: 是否保存可视化结果
        
    Returns:
        OCR 识别结果
    """
    try:
        # 解码 Base64 图像
        image_bytes = base64.b64decode(image_base64)
        pil_image = Image.open(io.BytesIO(image_bytes))
        
        # 创建临时 UploadFile 对象
        class FakeUploadFile:
            async def read(self):
                return image_bytes
        
        fake_file = FakeUploadFile()
        
        # 调用主 OCR 接口
        return await ocr_image(
            image=fake_file,
            task=task,
            custom_prompt=custom_prompt,
            resolution_mode=resolution_mode,
            save_visualization=save_visualization
        )
        
    except Exception as e:
        logger.error(f"❌ Base64 解码失败: {e}")
        return OCRResponse(
            success=False,
            message="Base64 解码失败",
            error=str(e)
        )


if __name__ == "__main__":
    # 运行 API 服务
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )

