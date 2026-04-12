"""LLM提供商基类"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from models.config import ModuleConfig


class LLMProvider(ABC):
    """LLM提供商基类"""
    
    def __init__(self, config: ModuleConfig):
        self.config = config
        self.provider_name = config.provider.value
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], timeout: int = 120, **kwargs) -> str:
        """对话接口
        
        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            timeout: 超时时间（秒），默认120秒
            **kwargs: 额外参数
            
        Returns:
            str: 模型回复
        """
        pass
    
    @abstractmethod
    def chat_stream(self, messages: List[Dict[str, str]], **kwargs):
        """流式对话接口
        
        Args:
            messages: 消息列表
            **kwargs: 额外参数
            
        Yields:
            str: 流式回复片段
        """
        pass
    
    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        """文本嵌入接口
        
        Args:
            texts: 文本列表
            
        Returns:
            List[List[float]]: 嵌入向量列表
        """
        pass
    
    @abstractmethod
    def get_models(self) -> List[Dict[str, Any]]:
        """获取可用模型列表
        
        Returns:
            List[Dict]: 模型信息列表，每个模型包含 id, name, context_length 等
        """
        pass
    
    def test_connection(self) -> bool:
        """测试连接
        
        Returns:
            bool: 连接是否成功
        """
        try:
            response = self.chat([{"role": "user", "content": "你好"}])
            return len(response) > 0
        except Exception as e:
            print(f"连接测试失败: {str(e)}")
            return False
    
    def _merge_params(self, **kwargs) -> Dict[str, Any]:
        """合并参数
        
        Returns:
            Dict: 合并后的参数
        """
        params = {
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }
        params.update(self.config.extra_params)
        params.update(kwargs)
        return params
