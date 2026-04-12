"""学术论文智能解析器 - 主程序入口"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ui.main_window import MainWindow
from ui.apple_style import apply_apple_style


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    app.setApplicationName("学术论文智能解析器")
    app.setOrganizationName("PaperParser")
    
    # 应用苹果风格样式
    apply_apple_style(app)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
