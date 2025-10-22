"""
Prompt构建模块
根据不同的OCR任务类型构建相应的Prompt
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


# Prompt模板字典
PROMPT_TEMPLATES: Dict[str, str] = {
    "文档转Markdown": "<image>\n<|grounding|>Convert the document to markdown.",
    "通用OCR": "<image>\n<|grounding|>OCR this image.",
    "纯文本提取": "<image>\nFree OCR.",
    "图表解析": "<image>\nParse the figure.",
    "图像描述": "<image>\nDescribe this image in detail.",
}


def build_prompt(task: str, custom_prompt: str = "") -> str:
    """
    根据任务类型构建Prompt
    
    Args:
        task: 任务类型，如"文档转Markdown"、"通用OCR"等
        custom_prompt: 自定义prompt内容（仅在task为"自定义Prompt"时使用）
        
    Returns:
        完整的prompt字符串
        
    Examples:
        >>> build_prompt("文档转Markdown")
        '<image>\\n<|grounding|>Convert the document to markdown.'
        
        >>> build_prompt("自定义Prompt", "识别图片中的所有数字")
        '<image>\\n识别图片中的所有数字'
    """
    # 处理自定义Prompt
    if task == "自定义Prompt":
        if not custom_prompt or not custom_prompt.strip():
            logger.warning("自定义Prompt为空，使用默认的文档转Markdown模板")
            prompt = PROMPT_TEMPLATES["文档转Markdown"]
        else:
            # 确保自定义prompt包含<image>标记
            if "<image>" not in custom_prompt:
                prompt = f"<image>\n{custom_prompt.strip()}"
            else:
                prompt = custom_prompt.strip()
            logger.info(f"使用自定义Prompt: {prompt}")
    else:
        # 使用预定义模板
        prompt = PROMPT_TEMPLATES.get(task, PROMPT_TEMPLATES["文档转Markdown"])
        logger.info(f"使用预定义Prompt模板: {task}")
    
    return prompt


def get_task_description(task: str) -> str:
    """
    获取任务类型的详细描述
    
    Args:
        task: 任务类型
        
    Returns:
        任务描述字符串
    """
    descriptions = {
        "文档转Markdown": "识别文档内容并转换为Markdown格式，保留文档结构和布局信息",
        "通用OCR": "识别图像中的所有文字内容，包含位置信息",
        "纯文本提取": "仅提取图像中的文字内容，忽略布局和格式",
        "图表解析": "识别和解析图表、图形、示意图等内容",
        "图像描述": "生成图像的详细文字描述",
        "自定义Prompt": "使用自定义的识别指令"
    }
    
    return descriptions.get(task, "未知任务类型")


def get_all_tasks() -> list:
    """
    获取所有支持的任务类型
    
    Returns:
        任务类型列表
    """
    return list(PROMPT_TEMPLATES.keys()) + ["自定义Prompt"]


def validate_prompt(prompt: str) -> tuple:
    """
    验证Prompt是否有效
    
    Args:
        prompt: 待验证的prompt字符串
        
    Returns:
        (是否有效, 错误消息)
    """
    if not prompt or not prompt.strip():
        return False, "Prompt不能为空"
    
    if "<image>" not in prompt:
        return False, "Prompt必须包含<image>标记"
    
    if len(prompt) > 1000:
        return False, "Prompt长度不能超过1000个字符"
    
    return True, ""


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 60)
    print("Prompt构建模块测试")
    print("=" * 60)
    
    # 测试所有预定义任务
    print("\n1. 预定义任务Prompt:")
    print("-" * 60)
    for task in get_all_tasks():
        if task != "自定义Prompt":
            prompt = build_prompt(task)
            description = get_task_description(task)
            print(f"\n任务: {task}")
            print(f"描述: {description}")
            print(f"Prompt: {prompt}")
    
    # 测试自定义Prompt
    print("\n\n2. 自定义Prompt测试:")
    print("-" * 60)
    
    test_cases = [
        ("识别图片中的所有数字", True),
        ("<image>\n提取表格数据", True),
        ("", False),  # 空prompt
        ("没有image标记的prompt", False),  # 缺少<image>标记
    ]
    
    for custom_text, should_succeed in test_cases:
        print(f"\n测试输入: '{custom_text}'")
        prompt = build_prompt("自定义Prompt", custom_text)
        is_valid, error_msg = validate_prompt(prompt)
        print(f"生成的Prompt: {prompt}")
        print(f"验证结果: {'✅ 有效' if is_valid else '❌ 无效'}")
        if error_msg:
            print(f"错误信息: {error_msg}")
    
    print("\n" + "=" * 60)

