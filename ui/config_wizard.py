"""配置向导"""
from PyQt6.QtWidgets import (
    QWizard, QWizardPage, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QLineEdit, QPushButton, QMessageBox, QFormLayout,
    QSpinBox, QDoubleSpinBox
)
from PyQt6.QtCore import Qt
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.config import LLMProviderType, ModuleConfig
from llm.factory import LLMProviderFactory


class ModuleConfigPage(QWizardPage):
    """模块配置页面"""
    
    def __init__(self, module_name, config_manager):
        super().__init__()
        self.module_name = module_name
        self.config_manager = config_manager
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setTitle(f"配置{self.module_name}")
        self.setSubTitle(f"为{self.module_name}选择LLM提供商和配置")
        
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
        self.temperature_spin.setValue(0.7)
        layout.addRow("温度:", self.temperature_spin)
        
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(100, 128000)
        self.max_tokens_spin.setValue(4096)
        layout.addRow("最大Token:", self.max_tokens_spin)
        
        test_btn = QPushButton("测试连接")
        test_btn.clicked.connect(self.test_connection)
        layout.addRow(test_btn)
        
        self.setLayout(layout)
        
        self.on_provider_changed(0)
    
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
    
    def set_config(self, config: ModuleConfig):
        """设置配置"""
        index = self.provider_combo.findData(config.provider)
        if index >= 0:
            self.provider_combo.setCurrentIndex(index)
        
        model_index = self.model_combo.findData(config.model)
        if model_index >= 0:
            self.model_combo.setCurrentIndex(model_index)
        
        self.api_key_edit.setText(config.api_key)
        self.base_url_edit.setText(config.base_url or "")
        self.temperature_spin.setValue(config.temperature)
        self.max_tokens_spin.setValue(config.max_tokens)


class ConfigWizard(QWizard):
    """配置向导"""
    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.config = config_manager.get_app_config()
        
        self.setWindowTitle("配置向导")
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        
        self.addPage(IntroPage())
        self.addPage(ModuleConfigPage("笔记生成", config_manager))
        self.addPage(ModuleConfigPage("PPT生成", config_manager))
        self.addPage(ModuleConfigPage("思维导图", config_manager))
        self.addPage(ModuleConfigPage("RAG构建", config_manager))
        self.addPage(ModuleConfigPage("嵌入模型", config_manager))
        self.addPage(ConclusionPage())
        
        self.resize(600, 500)
    
    def accept(self):
        """接受配置"""
        try:
            # 获取所有页面ID
            page_ids = self.pageIds()
            print(f"页面IDs: {page_ids}")
            
            # 找到各个配置页面 (跳过IntroPage和ConclusionPage)
            config_pages = []
            for page_id in page_ids:
                page = self.page(page_id)
                if isinstance(page, ModuleConfigPage):
                    config_pages.append(page)
            
            print(f"找到 {len(config_pages)} 个配置页面")
            
            # 按顺序获取配置
            if len(config_pages) >= 5:
                note_config = config_pages[0].get_config()
                ppt_config = config_pages[1].get_config()
                mindmap_config = config_pages[2].get_config()
                rag_config = config_pages[3].get_config()
                embed_config = config_pages[4].get_config()
                
                print(f"笔记生成配置: {note_config.provider.value}")
                print(f"PPT生成配置: {ppt_config.provider.value}")
                print(f"思维导图配置: {mindmap_config.provider.value}")
                print(f"RAG配置: {rag_config.provider.value}")
                print(f"嵌入配置: {embed_config.provider.value}")
                
                self.config.note_generator = note_config
                self.config.ppt_generator = ppt_config
                self.config.mindmap_generator = mindmap_config
                self.config.rag_builder = rag_config
                self.config.embeddings = embed_config
                self.config.first_run = False
                
                self.config_manager.save_app_config(self.config)
                print("配置保存成功!")
                
                super().accept()
            else:
                raise ValueError(f"配置页面数量不正确，期望5个，实际{len(config_pages)}个")
                
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"保存配置失败: {error_detail}")
            QMessageBox.critical(self, "错误", f"保存配置失败: {str(e)}\n\n详细信息:\n{error_detail}")


class IntroPage(QWizardPage):
    """介绍页面"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("欢迎使用")
        self.setSubTitle("配置学术论文智能解析器")
        
        layout = QVBoxLayout()
        
        label = QLabel(
            "欢迎使用学术论文智能解析器！\n\n"
            "本向导将帮助您配置各个功能模块的LLM提供商。\n"
            "您需要为以下模块分别配置:\n"
            "- 笔记生成\n"
            "- PPT生成\n"
            "- RAG构建\n"
            "- 嵌入模型\n\n"
            "点击'下一步'开始配置。"
        )
        label.setWordWrap(True)
        layout.addWidget(label)
        
        self.setLayout(layout)


class ConclusionPage(QWizardPage):
    """结束页面"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("配置完成")
        self.setSubTitle("所有配置已完成")
        
        layout = QVBoxLayout()
        
        label = QLabel(
            "配置已完成！\n\n"
            "您可以随时在'设置'中修改配置。\n\n"
            "点击'完成'开始使用。"
        )
        label.setWordWrap(True)
        layout.addWidget(label)
        
        self.setLayout(layout)
