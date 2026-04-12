"""配置管理模块"""
import os
import configparser
import keyring
from pathlib import Path
from typing import Optional
from models.config import AppConfig, ModuleConfig, LLMProviderType, OCRProviderType, OCRConfig, PPTConfig, PPTProviderType


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = "storage/config/config.ini"):
        self.config_file = Path(config_file)
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.config = configparser.ConfigParser()
        self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        if self.config_file.exists():
            self.config.read(self.config_file, encoding='utf-8')
    
    def _save_config(self):
        """保存配置文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)
    
    def get_app_config(self) -> AppConfig:
        """获取应用配置"""
        app_config = AppConfig()
        
        if self.config.has_section('app'):
            app_config.version = self.config.get('app', 'version', fallback='1.0.0')
            app_config.first_run = self.config.getboolean('app', 'first_run', fallback=True)
        
        # 加载 OCR 配置
        app_config.ocr = self._get_ocr_config()
        
        app_config.note_generator = self._get_module_config('note_generator')
        # PPT 配置使用新的 PPTConfig
        app_config.ppt_generator = self._get_ppt_config()
        app_config.mindmap_generator = self._get_module_config('mindmap_generator')
        app_config.rag_builder = self._get_module_config('rag_builder')
        app_config.embeddings = self._get_module_config('embeddings')
        
        if self.config.has_section('paths'):
            app_config.uploads_path = self.config.get('paths', 'uploads', fallback='storage/uploads')
            app_config.outputs_path = self.config.get('paths', 'outputs', fallback='storage/outputs')
            app_config.config_path = self.config.get('paths', 'config', fallback='storage/config')
        
        return app_config
    
    def _get_module_config(self, section: str) -> ModuleConfig:
        """获取模块配置"""
        if not self.config.has_section(section):
            return ModuleConfig(provider=LLMProviderType.OPENAI, model="", api_key="")
        
        provider_str = self.config.get(section, 'provider', fallback='openai')
        try:
            provider = LLMProviderType(provider_str)
        except ValueError:
            provider = LLMProviderType.OPENAI
        
        model = self.config.get(section, 'model', fallback='')
        
        # 首先尝试从 keyring 获取 API key
        service_name = f"paper_parser_{section}"
        api_key = keyring.get_password(service_name, "api_key")
        
        # 如果 keyring 中没有，尝试从配置文件读取
        if api_key is None:
            api_key = self.config.get(section, 'api_key', fallback="")
        
        base_url = self.config.get(section, 'base_url', fallback=None)
        temperature = self.config.getfloat(section, 'temperature', fallback=0.7)
        max_tokens = self.config.getint(section, 'max_tokens', fallback=4096)
        
        return ModuleConfig(
            provider=provider,
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    def save_app_config(self, app_config: AppConfig):
        """保存应用配置"""
        if not self.config.has_section('app'):
            self.config.add_section('app')
        self.config.set('app', 'version', app_config.version)
        self.config.set('app', 'first_run', str(app_config.first_run))
        
        # 保存 OCR 配置
        self._save_ocr_config(app_config.ocr)
        
        self._save_module_config('note_generator', app_config.note_generator)
        # PPT 配置使用新的保存方法
        self._save_ppt_config(app_config.ppt_generator)
        self._save_module_config('mindmap_generator', app_config.mindmap_generator)
        self._save_module_config('rag_builder', app_config.rag_builder)
        self._save_module_config('embeddings', app_config.embeddings)
        
        if not self.config.has_section('paths'):
            self.config.add_section('paths')
        self.config.set('paths', 'uploads', app_config.uploads_path)
        self.config.set('paths', 'outputs', app_config.outputs_path)
        self.config.set('paths', 'config', app_config.config_path)
        
        self._save_config()
    
    def _get_ocr_config(self) -> OCRConfig:
        """获取 OCR 配置"""
        if not self.config.has_section('ocr'):
            return OCRConfig(provider=OCRProviderType.LOCAL, api_key="")
        
        provider_str = self.config.get('ocr', 'provider', fallback='local')
        try:
            provider = OCRProviderType(provider_str)
        except ValueError:
            provider = OCRProviderType.LOCAL
        
        api_key = keyring.get_password("paper_parser_ocr", "api_key") or ""
        base_url = self.config.get('ocr', 'base_url', fallback=None)
        
        return OCRConfig(
            provider=provider,
            api_key=api_key,
            base_url=base_url
        )
    
    def _save_ocr_config(self, ocr_config: OCRConfig):
        """保存 OCR 配置"""
        if not self.config.has_section('ocr'):
            self.config.add_section('ocr')
        
        provider_value = ocr_config.provider.value if ocr_config.provider else "local"
        self.config.set('ocr', 'provider', provider_value)
        
        if ocr_config.base_url:
            self.config.set('ocr', 'base_url', ocr_config.base_url)
        
        keyring.set_password("paper_parser_ocr", "api_key", ocr_config.api_key or "")
    
    def _get_ppt_config(self) -> PPTConfig:
        """获取 PPT 配置"""
        if not self.config.has_section('ppt_generator'):
            return PPTConfig(provider=PPTProviderType.KIMI)
        
        provider_str = self.config.get('ppt_generator', 'provider', fallback='kimi')
        try:
            provider = PPTProviderType(provider_str)
        except ValueError:
            provider = PPTProviderType.KIMI
        
        api_key = keyring.get_password("paper_parser_ppt", "api_key") or ""
        base_url = self.config.get('ppt_generator', 'base_url', fallback=None)
        auto_open = self.config.getboolean('ppt_generator', 'auto_open_browser', fallback=True)
        auto_copy = self.config.getboolean('ppt_generator', 'auto_copy_prompt', fallback=True)
        
        return PPTConfig(
            provider=provider,
            api_key=api_key,
            base_url=base_url,
            auto_open_browser=auto_open,
            auto_copy_prompt=auto_copy
        )
    
    def _save_ppt_config(self, ppt_config: PPTConfig):
        """保存 PPT 配置"""
        if not self.config.has_section('ppt_generator'):
            self.config.add_section('ppt_generator')
        
        provider_value = ppt_config.provider.value if ppt_config.provider else "kimi"
        self.config.set('ppt_generator', 'provider', provider_value)
        self.config.set('ppt_generator', 'auto_open_browser', str(ppt_config.auto_open_browser))
        self.config.set('ppt_generator', 'auto_copy_prompt', str(ppt_config.auto_copy_prompt))
        
        if ppt_config.base_url:
            self.config.set('ppt_generator', 'base_url', ppt_config.base_url)
        
        keyring.set_password("paper_parser_ppt", "api_key", ppt_config.api_key or "")
    
    def _save_module_config(self, section: str, module_config: ModuleConfig):
        """保存模块配置"""
        if not self.config.has_section(section):
            self.config.add_section(section)
        
        # 确保provider不为None
        provider_value = module_config.provider.value if module_config.provider else "openai"
        self.config.set(section, 'provider', provider_value)
        self.config.set(section, 'model', module_config.model or "")
        self.config.set(section, 'temperature', str(module_config.temperature))
        self.config.set(section, 'max_tokens', str(module_config.max_tokens))
        
        if module_config.base_url:
            self.config.set(section, 'base_url', module_config.base_url)
        
        service_name = f"paper_parser_{section}"
        keyring.set_password(service_name, "api_key", module_config.api_key or "")
    
    def update_module_config(self, module_name: str, module_config: ModuleConfig):
        """更新单个模块配置"""
        self._save_module_config(module_name, module_config)
        self._save_config()
    
    def set_first_run(self, first_run: bool):
        """设置首次运行标志"""
        if not self.config.has_section('app'):
            self.config.add_section('app')
        self.config.set('app', 'first_run', str(first_run))
        self._save_config()
