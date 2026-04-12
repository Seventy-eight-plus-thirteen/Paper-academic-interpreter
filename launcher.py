"""轻量级桌面启动器 - 核心功能"""
import sys
import os
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTextEdit, 
                             QFileDialog, QMessageBox, QGroupBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont


class ScriptRunner(QThread):
    """脚本运行器"""
    output_received = pyqtSignal(str)
    finished = pyqtSignal(int)
    
    def __init__(self, script_path, args=None):
        super().__init__()
        self.script_path = script_path
        self.args = args or []
    
    def run(self):
        """运行脚本"""
        try:
            cmd = [sys.executable, self.script_path] + self.args
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(Path(__file__).parent)
            )
            
            for line in process.stdout:
                self.output_received.emit(line.strip())
            
            for line in process.stderr:
                self.output_received.emit(f"ERROR: {line.strip()}")
            
            return_code = process.wait()
            self.finished.emit(return_code)
            
        except Exception as e:
            self.output_received.emit(f"启动失败: {str(e)}")
            self.finished.emit(1)


class PaperProcessorLauncher(QMainWindow):
    """论文处理启动器"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("学术论文智能解析器")
        self.setGeometry(100, 100, 700, 500)
        
        self.project_root = Path(__file__).parent
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # 标题
        title = QLabel("学术论文智能解析器")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # PDF选择
        pdf_group = QGroupBox("选择PDF文件")
        pdf_layout = QHBoxLayout(pdf_group)
        
        self.pdf_path_edit = QLineEdit()
        self.pdf_path_edit.setPlaceholderText("选择PDF文件...")
        pdf_layout.addWidget(self.pdf_path_edit)
        
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self.browse_pdf)
        pdf_layout.addWidget(browse_btn)
        
        layout.addWidget(pdf_group)
        
        # 核心功能按钮
        func_group = QGroupBox("核心功能")
        func_layout = QVBoxLayout(func_group)
        
        process_btn = QPushButton("🚀 完整处理（笔记+PPT+思维导图+RAG）")
        process_btn.setStyleSheet("font-size: 14px; padding: 10px;")
        process_btn.clicked.connect(self.run_full_process)
        func_layout.addWidget(process_btn)
        
        # 单独功能
        single_layout = QHBoxLayout()
        
        notes_btn = QPushButton("📝 生成笔记")
        notes_btn.clicked.connect(self.run_notes_only)
        single_layout.addWidget(notes_btn)
        
        ppt_btn = QPushButton("📊 生成PPT")
        ppt_btn.clicked.connect(self.run_ppt_only)
        single_layout.addWidget(ppt_btn)
        
        mindmap_btn = QPushButton("🧠 思维导图")
        mindmap_btn.clicked.connect(self.run_mindmap_only)
        single_layout.addWidget(mindmap_btn)
        
        func_layout.addLayout(single_layout)
        
        layout.addWidget(func_group)
        
        # 配置按钮
        config_group = QGroupBox("配置")
        config_layout = QHBoxLayout(config_group)
        
        config_btn = QPushButton("⚙️ 配置向导")
        config_btn.clicked.connect(self.run_config_wizard)
        config_layout.addWidget(config_btn)
        
        layout.addWidget(config_group)
        
        # 输出区域
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Consolas", 10))
        layout.addWidget(QLabel("输出日志:"))
        layout.addWidget(self.output_text)
        
        # 状态栏
        self.status_bar = QLabel("就绪")
        layout.addWidget(self.status_bar)
    
    def browse_pdf(self):
        """浏览PDF文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择PDF文件", "", "PDF Files (*.pdf)"
        )
        if file_path:
            self.pdf_path_edit.setText(file_path)
    
    def run_script(self, script_name, args=None):
        """运行脚本"""
        if not self.pdf_path_edit.text() and script_name != "ui/config_wizard.py":
            QMessageBox.warning(self, "警告", "请先选择PDF文件")
            return
        
        script_path = self.project_root / script_name
        if not script_path.exists():
            QMessageBox.critical(self, "错误", f"脚本不存在: {script_name}")
            return
        
        self.output_text.clear()
        self.status_bar.setText("正在运行...")
        
        self.runner = ScriptRunner(str(script_path), args)
        self.runner.output_received.connect(self.append_output)
        self.runner.finished.connect(self.on_script_finished)
        self.runner.start()
    
    def run_full_process(self):
        """运行完整处理"""
        pdf_path = self.pdf_path_edit.text()
        self.run_script("main.py", [pdf_path])
    
    def run_notes_only(self):
        """仅生成笔记"""
        pdf_path = self.pdf_path_edit.text()
        self.run_script("core/note_generator.py", [pdf_path])
    
    def run_ppt_only(self):
        """仅生成PPT"""
        pdf_path = self.pdf_path_edit.text()
        self.run_script("core/ppt_generator.py", [pdf_path])
    
    def run_mindmap_only(self):
        """仅生成思维导图"""
        pdf_path = self.pdf_path_edit.text()
        self.run_script("core/mindmap_generator.py", [pdf_path])
    
    def run_config_wizard(self):
        """运行配置向导"""
        self.run_script("ui/config_wizard.py")
    
    def append_output(self, text):
        """追加输出"""
        self.output_text.append(text)
    
    def on_script_finished(self, return_code):
        """脚本完成"""
        if return_code == 0:
            self.status_bar.setText("处理完成")
            QMessageBox.information(self, "成功", "处理完成！")
        else:
            self.status_bar.setText("处理失败")
            QMessageBox.critical(self, "错误", f"处理失败，返回码: {return_code}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = PaperProcessorLauncher()
    launcher.show()
    sys.exit(app.exec())
