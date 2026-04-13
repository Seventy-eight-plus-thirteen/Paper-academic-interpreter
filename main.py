"""学术论文智能解析器 - 主程序入口"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ui.main_window import MainWindow
from ui.liquid_glass_style import LiquidGlassStyle


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    app.setApplicationName("学术论文智能解析器")
    app.setOrganizationName("PaperParser")
    
    # 应用 Liquid Glass 玻璃质感样式
    LiquidGlassStyle.apply_to_app(app)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
