"""
OCR推理模块
负责执行DeepSeek-OCR模型推理
"""

import logging
import time
import tempfile
import os
from typing import Tuple, Optional
from PIL import Image

from .model_manager import ModelManager

logger = logging.getLogger(__name__)


class OCREngine:
    """OCR推理引擎"""
    
    def __init__(self, model_manager: ModelManager):
        """
        初始化OCR引擎
        
        Args:
            model_manager: 模型管理器实例
        """
        self.model_manager = model_manager
        logger.info("OCR推理引擎初始化完成")
    
    def infer(
        self,
        image: Image.Image,
        prompt: str,
        base_size: int = 1024,
        image_size: int = 1024,
        crop_mode: bool = False,
        save_results: bool = False
    ) -> Tuple[str, float, int]:
        """
        执行OCR推理
        
        Args:
            image: PIL Image对象
            prompt: 推理使用的prompt
            base_size: 全局视图尺寸
            image_size: 局部视图尺寸（仅在crop_mode=True时使用）
            crop_mode: 是否启用动态裁剪
            save_results: 是否保存中间结果
            
        Returns:
            (识别结果文本, 推理时间(秒), 生成的token数)
            
        Raises:
            RuntimeError: 模型未加载或推理失败
        """
        # 检查模型是否已加载
        if not self.model_manager.is_loaded():
            raise RuntimeError("模型未加载，请先加载模型")
        
        try:
            logger.info("=" * 60)
            logger.info("开始OCR推理")
            logger.info(f"Prompt: {prompt}")
            logger.info(f"图像尺寸: {image.size}")
            logger.info(f"分辨率参数: base_size={base_size}, image_size={image_size}, crop_mode={crop_mode}")
            
            # 获取模型和分词器
            model = self.model_manager.get_model()
            tokenizer = self.model_manager.get_tokenizer()
            
            # 创建临时文件保存图像
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                temp_image_path = tmp_file.name
                image.save(temp_image_path, format='JPEG', quality=95)
                logger.info(f"临时图像保存至: {temp_image_path}")
            
            # 创建临时输出目录
            temp_output_dir = tempfile.mkdtemp()
            logger.info(f"临时输出目录: {temp_output_dir}")
            
            try:
                # 记录开始时间
                start_time = time.time()
                
                # 调用模型的infer方法
                logger.info("调用模型推理...")
                result_text = model.infer(
                    tokenizer=tokenizer,
                    prompt=prompt,
                    image_file=temp_image_path,
                    output_path=temp_output_dir,
                    base_size=base_size,
                    image_size=image_size,
                    crop_mode=crop_mode,
                    save_results=save_results,
                    test_compress=False,
                    eval_mode=True  # 必须设置为True才能返回结果
                )
                
                # 计算推理时间
                inference_time = time.time() - start_time

                # 检查结果
                if result_text is None:
                    logger.error("模型返回了 None，可能是推理失败")
                    raise RuntimeError("模型推理返回 None")

                # 估算生成的token数（简单估算：字符数/4）
                num_tokens = len(result_text) // 4 if result_text else 0

                logger.info(f"✅ 推理完成！")
                logger.info(f"推理时间: {inference_time:.2f}秒")
                logger.info(f"生成文本长度: {len(result_text)}字符")
                logger.info(f"估算Token数: {num_tokens}")
                logger.info("=" * 60)

                return result_text, inference_time, num_tokens
                
            finally:
                # 清理临时文件
                try:
                    if os.path.exists(temp_image_path):
                        os.remove(temp_image_path)
                        logger.debug(f"已删除临时图像: {temp_image_path}")
                    
                    # 清理临时输出目录
                    if os.path.exists(temp_output_dir):
                        import shutil
                        shutil.rmtree(temp_output_dir)
                        logger.debug(f"已删除临时输出目录: {temp_output_dir}")
                except Exception as e:
                    logger.warning(f"清理临时文件失败: {e}")
        
        except Exception as e:
            logger.error(f"❌ OCR推理失败: {e}", exc_info=True)
            raise RuntimeError(f"OCR推理失败: {str(e)}")
    
    def infer_batch(
        self,
        images: list,
        prompts: list,
        base_size: int = 1024,
        image_size: int = 1024,
        crop_mode: bool = False
    ) -> list:
        """
        批量推理（顺序执行）
        
        Args:
            images: PIL Image对象列表
            prompts: Prompt列表
            base_size: 全局视图尺寸
            image_size: 局部视图尺寸
            crop_mode: 是否启用动态裁剪
            
        Returns:
            结果列表，每个元素为(result_text, inference_time, num_tokens)
        """
        if len(images) != len(prompts):
            raise ValueError("图像数量和Prompt数量必须相同")
        
        results = []
        total_start_time = time.time()
        
        logger.info(f"开始批量推理，共{len(images)}张图像")
        
        for idx, (image, prompt) in enumerate(zip(images, prompts), 1):
            logger.info(f"处理第{idx}/{len(images)}张图像...")
            try:
                result = self.infer(
                    image=image,
                    prompt=prompt,
                    base_size=base_size,
                    image_size=image_size,
                    crop_mode=crop_mode,
                    save_results=False
                )
                results.append(result)
            except Exception as e:
                logger.error(f"第{idx}张图像推理失败: {e}")
                results.append(("", 0.0, 0))
        
        total_time = time.time() - total_start_time
        logger.info(f"批量推理完成，总耗时: {total_time:.2f}秒")
        
        return results


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("OCR推理引擎测试")
    print("注意：此测试需要先加载模型，可能需要较长时间")
    
    # 这里只是示例，实际测试需要真实的模型和图像
    # from .model_manager import ModelManager
    # manager = ModelManager()
    # manager.load_model()
    # engine = OCREngine(manager)
    # ...

