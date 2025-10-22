"""
图像处理模块
负责图像验证、预处理和格式转换
"""

import logging
from typing import Tuple, Optional
from PIL import Image, ImageOps

logger = logging.getLogger(__name__)


class ImageProcessor:
    """图像处理器"""
    
    # 支持的图像格式
    SUPPORTED_FORMATS = {'JPEG', 'JPG', 'PNG', 'WEBP'}
    
    # 最大图像尺寸（像素）
    MAX_IMAGE_SIZE = 10000
    
    # 最大文件大小（字节，10MB）
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    def __init__(self):
        """初始化图像处理器"""
        logger.info("图像处理器初始化完成")
    
    def validate_image(self, image: Image.Image) -> Tuple[bool, str]:
        """
        验证图像是否符合要求
        
        Args:
            image: PIL Image对象
            
        Returns:
            (是否有效, 错误消息)
        """
        try:
            # 检查图像是否为None
            if image is None:
                return False, "图像为空，请上传有效的图片"
            
            # 检查图像格式
            if image.format and image.format.upper() not in self.SUPPORTED_FORMATS:
                return False, f"不支持的图像格式: {image.format}。支持的格式: {', '.join(self.SUPPORTED_FORMATS)}"
            
            # 检查图像尺寸
            width, height = image.size
            if width <= 0 or height <= 0:
                return False, f"无效的图像尺寸: {width}x{height}"
            
            if width > self.MAX_IMAGE_SIZE or height > self.MAX_IMAGE_SIZE:
                return False, f"图像尺寸过大: {width}x{height}。最大支持: {self.MAX_IMAGE_SIZE}x{self.MAX_IMAGE_SIZE}"
            
            # 检查图像模式
            if image.mode not in ['RGB', 'RGBA', 'L', 'P']:
                logger.warning(f"图像模式 {image.mode} 将被转换为 RGB")
            
            logger.info(f"图像验证通过: {width}x{height}, 格式: {image.format}, 模式: {image.mode}")
            return True, ""
            
        except Exception as e:
            logger.error(f"图像验证失败: {e}")
            return False, f"图像验证失败: {str(e)}"
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        图像预处理
        
        Args:
            image: 原始PIL Image对象
            
        Returns:
            预处理后的PIL Image对象
        """
        try:
            # 1. 处理EXIF旋转信息
            image = ImageOps.exif_transpose(image)
            logger.info("已处理EXIF旋转信息")
            
            # 2. 转换为RGB模式
            if image.mode != 'RGB':
                logger.info(f"将图像从 {image.mode} 模式转换为 RGB 模式")
                image = image.convert('RGB')
            
            logger.info(f"图像预处理完成: {image.size}")
            return image
            
        except Exception as e:
            logger.error(f"图像预处理失败: {e}")
            # 如果预处理失败，尝试返回原图
            if image.mode != 'RGB':
                return image.convert('RGB')
            return image
    
    @staticmethod
    def get_resolution_params(mode: str) -> Tuple[int, int, bool]:
        """
        根据分辨率模式名称获取参数
        
        Args:
            mode: 分辨率模式字符串
            
        Returns:
            (base_size, image_size, crop_mode)
        """
        mode_mapping = {
            "Tiny": (512, 512, False),
            "Small": (640, 640, False),
            "Base": (1024, 1024, False),
            "Large": (1280, 1280, False),
            "Gundam": (1024, 640, True)
        }
        
        # 从模式字符串中提取关键词
        for key, params in mode_mapping.items():
            if key in mode:
                logger.info(f"分辨率模式: {key} -> base_size={params[0]}, image_size={params[1]}, crop_mode={params[2]}")
                return params
        
        # 默认返回Base模式
        logger.warning(f"未识别的分辨率模式: {mode}，使用默认Base模式")
        return mode_mapping["Base"]
    
    @staticmethod
    def get_image_info(image: Image.Image) -> dict:
        """
        获取图像信息
        
        Args:
            image: PIL Image对象
            
        Returns:
            包含图像信息的字典
        """
        return {
            "size": f"{image.size[0]}x{image.size[1]}",
            "width": image.size[0],
            "height": image.size[1],
            "format": image.format or "Unknown",
            "mode": image.mode
        }


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    processor = ImageProcessor()
    
    # 测试分辨率参数获取
    print("\n测试分辨率参数:")
    test_modes = [
        "Tiny (512×512) - 快速",
        "Small (640×640) - 中等",
        "Base (1024×1024) - 推荐",
        "Large (1280×1280) - 高质量",
        "Gundam (动态) - 大图像"
    ]
    
    for mode in test_modes:
        base_size, image_size, crop_mode = processor.get_resolution_params(mode)
        print(f"{mode}:")
        print(f"  base_size={base_size}, image_size={image_size}, crop_mode={crop_mode}")

