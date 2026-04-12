"""OCR 设置组件"""
from PyQt6.QtWidgets import (
    QWidget, QFormLayout, QComboBox, QLineEdit,
    QPushButton, QMessageBox
)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.config import OCRProviderType, OCRConfig


class OCRSettingsWidget(QWidget):
    """OCR 设置组件"""
    
    def __init__(self, config: OCRConfig):
        super().__init__()
        self.config = config
        self.init_ui()
    
    def init_ui(self):
        """初始化 UI"""
        layout = QFormLayout()
        
        # OCR 提供商选择
        self.provider_combo = QComboBox()
        providers = [
            (OCRProviderType.LOCAL, "本地解析 (pdfplumber) - 免费"),
            (OCRProviderType.ZHIPU, "智谱 AI OCR - 0.012元/页"),
            (OCRProviderType.BAIDU, "百度 OCR - 按需付费"),
            (OCRProviderType.TENCENT, "腾讯云 OCR - 按需付费"),
            (OCRProviderType.CUSTOM, "自定义 OCR 服务"),
        ]
        for provider, display_text in providers:
            self.provider_combo.addItem(display_text, provider)
        
        self.provider_combo.currentIndexChanged.connect(self.on_provider_changed)
        layout.addRow("OCR 提供商:", self.provider_combo)
        
        # API Key
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("API Key:", self.api_key_edit)
        
        # Base URL (可选)
        self.base_url_edit = QLineEdit()
        self.base_url_edit.setPlaceholderText("可选，用于自定义服务")
        layout.addRow("Base URL:", self.base_url_edit)
        
        # 测试按钮
        test_btn = QPushButton("测试连接")
        test_btn.clicked.connect(self.test_connection)
        layout.addRow(test_btn)
        
        self.setLayout(layout)
        self.load_config()
    
    def on_provider_changed(self, index):
        """提供商改变"""
        provider = self.provider_combo.currentData()
        
        # 本地解析不需要 API Key
        if provider == OCRProviderType.LOCAL:
            self.api_key_edit.setEnabled(False)
            self.api_key_edit.setPlaceholderText("本地解析不需要 API Key")
        else:
            self.api_key_edit.setEnabled(True)
            self.api_key_edit.setPlaceholderText("输入 API Key")
    
    def test_connection(self):
        """测试连接"""
        provider = self.provider_combo.currentData()
        
        if provider == OCRProviderType.LOCAL:
            QMessageBox.information(self, "成功", "本地解析器已就绪！")
            return
        
        api_key = self.api_key_edit.text()
        if not api_key:
            QMessageBox.warning(self, "警告", "请输入 API Key")
            return
        
        # TODO: 实现具体的 OCR 服务测试逻辑
        QMessageBox.information(
            self, 
            "提示", 
            f"{provider.value} OCR 配置已保存。\n\n实际连接测试将在解析 PDF 时进行。"
        )
    
    def load_config(self):
        """加载配置"""
        if self.config.provider:
            index = self.provider_combo.findData(self.config.provider)
            if index >= 0:
                self.provider_combo.setCurrentIndex(index)
        
        self.api_key_edit.setText(self.config.api_key)
        self.base_url_edit.setText(self.config.base_url or "")
        
        # 触发一次显示更新
        self.on_provider_changed(self.provider_combo.currentIndex())
    
    def get_config(self) -> OCRConfig:
        """获取配置"""
        return OCRConfig(
            provider=self.provider_combo.currentData(),
            api_key=self.api_key_edit.text(),
            base_url=self.base_url_edit.text() or None
        )
