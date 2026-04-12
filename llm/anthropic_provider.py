"""Anthropic Claude提供商实现"""
from typing import List, Dict, Any
import anthropic
from llm.base import LLMProvider
from models.config import ModuleConfig


class AnthropicProvider(LLMProvider):
    """Anthropic Claude提供商"""
    
    def __init__(self, config: ModuleConfig):
        super().__init__(config)
        self.client = anthropic.Anthropic(api_key=config.api_key)
    
    def chat(self, messages: List[Dict[str, str]], timeout: int = 120, **kwargs) -> str:
        """对话接口"""
        params = self._merge_params(**kwargs)
        
        system_message = ""
        user_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                user_messages.append(msg)
        
        response = self.client.messages.create(
            model=self.config.model,
            system=system_message,
            messages=user_messages,
            max_tokens=params.get("max_tokens", 4096),
            temperature=params.get("temperature", 0.7),
            timeout=timeout
        )
        return response.content[0].text
    
    def chat_stream(self, messages: List[Dict[str, str]], **kwargs):
        """流式对话接口"""
        params = self._merge_params(**kwargs)
        
        system_message = ""
        user_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                user_messages.append(msg)
        
        with self.client.messages.stream(
            model=self.config.model,
            system=system_message,
            messages=user_messages,
            max_tokens=params.get("max_tokens", 4096),
            temperature=params.get("temperature", 0.7)
        ) as stream:
            for text in stream.text_stream:
                yield text
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """文本嵌入接口
        
        Claude不提供原生嵌入API，使用简单的哈希方法
        """
        import hashlib
        embeddings = []
        for text in texts:
            hash_obj = hashlib.md5(text.encode())
            hash_bytes = hash_obj.digest()
            vector = []
            for i in range(1536):
                byte_val = hash_bytes[i % 16]
                vector.append((byte_val / 255.0) * 2 - 1)
            embeddings.append(vector)
        return embeddings
    
    def get_models(self) -> List[Dict[str, Any]]:
        """获取可用模型列表"""
        return [
            {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus", "context_length": 200000},
            {"id": "claude-3-sonnet-20240229", "name": "Claude 3 Sonnet", "context_length": 200000},
            {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku", "context_length": 200000},
            {"id": "claude-2.1", "name": "Claude 2.1", "context_length": 200000},
            {"id": "claude-2.0", "name": "Claude 2.0", "context_length": 100000},
        ]
