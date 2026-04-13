"""
Gemini 风格 Liquid Glass 样式系统
使用 Google Gemini 品牌色彩：蓝紫渐变色系
"""

from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QFrame, 
    QGraphicsDropShadowEffect, QGraphicsBlurEffect
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QColor, QPalette, QFont


class LiquidGlassColors:
    """Gemini 风格颜色系统"""
    # 主背景色 - 浅灰蓝色调
    BACKGROUND = "#f0f4f8"
    BACKGROUND_LIGHT = "#f8fafc"
    
    # Gemini 品牌色
    GEMINI_BLUE = "#4796E3"      # 明亮蓝
    GEMINI_PURPLE = "#9177C7"    # 柔和紫
    GEMINI_TEAL = "#40C080"      # 青绿色
    GEMINI_PINK = "#CA6673"      # 玫瑰粉
    
    # 渐变色定义
    GRADIENT_PRIMARY = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4796E3, stop:1 #9177C7)"
    GRADIENT_SECONDARY = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #40C080, stop:1 #4796E3)"
    GRADIENT_ACCENT = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #9177C7, stop:1 #CA6673)"
    
    # 玻璃表面色（基于浅色背景）
    SURFACE = "rgba(255, 255, 255, 0.85)"
    SURFACE_HOVER = "rgba(255, 255, 255, 0.95)"
    SURFACE_PRESSED = "rgba(240, 244, 248, 0.9)"
    
    # 边框色
    BORDER = "rgba(71, 150, 227, 0.25)"
    BORDER_STRONG = "rgba(71, 150, 227, 0.4)"
    
    # 文字色
    TEXT_PRIMARY = "#1a1a2e"
    TEXT_SECONDARY = "#4a5568"
    TEXT_TERTIARY = "#718096"
    
    # 强调色（Gemini 蓝）
    ACCENT = "#4796E3"
    ACCENT_HOVER = "#3a7bc8"
    ACCENT_PRESSED = "#2d6ab0"
    
    # 阴影色（柔和的蓝紫色调）
    SHADOW = "rgba(71, 150, 227, 0.15)"
    SHADOW_STRONG = "rgba(145, 119, 199, 0.2)"


class LiquidGlassStyle:
    """Gemini 风格 Liquid Glass 样式应用器"""
    
    @staticmethod
    def apply_to_app(app: QApplication):
        """应用 Liquid Glass 全局样式"""
        app.setStyle("Fusion")
        
        # 设置全局字体
        font = QFont("-apple-system", 13)
        font.setStyleHint(QFont.StyleHint.SansSerif)
        app.setFont(font)
        
        # 应用 QSS
        app.setStyleSheet(LiquidGlassStyle.get_global_stylesheet())
    
    @staticmethod
    def get_global_stylesheet() -> str:
        """获取全局样式表"""
        return """
        /* ==================== 全局样式 ==================== */
        QWidget {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
            font-size: 13px;
            color: #1a1a2e;
        }
        
        /* ==================== 主窗口 - 浅色背景 ==================== */
        QMainWindow {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #f0f4f8,
                stop:0.5 #e8eef5,
                stop:1 #f5f0f8);
        }
        
        /* ==================== 中央部件背景 ==================== */
        QWidget#centralwidget {
            background: transparent;
        }
        
        /* ==================== 玻璃按钮 ==================== */
        QPushButton {
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(71, 150, 227, 0.3);
            border-radius: 12px;
            padding: 10px 20px;
            color: #1a1a2e;
            font-weight: 500;
        }
        
        QPushButton:hover {
            background: rgba(255, 255, 255, 1);
            border-color: rgba(71, 150, 227, 0.5);
        }
        
        QPushButton:pressed {
            background: rgba(240, 244, 248, 0.95);
            border-color: rgba(71, 150, 227, 0.4);
        }
        
        QPushButton:disabled {
            background: rgba(255, 255, 255, 0.5);
            color: rgba(26, 26, 46, 0.4);
            border-color: rgba(71, 150, 227, 0.15);
        }
        
        /* 主要按钮 - Gemini 蓝紫渐变 */
        QPushButton[primary="true"] {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #4796E3,
                stop:1 #9177C7);
            color: white;
            border: none;
            font-weight: 600;
        }
        
        QPushButton[primary="true"]:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #5aa3e8,
                stop:1 #a085d1);
        }
        
        QPushButton[primary="true"]:pressed {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #3a7bc8,
                stop:1 #7d65b0);
        }
        
        /* 次要按钮 */
        QPushButton[secondary="true"] {
            background: rgba(71, 150, 227, 0.1);
            border: 1px solid rgba(71, 150, 227, 0.25);
            color: #4796E3;
        }
        
        QPushButton[secondary="true"]:hover {
            background: rgba(71, 150, 227, 0.18);
            border-color: rgba(71, 150, 227, 0.4);
        }
        
        /* ==================== 玻璃卡片 ==================== */
        QFrame[glass="true"] {
            background: rgba(255, 255, 255, 0.8);
            border: 1px solid rgba(71, 150, 227, 0.2);
            border-radius: 20px;
        }
        
        /* ==================== 输入框 ==================== */
        QLineEdit {
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(71, 150, 227, 0.25);
            border-radius: 10px;
            padding: 10px 14px;
            selection-background-color: #4796E3;
        }
        
        QLineEdit:focus {
            background: rgba(255, 255, 255, 1);
            border: 2px solid #4796E3;
        }
        
        /* ==================== 文本编辑 ==================== */
        QTextEdit {
            background: rgba(255, 255, 255, 0.85);
            border: 1px solid rgba(71, 150, 227, 0.2);
            border-radius: 16px;
            padding: 12px;
            selection-background-color: #4796E3;
        }
        
        QTextEdit:focus {
            border-color: rgba(71, 150, 227, 0.4);
        }
        
        /* ==================== 列表 ==================== */
        QListWidget {
            background: rgba(255, 255, 255, 0.7);
            border: 1px solid rgba(71, 150, 227, 0.2);
            border-radius: 16px;
            padding: 8px;
            outline: none;
        }
        
        QListWidget::item {
            background: transparent;
            border-radius: 10px;
            padding: 10px 14px;
            margin: 2px 4px;
            color: #1a1a2e;
        }
        
        QListWidget::item:selected {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(71, 150, 227, 0.15),
                stop:1 rgba(145, 119, 199, 0.1));
            color: #4796E3;
            font-weight: 500;
        }
        
        QListWidget::item:hover {
            background: rgba(71, 150, 227, 0.08);
        }
        
        /* ==================== 下拉框 ==================== */
        QComboBox {
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(71, 150, 227, 0.25);
            border-radius: 10px;
            padding: 8px 14px;
        }
        
        QComboBox:hover {
            background: rgba(255, 255, 255, 1);
            border-color: rgba(71, 150, 227, 0.4);
        }
        
        QComboBox::drop-down {
            border: none;
            width: 24px;
        }
        
        QComboBox QAbstractItemView {
            background: rgba(255, 255, 255, 0.95);
            border: 1px solid rgba(71, 150, 227, 0.2);
            border-radius: 10px;
            selection-background-color: rgba(71, 150, 227, 0.15);
        }
        
        /* ==================== 进度条 - Gemini 渐变 ==================== */
        QProgressBar {
            background: rgba(71, 150, 227, 0.1);
            border: none;
            border-radius: 6px;
            height: 6px;
            text-align: center;
        }
        
        QProgressBar::chunk {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #4796E3,
                stop:0.5 #9177C7,
                stop:1 #40C080);
            border-radius: 6px;
        }
        
        /* ==================== 分组框 ==================== */
        QGroupBox {
            background: rgba(255, 255, 255, 0.75);
            border: 1px solid rgba(71, 150, 227, 0.2);
            border-radius: 20px;
            margin-top: 12px;
            padding-top: 24px;
            font-weight: 600;
            color: #1a1a2e;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 20px;
            padding: 0 12px;
            color: #4796E3;
        }
        
        /* ==================== 标签页 ==================== */
        QTabWidget::pane {
            background: rgba(255, 255, 255, 0.7);
            border: 1px solid rgba(71, 150, 227, 0.2);
            border-radius: 16px;
            top: -1px;
        }
        
        QTabBar::tab {
            background: transparent;
            border: none;
            padding: 10px 20px;
            margin-right: 4px;
            border-radius: 10px;
            color: #718096;
        }
        
        QTabBar::tab:selected {
            background: rgba(255, 255, 255, 0.9);
            color: #4796E3;
            font-weight: 500;
            border: 1px solid rgba(71, 150, 227, 0.2);
        }
        
        QTabBar::tab:hover {
            background: rgba(71, 150, 227, 0.1);
            color: #1a1a2e;
        }
        
        /* ==================== 滚动条 ==================== */
        QScrollBar:vertical {
            background: transparent;
            width: 8px;
            border-radius: 4px;
        }
        
        QScrollBar::handle:vertical {
            background: rgba(71, 150, 227, 0.3);
            border-radius: 4px;
            min-height: 30px;
        }
        
        QScrollBar::handle:vertical:hover {
            background: rgba(71, 150, 227, 0.5);
        }
        
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0;
        }
        
        /* ==================== 复选框 ==================== */
        QCheckBox {
            spacing: 10px;
            color: #1a1a2e;
        }
        
        QCheckBox::indicator {
            width: 22px;
            height: 22px;
            border-radius: 6px;
            border: 2px solid rgba(71, 150, 227, 0.4);
            background: rgba(255, 255, 255, 0.8);
        }
        
        QCheckBox::indicator:checked {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #4796E3,
                stop:1 #9177C7);
            border-color: #4796E3;
        }
        
        QCheckBox::indicator:hover {
            border-color: #4796E3;
        }
        
        /* ==================== 标签 ==================== */
        QLabel {
            color: #1a1a2e;
        }
        
        QLabel[caption="true"] {
            color: #718096;
            font-size: 12px;
        }
        
        /* ==================== 分割器 ==================== */
        QSplitter::handle {
            background: rgba(71, 150, 227, 0.15);
        }
        
        QSplitter::handle:horizontal {
            width: 2px;
        }
        
        QSplitter::handle:hover {
            background: rgba(71, 150, 227, 0.3);
        }
        """


class GlassButton(QPushButton):
    """Gemini 风格玻璃质感按钮"""
    
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self._setup_shadow()
        self._setup_animation()
    
    def _setup_shadow(self):
        """设置 Gemini 风格阴影效果"""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(71, 150, 227, 40))  # Gemini 蓝色阴影
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
    
    def _setup_animation(self):
        """设置按压动画"""
        self._scale_animation = QPropertyAnimation(self, b"geometry")
        self._scale_animation.setDuration(150)
        self._scale_animation.setEasingCurve(QEasingCurve.Type.OutBack)
    
    def enterEvent(self, event):
        """鼠标进入"""
        shadow = self.graphicsEffect()
        if shadow:
            shadow.setBlurRadius(25)
            shadow.setColor(QColor(145, 119, 199, 50))  # Gemini 紫色阴影
            shadow.setOffset(0, 6)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """鼠标离开"""
        shadow = self.graphicsEffect()
        if shadow:
            shadow.setBlurRadius(20)
            shadow.setColor(QColor(71, 150, 227, 40))
            shadow.setOffset(0, 4)
        super().leaveEvent(event)


class GlassCard(QFrame):
    """Gemini 风格玻璃质感卡片"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("glass", True)
        self._setup_shadow()
    
    def _setup_shadow(self):
        """设置 Gemini 风格悬浮阴影"""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(71, 150, 227, 30))
        shadow.setOffset(0, 8)
        self.setGraphicsEffect(shadow)


def apply_blur_background(widget: QWidget, radius: int = 20):
    """
    为背景添加模糊效果
    注意：这需要底层窗口支持，在 Windows 上效果有限
    """
    blur = QGraphicsBlurEffect()
    blur.setBlurRadius(radius)
    # 注意：这会将模糊应用到 widget 本身，不是背景
    # 真正的背景模糊需要更复杂的实现
