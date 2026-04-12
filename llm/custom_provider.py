"""自定义LLM提供商 - 支持本地模型和中转站"""
import requests
from typing import List, Dict, Any, Optional
from llm.base import LLMProvider


class CustomProvider(LLMProvider):
    """自定义LLM提供商
    
    支持:
    - 本地模型 (Ollama, LM Studio, etc.)
    - 中转站/代理服务
    - 任何OpenAI兼容API
    """
    
    def __init__(self, config):
        super().__init__(config)
        self.base_url = config.base_url or "http://localhost:11434"
        # 确保base_url以/v1结尾（OpenAI兼容格式）
        if not self.base_url.endswith('/v1'):
            self.base_url = self.base_url.rstrip('/') + '/v1'
        self.api_key = config.api_key or "sk-custom"
    
    def chat(self, messages: List[Dict[str, str]], timeout: int = 120, **kwargs) -> str:
        """对话接口"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        params = self._merge_params(**kwargs)
        
        data = {
            "model": self.config.model,
            "messages": messages,
            "temperature": params.get("temperature", 0.7),
            "max_tokens": params.get("max_tokens", 4096),
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=timeout
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            raise Exception(f"Custom API调用失败: {str(e)}")
    
    def chat_stream(self, messages: List[Dict[str, str]], **kwargs):
        """流式对话接口"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        params = self._merge_params(**kwargs)
        
        data = {
            "model": self.config.model,
            "messages": messages,
            "temperature": params.get("temperature", 0.7),
            "max_tokens": params.get("max_tokens", 4096),
            "stream": True
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                stream=True,
                timeout=120
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        line = line[6:]
                        if line == '[DONE]':
                            break
                        try:
                            import json
                            chunk = json.loads(line)
                            if "choices" in chunk and len(chunk["choices"]) > 0:
                                delta = chunk["choices"][0].get("delta", {})
                                if "content" in delta:
                                    yield delta["content"]
                        except:
                            pass
        except Exception as e:
            raise Exception(f"Custom API流式调用失败: {str(e)}")
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """文本嵌入接口"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 使用配置的嵌入模型，如果没有则使用对话模型
        embed_model = getattr(self.config, 'embed_model', None) or self.config.model
        
        embeddings = []
        for text in texts:
            data = {
                "model": embed_model,
                "input": text
            }
            
            try:
                response = requests.post(
                    f"{self.base_url}/embeddings",
                    headers=headers,
                    json=data,
                    timeout=60
                )
                response.raise_for_status()
                result = response.json()
                embeddings.append(result["data"][0]["embedding"])
            except Exception as e:
                # 如果嵌入API失败，返回零向量作为fallback
                print(f"嵌入API调用失败: {str(e)}")
                embeddings.append([0.0] * 1536)  # 默认维度
        
        return embeddings
    
    def get_models(self) -> List[Dict[str, Any]]:
        """获取可用模型列表"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            response = requests.get(
                f"{self.base_url}/models",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                models = []
                for model in data.get("data", []):
                    models.append({
                        "id": model.get("id", "unknown"),
                        "name": model.get("id", "Unknown Model"),
                        "context_length": 8192  # 默认值
                    })
                return models
        except:
            pass
        
        # 返回默认模型列表
        return [
            {"id": self.config.model, "name": self.config.model, "context_length": 8192},
            {"id": "llama2", "name": "Llama 2", "context_length": 4096},
            {"id": "mistral", "name": "Mistral", "context_length": 8192},
            {"id": "qwen", "name": "Qwen", "context_length": 8192},
        ]
    
    def test_connection(self) -> bool:
        """测试连接"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # 尝试获取模型列表
            response = requests.get(
                f"{self.base_url}/models",
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                return True
            
            # 如果获取模型列表失败，尝试简单对话
            response = self.chat([{"role": "user", "content": "Hi"}], timeout=10)
            return len(response) > 0
            
        except Exception as e:
            print(f"连接测试失败: {str(e)}")
            return False
