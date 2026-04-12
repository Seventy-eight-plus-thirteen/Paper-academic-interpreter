"""OpenAI提供商实现"""
from typing import List, Dict, Any
import openai
from llm.base import LLMProvider
from models.config import ModuleConfig


class OpenAIProvider(LLMProvider):
    """OpenAI提供商"""
    
    def __init__(self, config: ModuleConfig):
        super().__init__(config)
        self.client = openai.OpenAI(
            api_key=config.api_key,
            base_url=config.base_url
        )
    
    def chat(self, messages: List[Dict[str, str]], timeout: int = 120, **kwargs) -> str:
        """对话接口"""
        params = self._merge_params(**kwargs)
        params['timeout'] = timeout
        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            **params
        )
        return response.choices[0].message.content
    
    def chat_stream(self, messages: List[Dict[str, str]], **kwargs):
        """流式对话接口"""
        params = self._merge_params(**kwargs)
        stream = self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            stream=True,
            **params
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """文本嵌入接口"""
        response = self.client.embeddings.create(
            model=self.config.model,
            input=texts
        )
        return [item.embedding for item in response.data]
    
    def get_models(self) -> List[Dict[str, Any]]:
        """获取可用模型列表"""
        models = [
            {"id": "gpt-4", "name": "GPT-4", "context_length": 8192},
            {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "context_length": 128000},
            {"id": "gpt-4-turbo-preview", "name": "GPT-4 Turbo Preview", "context_length": 128000},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "context_length": 16385},
            {"id": "gpt-3.5-turbo-16k", "name": "GPT-3.5 Turbo 16K", "context_length": 16385},
        ]
        
        embedding_models = [
            {"id": "text-embedding-ada-002", "name": "Ada Embedding", "context_length": 8191},
            {"id": "text-embedding-3-small", "name": "Embedding 3 Small", "context_length": 8191},
            {"id": "text-embedding-3-large", "name": "Embedding 3 Large", "context_length": 8191},
        ]
        
        return models + embedding_models
