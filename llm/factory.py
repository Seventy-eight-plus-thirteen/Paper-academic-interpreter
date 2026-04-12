"""LLM提供商工厂"""
from typing import Dict, Type
from llm.base import LLMProvider
from llm.openai_provider import OpenAIProvider
from llm.anthropic_provider import AnthropicProvider
from llm.baidu_provider import BaiduProvider
from llm.alibaba_provider import AlibabaProvider
from llm.zhipu_provider import ZhipuProvider
from llm.deepseek_provider import DeepSeekProvider
from llm.kimi_provider import KimiProvider
from llm.custom_provider import CustomProvider
from models.config import ModuleConfig, LLMProviderType


class LLMProviderFactory:
    """LLM提供商工厂"""
    
    _providers: Dict[LLMProviderType, Type[LLMProvider]] = {
        LLMProviderType.OPENAI: OpenAIProvider,
        LLMProviderType.ANTHROPIC: AnthropicProvider,
        LLMProviderType.BAIDU: BaiduProvider,
        LLMProviderType.ALIBABA: AlibabaProvider,
        LLMProviderType.ZHIPU: ZhipuProvider,
        LLMProviderType.DEEPSEEK: DeepSeekProvider,
        LLMProviderType.KIMI: KimiProvider,
        LLMProviderType.CUSTOM: CustomProvider,
    }
    
    @classmethod
    def create(cls, config: ModuleConfig) -> LLMProvider:
        """创建LLM提供商实例
        
        Args:
            config: 模块配置
            
        Returns:
            LLMProvider: LLM提供商实例
        """
        provider_class = cls._providers.get(config.provider)
        if provider_class is None:
            raise ValueError(f"Unsupported provider: {config.provider}")
        return provider_class(config)
    
    @classmethod
    def register_provider(cls, provider_type: LLMProviderType, provider_class: Type[LLMProvider]):
        """注册新的提供商
        
        Args:
            provider_type: 提供商类型
            provider_class: 提供商类
        """
        cls._providers[provider_type] = provider_class
    
    @classmethod
    def get_available_providers(cls) -> list:
        """获取可用的提供商列表
        
        Returns:
            list: 提供商类型列表
        """
        return list(cls._providers.keys())
