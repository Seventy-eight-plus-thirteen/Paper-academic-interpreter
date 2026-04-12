"""设置对话框"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QLineEdit, QPushButton, QMessageBox,
    QTabWidget, QWidget, QFormLayout, QSpinBox, QDoubleSpinBox
)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.config import LLMProviderType, ModuleConfig, OCRProviderType, PPTConfig
from llm.factory import LLMProviderFactory
from ui.ocr_settings_widget import OCRSettingsWidget
from ui.ppt_settings_widget import PPTSettingsWidget


class ModuleSettingsWidget(QWidget):
    """模块设置组件"""
    
    def __init__(self, module_name, config: ModuleConfig):
        super().__init__()
        self.module_name = module_name
        self.config = config
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QFormLayout()
        
        self.provider_combo = QComboBox()
        providers = LLMProviderFactory.get_available_providers()
        for provider in providers:
            self.provider_combo.addItem(provider.value, provider)
        self.provider_combo.currentIndexChanged.connect(self.on_provider_changed)
        layout.addRow("提供商:", self.provider_combo)
        
        self.model_combo = QComboBox()
        layout.addRow("模型:", self.model_combo)
        
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("API Key:", self.api_key_edit)
        
        self.base_url_edit = QLineEdit()
        layout.addRow("Base URL (可选):", self.base_url_edit)
        
        self.temperature_spin = QDoubleSpinBox()
        self.temperature_spin.setRange(0.0, 2.0)
        self.temperature_spin.setSingleStep(0.1)
        layout.addRow("温度:", self.temperature_spin)
        
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(100, 128000)
        layout.addRow("最大Token:", self.max_tokens_spin)
        
        test_btn = QPushButton("测试连接")
        test_btn.clicked.connect(self.test_connection)
        layout.addRow(test_btn)
        
        self.setLayout(layout)
        self.load_config()
    
    def on_provider_changed(self, index):
        """提供商改变"""
        provider = self.provider_combo.currentData()
        self.model_combo.clear()
        
        # 自定义提供商允许手动输入
        if provider == LLMProviderType.CUSTOM:
            self.model_combo.setEditable(True)
            self.model_combo.setPlaceholderText("输入模型名称，如: llama2, mistral, qwen...")
            # 添加一些常见的本地模型作为提示
            common_models = [
                ("llama2", "Llama 2"),
                ("llama3", "Llama 3"),
                ("mistral", "Mistral"),
                ("qwen", "Qwen"),
                ("gpt-3.5-turbo", "GPT-3.5 Turbo (中转)"),
                ("gpt-4", "GPT-4 (中转)"),
            ]
            for model_id, model_name in common_models:
                self.model_combo.addItem(model_name, model_id)
            # 添加提示文字
            self.base_url_edit.setPlaceholderText("http://localhost:11434 或中转站URL")
        else:
            self.model_combo.setEditable(False)
            self.base_url_edit.setPlaceholderText("")
            
            try:
                temp_config = ModuleConfig(provider=provider, model="", api_key="")
                llm = LLMProviderFactory.create(temp_config)
                models = llm.get_models()
                
                for model in models:
                    self.model_combo.addItem(f"{model['name']} ({model['context_length']} tokens)", model['id'])
            except Exception as e:
                self.model_combo.addItem("无法获取模型列表")
    
    def test_connection(self):
        """测试连接"""
        provider = self.provider_combo.currentData()
        model = self.model_combo.currentData()
        api_key = self.api_key_edit.text()
        
        if not api_key:
            QMessageBox.warning(self, "警告", "请输入API Key")
            return
        
        try:
            config = ModuleConfig(
                provider=provider,
                model=model,
                api_key=api_key,
                base_url=self.base_url_edit.text() or None,
                temperature=self.temperature_spin.value(),
                max_tokens=self.max_tokens_spin.value()
            )
            
            print(f"\n测试连接 - 提供商: {provider.value}, 模型: {model}")
            print(f"API Key: {api_key[:10]}...{api_key[-4:]}")
            
            llm = LLMProviderFactory.create(config)
            
            if llm.test_connection():
                QMessageBox.information(self, "成功", "连接测试成功！")
            else:
                QMessageBox.warning(self, "失败", "连接测试失败，请检查API Key和网络连接")
        except ValueError as e:
            QMessageBox.critical(self, "错误", f"配置错误: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"连接测试失败: {str(e)}\n\n请检查:\n1. API Key是否正确\n2. 网络连接是否正常\n3. 提供商服务是否可用")
    
    def load_config(self):
        """加载配置"""
        index = self.provider_combo.findData(self.config.provider)
        if index >= 0:
            self.provider_combo.setCurrentIndex(index)
        
        model_index = self.model_combo.findData(self.config.model)
        if model_index >= 0:
            self.model_combo.setCurrentIndex(model_index)
        
        self.api_key_edit.setText(self.config.api_key)
        self.base_url_edit.setText(self.config.base_url or "")
        self.temperature_spin.setValue(self.config.temperature)
        self.max_tokens_spin.setValue(self.config.max_tokens)
    
    def get_config(self):
        """获取配置"""
        return ModuleConfig(
            provider=self.provider_combo.currentData(),
            model=self.model_combo.currentData(),
            api_key=self.api_key_edit.text(),
            base_url=self.base_url_edit.text() or None,
            temperature=self.temperature_spin.value(),
            max_tokens=self.max_tokens_spin.value()
        )


class SettingsDialog(QDialog):
    """设置对话框"""
    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.config = config_manager.get_app_config()
        
        self.init_ui()
    
    def init_ui(self):
        """初始化 UI"""
        self.setWindowTitle("设置")
        self.setGeometry(200, 200, 600, 500)
        
        layout = QVBoxLayout(self)
        
        tab_widget = QTabWidget()
        
        # OCR 设置
        self.ocr_widget = OCRSettingsWidget(self.config.ocr)
        tab_widget.addTab(self.ocr_widget, "PDF 解析器")
        
        self.note_widget = ModuleSettingsWidget("笔记生成", self.config.note_generator)
        tab_widget.addTab(self.note_widget, "笔记生成")
        
        # PPT 生成使用新的 PPTSettingsWidget
        if hasattr(self.config, 'ppt_generator') and isinstance(self.config.ppt_generator, PPTConfig):
            self.ppt_widget = PPTSettingsWidget(self.config.ppt_generator)
        else:
            # 兼容旧配置，转换为新的 PPTConfig
            from models.config import PPTProviderType
            ppt_config = PPTConfig(
                provider=PPTProviderType.KIMI,
                auto_open_browser=True,
                auto_copy_prompt=True
            )
            self.config.ppt_generator = ppt_config
            self.ppt_widget = PPTSettingsWidget(ppt_config)
        tab_widget.addTab(self.ppt_widget, "PPT 生成")
        
        self.mindmap_widget = ModuleSettingsWidget("思维导图", self.config.mindmap_generator)
        tab_widget.addTab(self.mindmap_widget, "思维导图")
        
        self.rag_widget = ModuleSettingsWidget("RAG 构建", self.config.rag_builder)
        tab_widget.addTab(self.rag_widget, "RAG 构建")
        
        self.embed_widget = ModuleSettingsWidget("嵌入模型", self.config.embeddings)
        tab_widget.addTab(self.embed_widget, "嵌入模型")
        
        layout.addWidget(tab_widget)
        
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def save_settings(self):
        """保存设置"""
        try:
            # 保存 OCR 配置
            self.config.ocr = self.ocr_widget.get_config()
            
            self.config.note_generator = self.note_widget.get_config()
            self.config.ppt_generator = self.ppt_widget.get_config()
            self.config.mindmap_generator = self.mindmap_widget.get_config()
            self.config.rag_builder = self.rag_widget.get_config()
            self.config.embeddings = self.embed_widget.get_config()
            
            self.config_manager.save_app_config(self.config)
            
            QMessageBox.information(self, "成功", "设置已保存")
            self.accept()
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            QMessageBox.critical(self, "错误", f"保存设置失败: {str(e)}\n\n详细错误:\n{error_detail}")
