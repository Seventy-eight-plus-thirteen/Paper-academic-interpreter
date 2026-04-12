"""配置数据模型"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from enum import Enum


class LLMProviderType(Enum):
    """LLM提供商类型"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    BAIDU = "baidu"
    ALIBABA = "alibaba"
    ZHIPU = "zhipu"
    DEEPSEEK = "deepseek"
    KIMI = "kimi"
    OLLAMA = "ollama"
    CUSTOM = "custom"  # 自定义/本地模型/中转站


class OCRProviderType(Enum):
    """OCR提供商类型"""
    LOCAL = "local"  # 本地 pdfplumber
    ZHIPU = "zhipu"  # 智谱 AI OCR
    BAIDU = "baidu"  # 百度 OCR
    TENCENT = "tencent"  # 腾讯云 OCR
    CUSTOM = "custom"  # 自定义 OCR 服务


class PPTProviderType(Enum):
    """PPT生成提供商类型"""
    KIMI = "kimi"           # Kimi PPT助手 https://www.kimi.com/slides
    GAMMA = "gamma"         # Gamma https://gamma.app
    CANVA = "canva"         # Canva https://www.canva.com
    BEAUTIFUL_AI = "beautiful_ai"  # Beautiful.ai
    LOCAL_HTML = "local_html"      # 本地生成HTML PPT
    CUSTOM = "custom"       # 自定义服务


@dataclass
class ModuleConfig:
    """模块配置"""
    provider: LLMProviderType
    model: str
    api_key: str
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096
    extra_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OCRConfig:
    """OCR 配置"""
    provider: OCRProviderType = OCRProviderType.LOCAL
    api_key: str = ""
    base_url: Optional[str] = None
    extra_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PPTConfig:
    """PPT生成配置"""
    provider: PPTProviderType = PPTProviderType.KIMI
    # 针对不同网站的配置
    api_key: str = ""  # 部分网站需要API Key
    base_url: Optional[str] = None  # 自定义服务URL
    # 生成选项
    auto_open_browser: bool = True  # 是否自动打开浏览器
    auto_copy_prompt: bool = True   # 是否自动复制提示词到剪贴板
    # 额外参数
    extra_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AppConfig:
    """应用配置"""
    version: str = "1.0.0"
    first_run: bool = True
    
    # OCR 配置
    ocr: OCRConfig = field(default_factory=lambda: OCRConfig(
        provider=OCRProviderType.LOCAL,
        api_key=""
    ))
    
    note_generator: ModuleConfig = field(default_factory=lambda: ModuleConfig(
        provider=LLMProviderType.OPENAI,
        model="gpt-4",
        api_key=""
    ))
    
    # 思维导图生成配置
    mindmap_generator: ModuleConfig = field(default_factory=lambda: ModuleConfig(
        provider=LLMProviderType.OPENAI,
        model="gpt-4",
        api_key=""
    ))
    
    # PPT生成配置（使用新的PPTConfig）
    ppt_generator: PPTConfig = field(default_factory=lambda: PPTConfig(
        provider=PPTProviderType.KIMI,
        auto_open_browser=True,
        auto_copy_prompt=True
    ))
    
    rag_builder: ModuleConfig = field(default_factory=lambda: ModuleConfig(
        provider=LLMProviderType.OPENAI,
        model="gpt-4",
        api_key=""
    ))
    
    embeddings: ModuleConfig = field(default_factory=lambda: ModuleConfig(
        provider=LLMProviderType.OPENAI,
        model="text-embedding-ada-002",
        api_key=""
    ))
    
    uploads_path: str = "storage/uploads"
    outputs_path: str = "storage/outputs"
    config_path: str = "storage/config"
