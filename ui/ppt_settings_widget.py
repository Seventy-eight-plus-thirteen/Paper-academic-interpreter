"""PPT设置组件 - 选择PPT生成网站"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QLineEdit, QPushButton, QMessageBox,
    QFormLayout, QCheckBox, QGroupBox
)
from PyQt6.QtCore import Qt

from models.config import PPTProviderType, PPTConfig


class PPTSettingsWidget(QWidget):
    """PPT设置组件 - 选择PPT生成网站"""
    
    # PPT提供商信息
    PPT_PROVIDERS = {
        PPTProviderType.KIMI: {
            "name": "Kimi PPT助手",
            "url": "https://www.kimi.com/slides",
            "description": "月之暗面出品的AI PPT生成工具，支持一键生成",
            "need_api_key": False,
            "need_browser": True
        },
        PPTProviderType.GAMMA: {
            "name": "Gamma",
            "url": "https://gamma.app",
            "description": "专业的AI演示文稿生成平台",
            "need_api_key": False,
            "need_browser": True
        },
        PPTProviderType.CANVA: {
            "name": "Canva",
            "url": "https://www.canva.com",
            "description": "知名设计平台，支持AI生成PPT",
            "need_api_key": False,
            "need_browser": True
        },
        PPTProviderType.BEAUTIFUL_AI: {
            "name": "Beautiful.ai",
            "url": "https://www.beautiful.ai",
            "description": "智能PPT设计工具",
            "need_api_key": False,
            "need_browser": True
        },
        PPTProviderType.LOCAL_HTML: {
            "name": "本地HTML生成",
            "url": "本地文件",
            "description": "在本地生成HTML格式的PPT文件",
            "need_api_key": False,
            "need_browser": False
        },
        PPTProviderType.CUSTOM: {
            "name": "自定义服务",
            "url": "自定义",
            "description": "使用其他PPT生成服务",
            "need_api_key": True,
            "need_browser": True
        }
    }
    
    def __init__(self, config: PPTConfig):
        super().__init__()
        self.config = config
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # 提供商选择组
        provider_group = QGroupBox("PPT生成服务")
        provider_layout = QFormLayout()
        
        self.provider_combo = QComboBox()
        for provider_type, info in self.PPT_PROVIDERS.items():
            self.provider_combo.addItem(f"{info['name']} - {info['description']}", provider_type)
        self.provider_combo.currentIndexChanged.connect(self.on_provider_changed)
        provider_layout.addRow("选择服务:", self.provider_combo)
        
        # 提供商信息标签
        self.provider_info_label = QLabel()
        self.provider_info_label.setWordWrap(True)
        self.provider_info_label.setStyleSheet("color: #666; font-size: 12px;")
        provider_layout.addRow("服务信息:", self.provider_info_label)
        
        # 网站链接
        self.url_label = QLabel()
        self.url_label.setOpenExternalLinks(True)
        self.url_label.setStyleSheet("color: #0066cc;")
        provider_layout.addRow("网站地址:", self.url_label)
        
        provider_group.setLayout(provider_layout)
        layout.addWidget(provider_group)
        
        # 高级选项组
        options_group = QGroupBox("生成选项")
        options_layout = QFormLayout()
        
        self.auto_open_checkbox = QCheckBox("生成后自动打开浏览器")
        self.auto_open_checkbox.setChecked(True)
        options_layout.addRow(self.auto_open_checkbox)
        
        self.auto_copy_checkbox = QCheckBox("自动复制提示词到剪贴板")
        self.auto_copy_checkbox.setChecked(True)
        options_layout.addRow(self.auto_copy_checkbox)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # API Key设置（仅部分提供商需要）
        self.api_key_group = QGroupBox("API设置")
        api_key_layout = QFormLayout()
        
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_edit.setPlaceholderText("部分服务需要API Key")
        api_key_layout.addRow("API Key:", self.api_key_edit)
        
        self.base_url_edit = QLineEdit()
        self.base_url_edit.setPlaceholderText("自定义服务URL（可选）")
        api_key_layout.addRow("服务URL:", self.base_url_edit)
        
        self.api_key_group.setLayout(api_key_layout)
        layout.addWidget(self.api_key_group)
        
        # 测试按钮
        test_btn = QPushButton("测试打开网站")
        test_btn.clicked.connect(self.test_open_website)
        layout.addWidget(test_btn)
        
        # 说明标签
        help_label = QLabel(
            "💡 提示: 选择在线PPT生成服务后，程序会自动生成提示词并打开网站，"
            "您只需在网页中粘贴提示词即可生成PPT。"
        )
        help_label.setWordWrap(True)
        help_label.setStyleSheet("color: #888; font-size: 11px; padding: 10px;")
        layout.addWidget(help_label)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # 加载配置
        self.load_config()
    
    def on_provider_changed(self, index):
        """提供商改变时更新UI"""
        provider = self.provider_combo.currentData()
        if provider and provider in self.PPT_PROVIDERS:
            info = self.PPT_PROVIDERS[provider]
            
            # 更新信息标签
            self.provider_info_label.setText(info['description'])
            
            # 更新URL链接
            if info['url'] != "本地文件" and info['url'] != "自定义":
                self.url_label.setText(f'<a href="{info["url"]}">{info["url"]}</a>')
            else:
                self.url_label.setText(info['url'])
            
            # 显示/隐藏API Key设置
            need_api_key = info['need_api_key']
            self.api_key_group.setVisible(need_api_key)
            
            # 显示/隐藏浏览器选项
            need_browser = info['need_browser']
            self.auto_open_checkbox.setVisible(need_browser)
    
    def test_open_website(self):
        """测试打开网站"""
        import webbrowser
        
        provider = self.provider_combo.currentData()
        if provider and provider in self.PPT_PROVIDERS:
            url = self.PPT_PROVIDERS[provider]['url']
            if url != "本地文件" and url != "自定义":
                webbrowser.open(url)
                QMessageBox.information(self, "成功", f"已打开 {self.PPT_PROVIDERS[provider]['name']}")
            else:
                QMessageBox.information(self, "提示", "本地生成不需要打开浏览器")
    
    def load_config(self):
        """加载配置"""
        # 设置提供商
        index = self.provider_combo.findData(self.config.provider)
        if index >= 0:
            self.provider_combo.setCurrentIndex(index)
        
        # 设置选项
        self.auto_open_checkbox.setChecked(self.config.auto_open_browser)
        self.auto_copy_checkbox.setChecked(self.config.auto_copy_prompt)
        
        # 设置API Key
        self.api_key_edit.setText(self.config.api_key)
        self.base_url_edit.setText(self.config.base_url or "")
    
    def get_config(self) -> PPTConfig:
        """获取配置"""
        return PPTConfig(
            provider=self.provider_combo.currentData(),
            api_key=self.api_key_edit.text(),
            base_url=self.base_url_edit.text() or None,
            auto_open_browser=self.auto_open_checkbox.isChecked(),
            auto_copy_prompt=self.auto_copy_checkbox.isChecked()
        )
