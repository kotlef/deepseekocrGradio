#!/usr/bin/env python3
"""
模块功能测试脚本
"""

import sys
import os
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules import (
    ModelManager,
    ImageProcessor,
    build_prompt,
    get_task_description,
    get_all_tasks,
    ResultProcessor
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_model_manager():
    """测试模型管理器"""
    print("\n" + "=" * 60)
    print("测试1: 模型管理器")
    print("=" * 60)
    
    try:
        manager = ModelManager()
        info = manager.get_model_info()
        
        print("\n模型信息:")
        for key, value in info.items():
            print(f"  {key}: {value}")
        
        print("\n✅ 模型管理器测试通过")
        return True
    except Exception as e:
        print(f"\n❌ 模型管理器测试失败: {e}")
        return False


def test_image_processor():
    """测试图像处理器"""
    print("\n" + "=" * 60)
    print("测试2: 图像处理器")
    print("=" * 60)
    
    try:
        processor = ImageProcessor()
        
        # 测试分辨率参数获取
        print("\n分辨率模式参数:")
        test_modes = [
            "Tiny (512×512) - 快速",
            "Small (640×640) - 中等",
            "Base (1024×1024) - 推荐",
            "Large (1280×1280) - 高质量",
            "Gundam (动态) - 大图像"
        ]
        
        for mode in test_modes:
            base_size, image_size, crop_mode = processor.get_resolution_params(mode)
            print(f"  {mode}:")
            print(f"    base_size={base_size}, image_size={image_size}, crop_mode={crop_mode}")
        
        print("\n✅ 图像处理器测试通过")
        return True
    except Exception as e:
        print(f"\n❌ 图像处理器测试失败: {e}")
        return False


def test_prompt_builder():
    """测试Prompt构建器"""
    print("\n" + "=" * 60)
    print("测试3: Prompt构建器")
    print("=" * 60)
    
    try:
        # 测试所有任务类型
        print("\n支持的任务类型:")
        for task in get_all_tasks():
            prompt = build_prompt(task)
            description = get_task_description(task)
            print(f"\n  任务: {task}")
            print(f"  描述: {description}")
            print(f"  Prompt: {prompt[:50]}...")
        
        # 测试自定义Prompt
        print("\n\n自定义Prompt测试:")
        custom_text = "识别图片中的所有数字"
        prompt = build_prompt("自定义Prompt", custom_text)
        print(f"  输入: {custom_text}")
        print(f"  生成: {prompt}")
        
        print("\n✅ Prompt构建器测试通过")
        return True
    except Exception as e:
        print(f"\n❌ Prompt构建器测试失败: {e}")
        return False


def test_result_processor():
    """测试结果处理器"""
    print("\n" + "=" * 60)
    print("测试4: 结果处理器")
    print("=" * 60)
    
    try:
        processor = ResultProcessor()
        
        # 测试文本清理
        test_text = """<|ref|>标题<|/ref|><|det|>[[100,50],[300,100]]<|/det|>

这是一段<|ref|>普通文本<|/ref|><|det|>[[100,150],[400,200]]<|/det|>。"""
        
        print("\n原始文本:")
        print(test_text)
        
        clean_text = processor.clean_markdown(test_text)
        print("\n清理后的文本:")
        print(clean_text)
        
        # 测试边界框提取
        boxes = processor.extract_bounding_boxes(test_text)
        print(f"\n提取到{len(boxes)}个边界框:")
        for idx, box in enumerate(boxes, 1):
            print(f"  {idx}. 文本: '{box['text']}', 坐标: {box['bbox']}")
        
        print("\n✅ 结果处理器测试通过")
        return True
    except Exception as e:
        print(f"\n❌ 结果处理器测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("=" * 60)
    print("DeepSeek-OCR Gradio应用 - 模块功能测试")
    print("=" * 60)
    
    results = []
    
    # 运行所有测试
    results.append(("模型管理器", test_model_manager()))
    results.append(("图像处理器", test_image_processor()))
    results.append(("Prompt构建器", test_prompt_builder()))
    results.append(("结果处理器", test_result_processor()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "-" * 60)
    print(f"总计: {len(results)}个测试, {passed}个通过, {failed}个失败")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

