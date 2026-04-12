"""Kimi提供商实现"""
from typing import List, Dict, Any
import requests
from llm.base import LLMProvider
from models.config import ModuleConfig


class KimiProvider(LLMProvider):
    """Kimi提供商"""
    
    def __init__(self, config: ModuleConfig):
        super().__init__(config)
        self.api_key = config.api_key
        self.base_url = config.base_url or "https://api.moonshot.cn/v1/chat/completions"
        self.embed_url = "https://api.moonshot.cn/v1/embeddings"
    
    def chat(self, messages: List[Dict[str, str]], timeout: int = 120, **kwargs) -> str:
        """对话接口"""
        params = self._merge_params(**kwargs)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.config.model,
            "messages": messages,
            "temperature": params.get("temperature", 0.7),
            "top_p": params.get("top_p", 0.7),
            "max_tokens": params.get("max_tokens", 4096)
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=timeout)
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                raise ValueError(f"API调用失败: {result}")
        except requests.exceptions.Timeout:
            raise ValueError(f"请求超时（{timeout}秒），请检查网络连接")
        except requests.exceptions.ConnectionError:
            raise ValueError("网络连接失败，请检查网络设置")
        except Exception as e:
            raise ValueError(f"Kimi API调用异常: {str(e)}")
    
    def chat_stream(self, messages: List[Dict[str, str]], **kwargs):
        """流式对话接口"""
        params = self._merge_params(**kwargs)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.config.model,
            "messages": messages,
            "temperature": params.get("temperature", 0.7),
            "top_p": params.get("top_p", 0.7),
            "max_tokens": params.get("max_tokens", 4096),
            "stream": True
        }
        
        response = requests.post(self.base_url, headers=headers, json=data, stream=True)
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data_str = line[6:]
                    if data_str == '[DONE]':
                        break
                    try:
                        import json
                        data = json.loads(data_str)
                        if 'choices' in data and len(data['choices']) > 0:
                            delta = data['choices'][0].get('delta', {})
                            if 'content' in delta:
                                yield delta['content']
                    except:
                        pass
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """文本嵌入接口"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "moonshot-v1-8k",
            "input": texts
        }
        
        response = requests.post(self.embed_url, headers=headers, json=data)
        result = response.json()
        
        if "data" in result:
            return [item["embedding"] for item in result["data"]]
        else:
            raise ValueError(f"嵌入失败: {result}")
    
    def get_models(self) -> List[Dict[str, Any]]:
        """获取可用模型列表"""
        return [
            {"id": "moonshot-v1-8k", "name": "Moonshot v1 8K", "context_length": 8192},
            {"id": "moonshot-v1-32k", "name": "Moonshot v1 32K", "context_length": 32768},
            {"id": "moonshot-v1-128k", "name": "Moonshot v1 128K", "context_length": 128000},
        ]
