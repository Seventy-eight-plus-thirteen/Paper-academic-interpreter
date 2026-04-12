"""百度文心一言提供商实现"""
from typing import List, Dict, Any
import requests
from llm.base import LLMProvider
from models.config import ModuleConfig


class BaiduProvider(LLMProvider):
    """百度文心一言提供商"""
    
    def __init__(self, config: ModuleConfig):
        super().__init__(config)
        self.api_key = config.api_key
        self.secret_key = config.base_url or ""
        self.access_token = None
        self._get_access_token()
    
    def _get_access_token(self):
        """获取访问令牌"""
        if not self.secret_key:
            raise ValueError("百度文心一言需要配置Secret Key")
        
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key
        }
        
        response = requests.post(url, params=params)
        result = response.json()
        
        if "access_token" in result:
            self.access_token = result["access_token"]
        else:
            raise ValueError(f"获取访问令牌失败: {result}")
    
    def chat(self, messages: List[Dict[str, str]], timeout: int = 120, **kwargs) -> str:
        """对话接口"""
        if not self.access_token:
            self._get_access_token()
        
        params = self._merge_params(**kwargs)
        
        url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/{self.config.model}"
        headers = {"Content-Type": "application/json"}
        data = {
            "messages": messages,
            "temperature": params.get("temperature", 0.7),
            "top_p": params.get("top_p", 0.8),
            "max_output_tokens": params.get("max_tokens", 4096)
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=timeout)
            result = response.json()
            
            if "result" in result:
                return result["result"]
            else:
                raise ValueError(f"API调用失败: {result}")
        except requests.exceptions.Timeout:
            raise ValueError(f"请求超时（{timeout}秒），请检查网络连接")
        except requests.exceptions.ConnectionError:
            raise ValueError("网络连接失败，请检查网络设置")
        except Exception as e:
            raise ValueError(f"百度API调用异常: {str(e)}")
    
    def chat_stream(self, messages: List[Dict[str, str]], **kwargs):
        """流式对话接口"""
        if not self.access_token:
            self._get_access_token()
        
        params = self._merge_params(**kwargs)
        
        url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/{self.config.model}"
        headers = {"Content-Type": "application/json"}
        data = {
            "messages": messages,
            "temperature": params.get("temperature", 0.7),
            "top_p": params.get("top_p", 0.8),
            "max_output_tokens": params.get("max_tokens", 4096),
            "stream": True
        }
        
        response = requests.post(url, headers=headers, json=data, stream=True)
        
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
                        if 'result' in data:
                            yield data['result']
                    except:
                        pass
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """文本嵌入接口"""
        if not self.access_token:
            self._get_access_token()
        
        url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/embeddings/embedding-v1"
        headers = {"Content-Type": "application/json"}
        
        embeddings = []
        for text in texts:
            data = {"input": text}
            response = requests.post(url, headers=headers, json=data)
            result = response.json()
            
            if "data" in result and len(result["data"]) > 0:
                embeddings.append(result["data"][0]["embedding"])
            else:
                raise ValueError(f"嵌入失败: {result}")
        
        return embeddings
    
    def get_models(self) -> List[Dict[str, Any]]:
        """获取可用模型列表"""
        return [
            {"id": "ernie-4.0-8k", "name": "ERNIE 4.0 8K", "context_length": 8192},
            {"id": "ernie-4.0-32k", "name": "ERNIE 4.0 32K", "context_length": 32768},
            {"id": "ernie-3.5-8k", "name": "ERNIE 3.5 8K", "context_length": 8192},
            {"id": "ernie-3.5-128k", "name": "ERNIE 3.5 128K", "context_length": 128000},
            {"id": "ernie-speed-8k", "name": "ERNIE Speed 8K", "context_length": 8192},
            {"id": "ernie-speed-128k", "name": "ERNIE Speed 128K", "context_length": 128000},
            {"id": "ernie-lite-8k", "name": "ERNIE Lite 8K", "context_length": 8192},
            {"id": "ernie-tiny-8k", "name": "ERNIE Tiny 8K", "context_length": 8192},
        ]
