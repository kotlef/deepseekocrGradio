"""
结果处理模块
负责解析OCR结果、提取定位信息、生成可视化
"""

import re
import logging
import os
from typing import List, Tuple, Dict, Optional
from PIL import Image, ImageDraw, ImageFont
import random

logger = logging.getLogger(__name__)


class ResultProcessor:
    """OCR结果处理器"""
    
    # 正则表达式模式：匹配 <|ref|>文本<|/ref|><|det|>坐标<|/det|>
    PATTERN = r'(<\|ref\|>(.*?)<\|/ref\|><\|det\|>(.*?)<\|/det\|>)'
    
    def __init__(self):
        """初始化结果处理器"""
        logger.info("结果处理器初始化完成")
    
    def parse_result(self, raw_text: str) -> Dict:
        """
        解析原始OCR结果
        
        Args:
            raw_text: 原始OCR输出文本
            
        Returns:
            包含解析结果的字典
        """
        result = {
            "raw_text": raw_text,
            "clean_text": self.clean_markdown(raw_text),
            "bounding_boxes": self.extract_bounding_boxes(raw_text),
            "has_grounding": "<|ref|>" in raw_text and "<|det|>" in raw_text
        }
        
        logger.info(f"解析结果: 检测到{len(result['bounding_boxes'])}个边界框")
        return result
    
    def extract_bounding_boxes(self, raw_text: str) -> List[Dict]:
        """
        从原始文本中提取边界框信息
        
        Args:
            raw_text: 原始OCR输出文本
            
        Returns:
            边界框列表，每个元素包含 {text, bbox}
        """
        boxes = []
        
        # 使用正则表达式匹配所有的定位标记
        matches = re.findall(self.PATTERN, raw_text)
        
        for match in matches:
            full_match, text, coords = match
            
            try:
                # 解析坐标字符串，格式如: "[[x1,y1],[x2,y2]]"
                # 坐标范围是 [0, 999]
                coords_clean = coords.strip()
                
                # 使用eval解析坐标（注意：生产环境应使用更安全的方法）
                coord_list = eval(coords_clean)
                
                if len(coord_list) == 2:
                    # 归一化坐标 [0, 999] -> [0, 1]
                    x1, y1 = coord_list[0]
                    x2, y2 = coord_list[1]
                    
                    boxes.append({
                        "text": text,
                        "bbox": [x1 / 999.0, y1 / 999.0, x2 / 999.0, y2 / 999.0]
                    })
                    
            except Exception as e:
                logger.warning(f"解析边界框失败: {coords}, 错误: {e}")
                continue
        
        logger.info(f"成功提取{len(boxes)}个边界框")
        return boxes
    
    def draw_bounding_boxes(
        self,
        image: Image.Image,
        boxes: List[Dict],
        show_text: bool = True,
        box_width: int = 3
    ) -> Image.Image:
        """
        在图像上绘制边界框
        
        Args:
            image: 原始PIL Image对象
            boxes: 边界框列表
            show_text: 是否显示文本标签
            box_width: 边界框线宽
            
        Returns:
            绘制了边界框的PIL Image对象
        """
        if not boxes:
            logger.info("没有边界框需要绘制")
            return image.copy()
        
        # 创建图像副本
        img_with_boxes = image.copy()
        draw = ImageDraw.Draw(img_with_boxes)
        
        # 获取图像尺寸
        img_width, img_height = image.size
        
        # 尝试加载字体
        try:
            # 尝试使用系统字体
            font_size = max(12, min(img_width, img_height) // 50)
            font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", font_size)
        except Exception as e:
            logger.warning(f"加载字体失败，使用默认字体: {e}")
            font = ImageFont.load_default()
        
        # 为每个边界框生成随机颜色
        colors = [
            (255, 0, 0),      # 红色
            (0, 255, 0),      # 绿色
            (0, 0, 255),      # 蓝色
            (255, 255, 0),    # 黄色
            (255, 0, 255),    # 品红
            (0, 255, 255),    # 青色
            (255, 128, 0),    # 橙色
            (128, 0, 255),    # 紫色
        ]
        
        # 绘制每个边界框
        for idx, box_info in enumerate(boxes):
            bbox = box_info["bbox"]
            text = box_info["text"]
            
            # 将归一化坐标转换为像素坐标
            x1 = int(bbox[0] * img_width)
            y1 = int(bbox[1] * img_height)
            x2 = int(bbox[2] * img_width)
            y2 = int(bbox[3] * img_height)
            
            # 选择颜色
            color = colors[idx % len(colors)]
            
            # 绘制矩形框
            draw.rectangle(
                [(x1, y1), (x2, y2)],
                outline=color,
                width=box_width
            )
            
            # 绘制文本标签（如果需要）
            if show_text and text:
                # 在边界框上方绘制文本背景
                text_display = text[:20] + "..." if len(text) > 20 else text
                
                # 计算文本位置
                text_y = max(0, y1 - font_size - 5)
                
                # 绘制文本背景
                try:
                    bbox_text = draw.textbbox((x1, text_y), text_display, font=font)
                    draw.rectangle(bbox_text, fill=color)
                    draw.text((x1, text_y), text_display, fill=(255, 255, 255), font=font)
                except Exception as e:
                    logger.warning(f"绘制文本失败: {e}")
        
        logger.info(f"成功绘制{len(boxes)}个边界框")
        return img_with_boxes
    
    def clean_markdown(self, raw_text: str) -> str:
        """
        清理Markdown文本，移除定位标签
        
        Args:
            raw_text: 包含定位标签的原始文本
            
        Returns:
            清理后的Markdown文本
        """
        # 移除所有的 <|ref|>...<|/ref|><|det|>...<|/det|> 标记
        # 保留 <|ref|> 和 <|/ref|> 之间的文本
        clean_text = re.sub(
            r'<\|ref\|>(.*?)<\|/ref\|><\|det\|>.*?<\|/det\|>',
            r'\1',
            raw_text
        )
        
        # 移除其他可能的特殊标记
        clean_text = clean_text.replace('<|grounding|>', '')
        
        return clean_text.strip()
    
    def save_results(
        self,
        text: str,
        image: Optional[Image.Image],
        output_dir: str,
        prefix: str = "ocr_result"
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        保存结果文件
        
        Args:
            text: 识别的文本
            image: 可视化图像（可选）
            output_dir: 输出目录
            prefix: 文件名前缀
            
        Returns:
            (文本文件路径, 图像文件路径)
        """
        os.makedirs(output_dir, exist_ok=True)
        
        text_path = None
        image_path = None
        
        # 保存文本文件
        if text:
            text_path = os.path.join(output_dir, f"{prefix}.md")
            try:
                with open(text_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                logger.info(f"文本结果已保存至: {text_path}")
            except Exception as e:
                logger.error(f"保存文本文件失败: {e}")
                text_path = None
        
        # 保存图像文件
        if image:
            image_path = os.path.join(output_dir, f"{prefix}_visualization.jpg")
            try:
                image.save(image_path, format='JPEG', quality=95)
                logger.info(f"可视化图像已保存至: {image_path}")
            except Exception as e:
                logger.error(f"保存图像文件失败: {e}")
                image_path = None
        
        return text_path, image_path


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    processor = ResultProcessor()
    
    # 测试文本清理
    print("\n测试1: 文本清理")
    print("-" * 60)
    test_text = """<|ref|>标题<|/ref|><|det|>[[100,50],[300,100]]<|/det|>

这是一段<|ref|>普通文本<|/ref|><|det|>[[100,150],[400,200]]<|/det|>。"""
    
    print("原始文本:")
    print(test_text)
    print("\n清理后的文本:")
    print(processor.clean_markdown(test_text))
    
    # 测试边界框提取
    print("\n\n测试2: 边界框提取")
    print("-" * 60)
    boxes = processor.extract_bounding_boxes(test_text)
    print(f"提取到{len(boxes)}个边界框:")
    for idx, box in enumerate(boxes, 1):
        print(f"  {idx}. 文本: '{box['text']}', 坐标: {box['bbox']}")

