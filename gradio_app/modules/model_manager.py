"""
模型管理模块
负责DeepSeek-OCR模型的加载、初始化和设备管理
"""

import torch
import logging
from typing import Optional, Dict
from transformers import AutoModel, AutoTokenizer

logger = logging.getLogger(__name__)


class ModelManager:
    """DeepSeek-OCR模型管理器"""
    
    def __init__(self, model_name: str = 'deepseek-ai/DeepSeek-OCR'):
        """
        初始化模型管理器
        
        Args:
            model_name: HuggingFace模型名称或本地路径
        """
        self.model_name = model_name
        self.device = self._detect_device()
        self.dtype = self._get_dtype()
        self.model = None
        self.tokenizer = None
        self._is_loaded = False
        
        logger.info(f"模型管理器初始化完成")
        logger.info(f"模型名称: {self.model_name}")
        logger.info(f"设备: {self.device}")
        logger.info(f"数据类型: {self.dtype}")
    
    def _detect_device(self) -> str:
        """
        检测可用的计算设备

        Returns:
            设备名称: 'cpu' (强制使用 CPU，因为 MPS 存在兼容性问题)
        """
        # 强制使用 CPU，因为在 Mac M2 上 MPS 存在严重的兼容性问题：
        # 1. 内存泄漏
        # 2. 无限循环输出
        # 3. 不支持某些操作符
        logger.info("强制使用 CPU 设备（Mac M2 上 MPS 存在兼容性问题）")
        return 'cpu'
    
    def _get_dtype(self) -> torch.dtype:
        """
        根据设备获取合适的数据类型
        
        Returns:
            torch数据类型
        """
        if self.device == 'cuda':
            # CUDA设备可以使用bfloat16
            return torch.bfloat16
        else:
            # MPS和CPU使用float32
            return torch.float32
    
    def load_model(self) -> None:
        """
        加载模型和分词器
        
        Raises:
            Exception: 模型加载失败时抛出异常
        """
        if self._is_loaded:
            logger.info("模型已加载，跳过重复加载")
            return
        
        try:
            logger.info("开始加载分词器...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            logger.info("分词器加载成功")
            
            logger.info("开始加载模型...")
            # 根据设备选择是否使用flash_attention_2
            if self.device == 'cuda':
                # CUDA设备可以尝试使用flash_attention_2
                try:
                    self.model = AutoModel.from_pretrained(
                        self.model_name,
                        _attn_implementation='flash_attention_2',
                        trust_remote_code=True,
                        use_safetensors=True
                    )
                    logger.info("使用 Flash Attention 2")
                except Exception as e:
                    logger.warning(f"Flash Attention 2 不可用，使用默认注意力机制: {e}")
                    self.model = AutoModel.from_pretrained(
                        self.model_name,
                        trust_remote_code=True,
                        use_safetensors=True
                    )
            else:
                # MPS和CPU使用默认注意力机制
                # 对于非CUDA设备，强制使用float32避免类型不匹配
                if self.device != 'cuda':
                    self.model = AutoModel.from_pretrained(
                        self.model_name,
                        trust_remote_code=True,
                        use_safetensors=True,
                        torch_dtype=torch.float32
                    )
                else:
                    self.model = AutoModel.from_pretrained(
                        self.model_name,
                        trust_remote_code=True,
                        use_safetensors=True
                    )

            logger.info("模型加载成功")

            # 设置为评估模式
            self.model = self.model.eval()

            # 对于非CUDA设备，强制转换所有参数为float32
            if self.device != 'cuda':
                logger.info(f"转换模型数据类型为 {self.dtype}...")
                # 递归转换所有参数和缓冲区
                def convert_to_float32(module):
                    for param in module.parameters():
                        param.data = param.data.to(torch.float32)
                    for buffer_name, buffer in module.named_buffers():
                        if buffer is not None:
                            module._buffers[buffer_name] = buffer.to(torch.float32)

                convert_to_float32(self.model)
                logger.info("所有模型参数已转换为 float32")

            # 移动到目标设备
            logger.info(f"将模型移动到 {self.device} 设备...")
            self.model = self.model.to(self.device)

            logger.info("模型设备和数据类型设置完成")
            
            self._is_loaded = True
            logger.info("✅ 模型加载完成！")
            
        except Exception as e:
            logger.error(f"❌ 模型加载失败: {e}")
            self._is_loaded = False
            raise Exception(f"模型加载失败: {str(e)}")
    
    def is_loaded(self) -> bool:
        """
        检查模型是否已加载
        
        Returns:
            True if模型已加载，否则False
        """
        return self._is_loaded
    
    def get_model_info(self) -> Dict[str, str]:
        """
        获取模型信息
        
        Returns:
            包含模型信息的字典
        """
        return {
            "model_name": self.model_name,
            "device": self.device,
            "dtype": str(self.dtype),
            "is_loaded": str(self._is_loaded),
            "torch_version": torch.__version__
        }
    
    def unload_model(self) -> None:
        """
        卸载模型以释放内存
        """
        if self._is_loaded:
            logger.info("开始卸载模型...")
            del self.model
            del self.tokenizer
            self.model = None
            self.tokenizer = None
            self._is_loaded = False
            
            # 清理GPU缓存
            if self.device == 'cuda':
                torch.cuda.empty_cache()
            elif self.device == 'mps':
                torch.mps.empty_cache()
            
            logger.info("模型已卸载")
        else:
            logger.info("模型未加载，无需卸载")
    
    def get_model(self):
        """
        获取模型实例
        
        Returns:
            模型实例
            
        Raises:
            RuntimeError: 如果模型未加载
        """
        if not self._is_loaded:
            raise RuntimeError("模型未加载，请先调用 load_model()")
        return self.model
    
    def get_tokenizer(self):
        """
        获取分词器实例
        
        Returns:
            分词器实例
            
        Raises:
            RuntimeError: 如果分词器未加载
        """
        if not self._is_loaded:
            raise RuntimeError("分词器未加载，请先调用 load_model()")
        return self.tokenizer


# 全局模型管理器实例（单例模式）
_global_model_manager: Optional[ModelManager] = None


def get_model_manager(model_name: str = 'deepseek-ai/DeepSeek-OCR') -> ModelManager:
    """
    获取全局模型管理器实例（单例模式）
    
    Args:
        model_name: 模型名称
        
    Returns:
        ModelManager实例
    """
    global _global_model_manager
    
    if _global_model_manager is None:
        _global_model_manager = ModelManager(model_name)
    
    return _global_model_manager


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建模型管理器
    manager = ModelManager()
    
    # 打印模型信息
    print("\n模型信息:")
    for key, value in manager.get_model_info().items():
        print(f"  {key}: {value}")
    
    # 加载模型
    print("\n开始加载模型...")
    try:
        manager.load_model()
        print("✅ 模型加载成功！")
        
        # 再次打印模型信息
        print("\n加载后的模型信息:")
        for key, value in manager.get_model_info().items():
            print(f"  {key}: {value}")
            
    except Exception as e:
        print(f"❌ 模型加载失败: {e}")

