"""主窗口"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QListWidget, QProgressBar, QMessageBox, QFileDialog,
    QSplitter, QTextEdit, QFrame, QComboBox, QLineEdit, QTabWidget,
    QDialog, QFormLayout
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from models.paper import Paper, Section
from models.config import ModuleConfig, LLMProviderType, OCRProviderType
from config import ConfigManager
from core.pdf_parser import PDFParser
from core.zhipu_pdf_parser import ZhipuPDFParser
from core.note_generator import NoteGenerator
from core.ppt_generator import PPTGenerator
from core.rag_builder import RAGBuilder
from core.mindmap_generator import MindMapGeneratorV2
from utils.helpers import sanitize_filename


class ProcessingThread(QThread):
    """处理线程"""
    progress_updated = pyqtSignal(str, int)
    finished = pyqtSignal(bool, str, list)  # success, message, generated_files
    log_updated = pyqtSignal(str)
    
    def __init__(self, pdf_files, config, options, custom_titles=None):
        super().__init__()
        self.pdf_files = pdf_files
        self.config = config
        self.options = options  # 生成选项
        self.custom_titles = custom_titles or {}  # 自定义标题 {file_path: title}
    
    def run(self):
        """执行处理流程"""
        generated_files = []  # 存储生成的文件信息
        
        try:
            total_files = len(self.pdf_files)
            
            for i, pdf_file in enumerate(self.pdf_files):
                self.log_updated.emit(f"开始处理: {pdf_file}")
                
                self.progress_updated.emit(f"解析PDF: {pdf_file}", int((i / total_files) * 100))
                
                # 根据 OCR 配置选择解析器
                if self.config.ocr.provider == OCRProviderType.ZHIPU:
                    # 使用智谱 AI OCR
                    api_key = self.config.ocr.api_key or self.config.note_generator.api_key
                    parser = ZhipuPDFParser(api_key=api_key)
                    self.log_updated.emit("使用智谱 AI OCR 解析 PDF...")
                else:
                    # 使用本地 pdfplumber
                    parser = PDFParser()
                
                paper = parser.parse(pdf_file)
                self.log_updated.emit(f"PDF解析完成: {paper.title}")
                
                # 使用自定义标题（如果有）
                if pdf_file in self.custom_titles and self.custom_titles[pdf_file]:
                    custom_title = self.custom_titles[pdf_file].strip()
                    if custom_title:
                        paper.title = custom_title
                        self.log_updated.emit(f"使用自定义标题: {custom_title}")
                
                self.progress_updated.emit(f"生成笔记: {paper.title}", int(((i + 0.33) / total_files) * 100))
                
                note_generator = NoteGenerator(self.config.note_generator)
                note = note_generator.generate(paper)
                
                safe_title = sanitize_filename(paper.title[:50])
                note_file = Path(self.config.outputs_path) / f"{safe_title}_notes.md"
                note_file.write_text(note, encoding='utf-8')
                self.log_updated.emit(f"笔记已保存: {note_file}")
                
                file_info = {
                    'paper_title': paper.title,
                    'note_file': str(note_file),
                    'safe_title': safe_title
                }
                
                # 生成PPT（如果启用）
                if self.options.get('generate_ppt', True):
                    self.progress_updated.emit(f"生成PPT: {paper.title}", int(((i + 0.50) / total_files) * 100))
                    
                    ppt_generator = PPTGenerator()
                    ppt = ppt_generator.generate(paper, note)
                    
                    safe_title = sanitize_filename(paper.title[:50])
                    ppt_file = Path(self.config.outputs_path) / f"{safe_title}_ppt.html"
                    ppt_file.write_text(ppt, encoding='utf-8')
                    self.log_updated.emit(f"PPT已保存: {ppt_file}")
                    file_info['ppt_file'] = str(ppt_file)
                
                # 生成思维导图（如果启用）
                if self.options.get('generate_mindmap', True):
                    self.progress_updated.emit(f"生成思维导图: {paper.title}", int(((i + 0.75) / total_files) * 100))
                    
                    try:
                        mindmap_generator = MindMapGeneratorV2(self.config.mindmap_generator)
                        # 使用 markmap 格式生成思维导图
                        mindmap_file = mindmap_generator.generate(paper, note, use_markmap=True)
                        self.log_updated.emit(f"思维导图已保存: {mindmap_file}")
                        file_info['mindmap_file'] = str(mindmap_file)
                    except Exception as e:
                        import traceback
                        error_msg = f"思维导图生成失败: {str(e)}\n{traceback.format_exc()}"
                        self.log_updated.emit(error_msg)
                        print(error_msg)
                
                # 构建RAG（如果启用）
                if self.options.get('generate_rag', True):
                    self.progress_updated.emit(f"构建RAG: {paper.title}", int(((i + 1) / total_files) * 100))
                    
                    rag_builder = RAGBuilder(self.config.rag_builder, self.config.embeddings)
                    rag_db = rag_builder.build(paper, self.config.outputs_path)
                    self.log_updated.emit(f"RAG数据库已保存: {rag_db}")
                    file_info['rag_db'] = str(rag_db)
                
                # 记录生成的文件
                generated_files.append(file_info)
            
            self.finished.emit(True, "所有文件处理完成！", generated_files)
        except Exception as e:
            self.log_updated.emit(f"处理失败: {str(e)}")
            import traceback
            traceback.print_exc()
            self.finished.emit(False, str(e), generated_files)


class RAGQueryThread(QThread):
    """RAG查询线程"""
    finished = pyqtSignal(str, str)  # 答案, 相关文档
    error = pyqtSignal(str)
    
    def __init__(self, rag_builder, db_path, query):
        super().__init__()
        self.rag_builder = rag_builder
        self.db_path = db_path
        self.query = query
    
    def run(self):
        """执行RAG查询"""
        try:
            # 获取相关文档
            docs = self.rag_builder.query(self.db_path, self.query, k=4)
            
            if not docs:
                self.finished.emit("未找到相关文档。请确保RAG数据库已正确构建，或尝试使用不同的关键词。", "")
                return
            
            context = "\n\n---\n\n".join([
                f"【{doc.metadata.get('section', 'Unknown')}】\n{doc.page_content[:500]}"
                for doc in docs
            ])
            
            # 生成答案
            answer = self.rag_builder.generate_answer(self.db_path, self.query)
            
            self.finished.emit(answer, context)
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            self.error.emit(f"{str(e)}\n\n详细错误:\n{error_detail}")


class FileRenameDialog(QDialog):
    """文件重命名对话框"""
    
    def __init__(self, generated_files, parent=None):
        super().__init__(parent)
        self.generated_files = generated_files
        self.new_names = {}
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("重命名生成的文件")
        self.setGeometry(200, 200, 600, 400)
        
        layout = QVBoxLayout(self)
        
        # 说明文字
        info_label = QLabel("您可以修改生成的文件名，留空则使用默认名称:")
        info_label.setStyleSheet("font-weight: bold; color: #2196F3;")
        layout.addWidget(info_label)
        
        # 为每个论文创建输入框
        form_layout = QFormLayout()
        
        for i, file_info in enumerate(self.generated_files):
            paper_title = file_info['paper_title']
            safe_title = file_info['safe_title']
            
            # 创建分组框
            group = QFrame()
            group.setFrameStyle(QFrame.Shape.StyledPanel)
            group_layout = QVBoxLayout(group)
            
            # 显示原始标题
            title_label = QLabel(f"论文标题: {paper_title[:60]}...")
            title_label.setStyleSheet("color: #666; font-size: 11px;")
            group_layout.addWidget(title_label)
            
            # 输入框
            line_edit = QLineEdit()
            line_edit.setPlaceholderText(f"默认: {safe_title}")
            line_edit.setText(safe_title)
            line_edit.setMinimumWidth(300)
            group_layout.addWidget(line_edit)
            
            form_layout.addRow(f"论文 {i+1}:", group)
            
            # 保存引用
            self.new_names[i] = {
                'line_edit': line_edit,
                'file_info': file_info
            }
        
        layout.addLayout(form_layout)
        
        # 按钮
        btn_layout = QHBoxLayout()
        
        self.ok_btn = QPushButton("确认重命名")
        self.ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.ok_btn)
        
        self.skip_btn = QPushButton("跳过")
        self.skip_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.skip_btn)
        
        layout.addLayout(btn_layout)
    
    def get_new_names(self):
        """获取新的文件名映射"""
        result = []
        for i, data in self.new_names.items():
            new_name = data['line_edit'].text().strip()
            if not new_name:
                new_name = data['file_info']['safe_title']
            
            # 清理文件名
            new_name = sanitize_filename(new_name)
            
            result.append({
                'file_info': data['file_info'],
                'new_name': new_name
            })
        return result


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.config = self.config_manager.get_app_config()
        self.pdf_files = []
        self.rag_databases = []  # 存储RAG数据库路径
        
        self.init_ui()
        self.check_first_run()
        self.load_rag_databases()
    
    def init_ui(self):
        """初始化UI - 苹果风格"""
        # 使用苹果风格布局
        from ui.main_window_apple import create_apple_style_main_window
        create_apple_style_main_window(self)
    
    def create_header(self):
        """创建头部"""
        header = QFrame()
        header.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(header)
        
        title = QLabel("学术论文智能解析器")
        title.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        layout.addStretch()
        
        settings_btn = QPushButton("设置")
        settings_btn.clicked.connect(self.show_settings)
        layout.addWidget(settings_btn)
        
        help_btn = QPushButton("帮助")
        help_btn.clicked.connect(self.show_help)
        layout.addWidget(help_btn)
        
        return header
    
    # 注意：旧的 UI 创建方法已被移除，现在使用 main_window_apple.py 中的苹果风格布局
    
    def check_first_run(self):
        """检查是否首次运行"""
        if self.config.first_run:
            self.show_config_wizard()
    
    def show_config_wizard(self):
        """显示配置向导"""
        from ui.config_wizard import ConfigWizard
        wizard = ConfigWizard(self.config_manager, self)
        if wizard.exec():
            self.config = self.config_manager.get_app_config()
            self.log("配置已保存")
    
    def show_settings(self):
        """显示设置"""
        from ui.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self.config_manager, self)
        if dialog.exec():
            self.config = self.config_manager.get_app_config()
            self.log("设置已更新")
    
    def show_help(self):
        """显示帮助"""
        QMessageBox.information(
            self,
            "帮助",
            "学术论文智能解析器使用说明:\n\n"
            "1. 点击'添加文件'选择PDF文件\n"
            "2. 点击'开始处理'开始解析\n"
            "3. 处理完成后，输出文件保存在storage/outputs目录\n"
            "4. 点击'设置'可以修改LLM提供商配置\n\n"
            "输出文件:\n"
            "- *_notes.md: Markdown笔记\n"
            "- *_ppt.html: HTML演示文稿\n"
            "- *_rag_db/: RAG向量数据库"
        )
    
    def add_files(self):
        """添加文件"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择PDF文件",
            "",
            "PDF文件 (*.pdf)"
        )
        
        if files:
            self.pdf_files.extend(files)
            for file in files:
                self.file_list.addItem(Path(file).name)
            self.process_btn.setEnabled(True)
            self.log(f"已添加 {len(files)} 个文件")
    
    def remove_files(self):
        """移除选中文件"""
        selected_items = self.file_list.selectedItems()
        if selected_items:
            for item in selected_items:
                index = self.file_list.row(item)
                self.pdf_files.pop(index)
                self.file_list.takeItem(index)
            
            if not self.pdf_files:
                self.process_btn.setEnabled(False)
            self.log(f"已移除 {len(selected_items)} 个文件")
    
    def clear_files(self):
        """清空文件列表"""
        self.pdf_files.clear()
        self.file_list.clear()
        self.process_btn.setEnabled(False)
        self.log("已清空文件列表")
    
    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名，移除Windows非法字符"""
        return sanitize_filename(filename)
    
    def start_processing(self):
        """开始处理"""
        if not self.pdf_files:
            QMessageBox.warning(self, "警告", "请先添加 PDF 文件")
            return
        
        # 检查 OCR 配置
        ocr_provider = self.config.ocr.provider
        if ocr_provider != OCRProviderType.LOCAL:
            reply = QMessageBox.question(
                self,
                "确认使用付费 OCR 服务",
                f"当前使用的是 {ocr_provider.value} OCR 服务，可能会产生费用。\n\n确认要继续吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        # 获取生成选项
        options = {
            'generate_ppt': self.ppt_checkbox.isChecked(),
            'generate_mindmap': self.mindmap_checkbox.isChecked(),
            'generate_rag': self.rag_checkbox.isChecked()
        }
        
        # 获取自定义标题
        custom_titles = {}
        custom_title = self.custom_title_edit.text().strip()
        if custom_title:
            # 为所有文件使用相同的自定义标题
            for pdf_file in self.pdf_files:
                custom_titles[pdf_file] = custom_title
        
        # 显示确认信息
        selected_options = []
        if options['generate_ppt']:
            selected_options.append("PPT")
        if options['generate_mindmap']:
            selected_options.append("思维导图")
        if options['generate_rag']:
            selected_options.append("RAG数据库")
        
        options_text = ", ".join(selected_options) if selected_options else "仅生成笔记"
        self.log(f"将生成: {options_text}")
        if custom_title:
            self.log(f"使用自定义标题: {custom_title}")
        
        self.process_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("处理中...")
        
        self.processing_thread = ProcessingThread(
            self.pdf_files, 
            self.config, 
            options,
            custom_titles
        )
        self.processing_thread.progress_updated.connect(self.update_progress)
        self.processing_thread.finished.connect(self.processing_finished)
        self.processing_thread.log_updated.connect(self.log)
        self.processing_thread.start()
    
    def update_progress(self, message, value):
        """更新进度"""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
    
    def processing_finished(self, success, message, generated_files):
        """处理完成"""
        self.process_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("就绪")
        
        if success:
            # 根据PPT配置自动打开网站（在显示对话框之前）
            if self.ppt_checkbox.isChecked():
                self.open_ppt_website(generated_files)
            
            # 显示完成消息
            QMessageBox.information(self, "完成", message)
            
            # 显示重命名对话框
            if generated_files:
                rename_dialog = FileRenameDialog(generated_files, self)
                if rename_dialog.exec() == QDialog.DialogCode.Accepted:
                    # 执行重命名
                    self.rename_generated_files(rename_dialog.get_new_names())
            # 刷新RAG数据库列表
            self.load_rag_databases()
            # 切换到RAG问答标签页
            self.tab_widget.setCurrentIndex(1)
        else:
            QMessageBox.critical(self, "错误", f"处理失败: {message}")
    
    def open_ppt_website(self, generated_files):
        """根据配置自动打开PPT生成网站"""
        import webbrowser
        from models.config import PPTProviderType
        
        ppt_config = self.config.ppt_generator
        provider = ppt_config.provider
        
        # 获取笔记内容用于生成提示词
        note_content = ""
        if generated_files and 'note_file' in generated_files[0]:
            try:
                note_file = Path(generated_files[0]['note_file'])
                if note_file.exists():
                    note_content = note_file.read_text(encoding='utf-8')
            except Exception as e:
                self.log(f"读取笔记文件失败: {e}")
        
        # 根据提供商类型打开相应网站
        if provider == PPTProviderType.KIMI:
            url = "https://www.kimi.com/slides"
            self.log(f"正在打开 Kimi PPT 助手: {url}")
            
            # 如果配置了自动复制提示词
            if ppt_config.auto_copy_prompt and note_content:
                self.copy_ppt_prompt_to_clipboard(note_content)
            
            webbrowser.open(url)
            
        elif provider == PPTProviderType.GAMMA:
            url = "https://gamma.app"
            self.log(f"正在打开 Gamma: {url}")
            webbrowser.open(url)
            
        elif provider == PPTProviderType.CANVA:
            url = "https://www.canva.com"
            self.log(f"正在打开 Canva: {url}")
            webbrowser.open(url)
            
        elif provider == PPTProviderType.BEAUTIFUL_AI:
            url = "https://www.beautiful.ai"
            self.log(f"正在打开 Beautiful.ai: {url}")
            webbrowser.open(url)
            
        elif provider == PPTProviderType.LOCAL_HTML:
            # 本地HTML，打开生成的文件
            if generated_files and 'ppt_file' in generated_files[0]:
                ppt_file = generated_files[0]['ppt_file']
                self.log(f"正在打开本地PPT: {ppt_file}")
                webbrowser.open(f"file:///{ppt_file}")
                
        elif provider == PPTProviderType.CUSTOM:
            # 自定义服务
            url = ppt_config.base_url or "https://www.kimi.com/slides"
            self.log(f"正在打开自定义PPT服务: {url}")
            webbrowser.open(url)
    
    def copy_ppt_prompt_to_clipboard(self, note_content: str):
        """复制PPT提示词到剪贴板"""
        try:
            import pyperclip
            
            # 构建简化的提示词（只包含结构和版式建议）
            prompt = f"""请基于以下学术论文笔记，生成一份专业的学术汇报PPT。

## 内容要求
1. 生成10-12页PPT
2. 包含：封面、目录、研究背景、研究目标、研究方法、实验设计、主要结果、结论、局限与展望、致谢
3. 每页内容简洁明了，适合学术汇报
4. 使用专业术语，保持学术严谨性

## 笔记内容（请基于此内容提炼关键点）
{note_content[:2000]}...

## 输出要求
请直接生成PPT框架，我会填入具体内容并选择合适的模板风格。"""
            
            pyperclip.copy(prompt)
            self.log("✅ PPT提示词已复制到剪贴板，请粘贴到网站输入框")
            
        except ImportError:
            self.log("⚠️ 无法复制提示词，请手动安装 pyperclip: pip install pyperclip")
        except Exception as e:
            self.log(f"⚠️ 复制提示词失败: {e}")
    
    def rename_generated_files(self, rename_list):
        """重命名生成的文件
        
        Args:
            rename_list: 包含 file_info 和 new_name 的字典列表
        """
        import shutil
        
        for item in rename_list:
            file_info = item['file_info']
            new_name = item['new_name']
            old_name = file_info['safe_title']
            
            if new_name == old_name:
                continue  # 名称未改变
            
            try:
                # 重命名笔记文件
                old_note = Path(file_info['note_file'])
                if old_note.exists():
                    new_note = old_note.parent / f"{new_name}_notes.md"
                    shutil.move(str(old_note), str(new_note))
                    self.log(f"重命名: {old_note.name} -> {new_note.name}")
                
                # 重命名PPT文件
                old_ppt = Path(file_info['ppt_file'])
                if old_ppt.exists():
                    new_ppt = old_ppt.parent / f"{new_name}_ppt.html"
                    shutil.move(str(old_ppt), str(new_ppt))
                    self.log(f"重命名: {old_ppt.name} -> {new_ppt.name}")
                
                # 重命名思维导图文件
                if 'mindmap_file' in file_info:
                    old_mindmap = Path(file_info['mindmap_file'])
                    if old_mindmap.exists():
                        new_mindmap = old_mindmap.parent / f"{new_name}_pretext_mindmap.html"
                        shutil.move(str(old_mindmap), str(new_mindmap))
                        self.log(f"重命名: {old_mindmap.name} -> {new_mindmap.name}")
                
                # 重命名RAG数据库目录
                old_rag = Path(file_info['rag_db'])
                if old_rag.exists():
                    new_rag = old_rag.parent / f"{new_name}_rag_db"
                    shutil.move(str(old_rag), str(new_rag))
                    self.log(f"重命名: {old_rag.name} -> {new_rag.name}")
                
            except Exception as e:
                self.log(f"重命名失败: {str(e)}")
    
    def log(self, message):
        """记录日志"""
        self.log_text.append(message)
    
    def load_rag_databases(self):
        """加载可用的RAG数据库"""
        self.rag_databases = []
        self.rag_db_combo.clear()
        
        outputs_path = Path(self.config.outputs_path)
        if outputs_path.exists():
            for db_dir in outputs_path.iterdir():
                if db_dir.is_dir() and db_dir.name.endswith("_rag_db"):
                    paper_name = db_dir.name.replace("_rag_db", "").replace("_", " ")
                    self.rag_databases.append((paper_name, str(db_dir)))
                    self.rag_db_combo.addItem(paper_name, str(db_dir))
        
        if self.rag_databases:
            self.log(f"已加载 {len(self.rag_databases)} 个RAG数据库")
        else:
            self.rag_db_combo.addItem("暂无RAG数据库", "")
    
    def execute_rag_query(self):
        """执行RAG查询"""
        query = self.query_input.text().strip()
        if not query:
            QMessageBox.warning(self, "警告", "请输入查询问题")
            return
        
        db_path = self.rag_db_combo.currentData()
        if not db_path or not Path(db_path).exists():
            QMessageBox.warning(self, "警告", "请先选择有效的RAG数据库")
            return
        
        self.query_btn.setEnabled(False)
        self.query_btn.setText("查询中...")
        self.rag_result_text.setText("正在查询，请稍候...")
        
        # 创建RAG构建器并执行查询
        rag_builder = RAGBuilder(self.config.rag_builder, self.config.embeddings)
        self.rag_query_thread = RAGQueryThread(rag_builder, db_path, query)
        self.rag_query_thread.finished.connect(self.on_rag_query_finished)
        self.rag_query_thread.error.connect(self.on_rag_query_error)
        self.rag_query_thread.start()
    
    def on_rag_query_finished(self, answer, context):
        """RAG查询完成"""
        result = f"**AI 回答:**\n\n{answer}\n\n---\n\n**相关文档片段:**\n\n{context}"
        self.rag_result_text.setText(result)
        self.query_btn.setEnabled(True)
        self.query_btn.setText("🔍 查询")
        self.log(f"RAG查询完成: {self.query_input.text()[:50]}...")
    
    def on_rag_query_error(self, error_msg):
        """RAG查询错误"""
        self.rag_result_text.setText(f"查询出错: {error_msg}")
        self.query_btn.setEnabled(True)
        self.query_btn.setText("🔍 查询")
        self.log(f"RAG查询失败: {error_msg}")
    
    def closeEvent(self, event):
        """关闭事件"""
        reply = QMessageBox.question(
            self,
            "确认退出",
            "确定要退出吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()
