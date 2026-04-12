"""智谱GLM提供商实现"""
from typing import List, Dict, Any
import requests
import jwt
import time
from llm.base import LLMProvider
from models.config import ModuleConfig


class ZhipuProvider(LLMProvider):
    """智谱GLM提供商"""
    
    def __init__(self, config: ModuleConfig):
        super().__init__(config)
        self.api_key = config.api_key
        self.base_url = config.base_url or "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        # 智谱AI的embedding API使用不同的端点
        self.embed_url = "https://open.bigmodel.cn/api/paas/v4/embeddings"
        print(f"智谱GLM初始化: model={config.model}")
    
    def _generate_token(self):
        """生成JWT token"""
        try:
            api_key_parts = self.api_key.split('.')
            if len(api_key_parts) != 2:
                print(f"API Key格式错误: 期望 id.secret 格式，实际: {self.api_key[:10]}...")
                return self.api_key
            
            api_id = api_key_parts[0]
            api_secret = api_key_parts[1]
            
            payload = {
                "api_key": api_id,
                "exp": int(time.time()) + 3600,
                "timestamp": int(time.time())
            }
            
            token = jwt.encode(payload, api_secret, algorithm="HS256")
            if isinstance(token, bytes):
                token = token.decode('utf-8')
            
            print(f"Token生成成功: {token[:50]}...")
            return token
        except Exception as e:
            print(f"生成token失败: {e}")
            import traceback
            print(f"详细错误: {traceback.format_exc()}")
            return self.api_key
    
    def chat(self, messages: List[Dict[str, str]], timeout: int = 120, **kwargs) -> str:
        """对话接口"""
        params = self._merge_params(**kwargs)
        
        print(f"智谱API调用: URL={self.base_url}, model={self.config.model}, timeout={timeout}s")
        
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
            
            print(f"智谱API响应状态: {response.status_code}")
            
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                error_msg = result.get("error", {}).get("message", str(result))
                raise ValueError(f"API调用失败: {error_msg}")
        except requests.exceptions.Timeout:
            raise ValueError(f"请求超时（{timeout}秒），请检查网络连接")
        except requests.exceptions.ConnectionError:
            raise ValueError("网络连接失败，请检查网络设置")
        except Exception as e:
            raise ValueError(f"智谱API调用异常: {str(e)}")
    
    def chat_stream(self, messages: List[Dict[str, str]], **kwargs):
        """流式对话接口"""
        params = self._merge_params(**kwargs)
        
        headers = {
            "Authorization": f"Bearer {self._generate_token()}",
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
        
        # 智谱embedding API需要使用专门的embedding模型
        # 如果当前模型是chat模型，则使用默认的embedding-2
        embedding_model = self.config.model
        if not embedding_model.startswith("embedding"):
            embedding_model = "embedding-2"
        
        data = {
            "model": embedding_model,
            "input": texts
        }
        
        try:
            print(f"智谱嵌入API调用: URL={self.embed_url}, model={embedding_model}, 文本数={len(texts)}")
            response = requests.post(self.embed_url, headers=headers, json=data, timeout=120)
            result = response.json()
            
            print(f"智谱嵌入API响应状态: {response.status_code}")
            
            if "data" in result:
                return [item["embedding"] for item in result["data"]]
            else:
                error_msg = result.get("error", {}).get("message", str(result))
                raise ValueError(f"嵌入失败: {error_msg}")
        except requests.exceptions.Timeout:
            raise ValueError(f"请求超时（120秒），请检查网络连接")
        except requests.exceptions.ConnectionError:
            raise ValueError("网络连接失败，请检查网络设置")
        except Exception as e:
            raise ValueError(f"智谱嵌入API调用异常: {str(e)}")
    
    def get_models(self) -> List[Dict[str, Any]]:
        """获取可用模型列表"""
        return [
            {"id": "glm-4", "name": "GLM-4", "context_length": 128000},
            {"id": "glm-4-air", "name": "GLM-4 Air", "context_length": 128000},
            {"id": "glm-4-flash", "name": "GLM-4 Flash", "context_length": 128000},
            {"id": "glm-4-plus", "name": "GLM-4 Plus", "context_length": 128000},
            {"id": "glm-3-turbo", "name": "GLM-3 Turbo", "context_length": 128000},
            {"id": "glm-4v", "name": "GLM-4V (视觉)", "context_length": 8192},
            {"id": "glm-4-alltools", "name": "GLM-4 AllTools", "context_length": 128000},
            {"id": "embedding-2", "name": "Embedding-2", "context_length": 8192},
            {"id": "embedding-3", "name": "Embedding-3", "context_length": 8192},
        ]
