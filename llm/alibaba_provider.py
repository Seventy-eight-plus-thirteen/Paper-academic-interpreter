"""阿里通义千问提供商实现"""
from typing import List, Dict, Any
import requests
from llm.base import LLMProvider
from models.config import ModuleConfig


class AlibabaProvider(LLMProvider):
    """阿里通义千问提供商"""
    
    def __init__(self, config: ModuleConfig):
        super().__init__(config)
        self.api_key = config.api_key
        self.base_url = config.base_url or "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    
    def chat(self, messages: List[Dict[str, str]], timeout: int = 120, **kwargs) -> str:
        """对话接口"""
        params = self._merge_params(**kwargs)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.config.model,
            "input": {
                "messages": messages
            },
            "parameters": {
                "temperature": params.get("temperature", 0.7),
                "top_p": params.get("top_p", 0.8),
                "max_tokens": params.get("max_tokens", 4096),
                "result_format": "message"
            }
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=timeout)
            result = response.json()
            
            if "output" in result and "choices" in result["output"]:
                return result["output"]["choices"][0]["message"]["content"]
            else:
                raise ValueError(f"API调用失败: {result}")
        except requests.exceptions.Timeout:
            raise ValueError(f"请求超时（{timeout}秒），请检查网络连接")
        except requests.exceptions.ConnectionError:
            raise ValueError("网络连接失败，请检查网络设置")
        except Exception as e:
            raise ValueError(f"阿里API调用异常: {str(e)}")
    
    def chat_stream(self, messages: List[Dict[str, str]], **kwargs):
        """流式对话接口"""
        params = self._merge_params(**kwargs)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        }
        
        data = {
            "model": self.config.model,
            "input": {
                "messages": messages
            },
            "parameters": {
                "temperature": params.get("temperature", 0.7),
                "top_p": params.get("top_p", 0.8),
                "max_tokens": params.get("max_tokens", 4096),
                "result_format": "message",
                "incremental_output": True
            }
        }
        
        response = requests.post(self.base_url, headers=headers, json=data, stream=True)
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data:'):
                    data_str = line[5:].strip()
                    if data_str == '[DONE]':
                        break
                    try:
                        import json
                        data = json.loads(data_str)
                        if 'output' in data and 'choices' in data['output']:
                            yield data['output']['choices'][0]['message']['content']
                    except:
                        pass
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """文本嵌入接口"""
        url = "https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        embeddings = []
        for text in texts:
            data = {
                "model": "text-embedding-v2",
                "input": {
                    "texts": [text]
                }
            }
            
            response = requests.post(url, headers=headers, json=data)
            result = response.json()
            
            if "output" in result and "embeddings" in result["output"]:
                embeddings.append(result["output"]["embeddings"][0]["embedding"])
            else:
                raise ValueError(f"嵌入失败: {result}")
        
        return embeddings
    
    def get_models(self) -> List[Dict[str, Any]]:
        """获取可用模型列表"""
        return [
            {"id": "qwen-max", "name": "Qwen Max", "context_length": 32768},
            {"id": "qwen-plus", "name": "Qwen Plus", "context_length": 32768},
            {"id": "qwen-turbo", "name": "Qwen Turbo", "context_length": 8192},
            {"id": "qwen-long", "name": "Qwen Long", "context_length": 1000000},
            {"id": "qwen-max-longcontext", "name": "Qwen Max Long", "context_length": 32768},
        ]
