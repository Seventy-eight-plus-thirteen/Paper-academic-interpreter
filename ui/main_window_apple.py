"""
苹果 Liquid Glass 风格主窗口布局
玻璃质感 UI 组件创建方法
"""
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QListWidget, QLineEdit, QTextEdit,
    QProgressBar, QCheckBox, QGroupBox, QTabWidget,
    QWidget, QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ui.liquid_glass_style import GlassButton, GlassCard


class AppleStyleUIComponents:
    """苹果风格 UI 组件工厂"""
    
    @staticmethod
    def create_header(title_text="学术论文智能解析器"):
        """创建苹果风格头部"""
        header = QFrame()
        header.setProperty("header", True)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 16, 20, 16)
        
        # 标题
        title = QLabel(title_text)
        title.setFont(QFont("-apple-system", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #1d1d1f; background: transparent;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # 设置按钮（次要样式）
        settings_btn = QPushButton("设置")
        settings_btn.setProperty("secondary", True)
        layout.addWidget(settings_btn)
        
        return header, settings_btn
    
    @staticmethod
    def create_file_list_panel():
        """创建文件列表面板"""
        panel = QGroupBox("📄 PDF 文件")
        panel.setFont(QFont("-apple-system", 14, QFont.Weight.Medium))
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 20, 16, 16)
        
        # 文件列表
        file_list = QListWidget()
        file_list.setProperty("fileList", True)
        file_list.setMinimumHeight(200)
        layout.addWidget(file_list)
        
        # 按钮组
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        add_btn = QPushButton("+ 添加文件")
        add_btn.setProperty("secondary", True)
        btn_layout.addWidget(add_btn)
        
        remove_btn = QPushButton("- 移除")
        remove_btn.setProperty("secondary", True)
        btn_layout.addWidget(remove_btn)
        
        clear_btn = QPushButton("清空")
        clear_btn.setProperty("secondary", True)
        btn_layout.addWidget(clear_btn)
        
        layout.addLayout(btn_layout)
        
        return panel, file_list, add_btn, remove_btn, clear_btn
    
    @staticmethod
    def create_options_panel():
        """创建选项面板"""
        panel = QGroupBox("🔧 生成选项")
        panel.setFont(QFont("-apple-system", 14, QFont.Weight.Medium))
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 20, 16, 16)
        
        # 使用 QCheckBox 替代 QPushButton 作为复选框
        ppt_checkbox = QCheckBox("生成 PPT")
        ppt_checkbox.setChecked(True)
        ppt_checkbox.setFont(QFont("-apple-system", 13))
        layout.addWidget(ppt_checkbox)
        
        mindmap_checkbox = QCheckBox("生成思维导图")
        mindmap_checkbox.setChecked(True)
        mindmap_checkbox.setFont(QFont("-apple-system", 13))
        layout.addWidget(mindmap_checkbox)
        
        rag_checkbox = QCheckBox("构建 RAG 数据库")
        rag_checkbox.setChecked(True)
        rag_checkbox.setFont(QFont("-apple-system", 13))
        layout.addWidget(rag_checkbox)
        
        layout.addStretch()
        
        return panel, ppt_checkbox, mindmap_checkbox, rag_checkbox
    
    @staticmethod
    def create_title_input_panel():
        """创建标题输入面板"""
        panel = QGroupBox("✏️ 自定义标题")
        panel.setFont(QFont("-apple-system", 14, QFont.Weight.Medium))
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 20, 16, 16)
        
        # 说明文字
        hint = QLabel("留空则使用 PDF 中的原始标题")
        hint.setProperty("caption", True)
        layout.addWidget(hint)
        
        # 输入框
        title_edit = QLineEdit()
        title_edit.setPlaceholderText("输入自定义标题...")
        layout.addWidget(title_edit)
        
        return panel, title_edit
    
    @staticmethod
    def create_process_button():
        """创建玻璃质感处理按钮"""
        btn = GlassButton("▶ 开始处理")
        btn.setProperty("primary", True)
        btn.setMinimumHeight(48)
        btn.setFont(QFont("-apple-system", 15, QFont.Weight.Medium))
        return btn
    
    @staticmethod
    def create_log_panel():
        """创建日志面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # 标题
        title = QLabel("处理日志")
        title.setFont(QFont("-apple-system", 14, QFont.Weight.Medium))
        layout.addWidget(title)
        
        # 日志文本框
        log_text = QTextEdit()
        log_text.setProperty("log", True)
        log_text.setReadOnly(True)
        log_text.setMinimumHeight(300)
        layout.addWidget(log_text)
        
        return panel, log_text
    
    @staticmethod
    def create_rag_panel():
        """创建 RAG 查询面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # 数据库选择
        db_group = QGroupBox("选择论文数据库")
        db_group.setFont(QFont("-apple-system", 13, QFont.Weight.Medium))
        db_layout = QHBoxLayout(db_group)
        db_layout.setContentsMargins(12, 16, 12, 12)
        
        db_combo = QComboBox()
        db_combo.setMinimumWidth(250)
        db_layout.addWidget(db_combo)
        
        refresh_btn = QPushButton("🔄")
        refresh_btn.setProperty("secondary", True)
        refresh_btn.setFixedSize(36, 36)
        db_layout.addWidget(refresh_btn)
        
        layout.addWidget(db_group)
        
        # 查询输入
        query_group = QGroupBox("输入问题")
        query_group.setFont(QFont("-apple-system", 13, QFont.Weight.Medium))
        query_layout = QVBoxLayout(query_group)
        query_layout.setContentsMargins(12, 16, 12, 12)
        
        query_input = QLineEdit()
        query_input.setPlaceholderText("例如: 这篇论文的主要贡献是什么？")
        query_layout.addWidget(query_input)
        
        query_btn = QPushButton("🔍 查询")
        query_btn.setProperty("primary", True)
        query_layout.addWidget(query_btn)
        
        layout.addWidget(query_group)
        
        # 结果显示
        result_group = QGroupBox("查询结果")
        result_group.setFont(QFont("-apple-system", 13, QFont.Weight.Medium))
        result_layout = QVBoxLayout(result_group)
        result_layout.setContentsMargins(12, 16, 12, 12)
        
        result_text = QTextEdit()
        result_text.setReadOnly(True)
        result_layout.addWidget(result_text)
        
        layout.addWidget(result_group)
        
        return panel, db_combo, refresh_btn, query_input, query_btn, result_text
    
    @staticmethod
    def create_progress_bar():
        """创建进度条"""
        progress = QProgressBar()
        progress.setTextVisible(True)
        progress.setMinimumHeight(6)
        return progress
    
    @staticmethod
    def create_footer():
        """创建底部状态栏"""
        footer = QFrame()
        footer.setProperty("footer", True)
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(20, 12, 20, 12)
        
        status_label = QLabel("就绪")
        status_label.setFont(QFont("-apple-system", 12))
        layout.addWidget(status_label)
        
        layout.addStretch()
        
        version_label = QLabel("v1.0.0")
        version_label.setProperty("caption", True)
        layout.addWidget(version_label)
        
        return footer, status_label


def create_apple_style_main_window(window):
    """
    为 MainWindow 创建苹果风格布局
    替换原有的 init_ui 方法
    """
    from PyQt6.QtWidgets import QSplitter
    
    window.setWindowTitle("学术论文智能解析器")
    window.setGeometry(100, 100, 1280, 900)
    
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    
    main_layout = QVBoxLayout(central_widget)
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.setSpacing(0)
    
    # 创建组件
    components = AppleStyleUIComponents()
    
    # 头部
    header, settings_btn = components.create_header()
    settings_btn.clicked.connect(window.show_settings)
    main_layout.addWidget(header)
    
    # 主体内容 - 分割器
    splitter = QSplitter(Qt.Orientation.Horizontal)
    
    # 左侧面板
    left_widget = QWidget()
    left_layout = QVBoxLayout(left_widget)
    left_layout.setContentsMargins(20, 20, 10, 20)
    left_layout.setSpacing(16)
    
    # 文件列表
    file_panel, window.file_list, add_btn, remove_btn, clear_btn = components.create_file_list_panel()
    add_btn.clicked.connect(window.add_files)
    remove_btn.clicked.connect(window.remove_files)
    clear_btn.clicked.connect(window.clear_files)
    left_layout.addWidget(file_panel)
    
    # 标题输入
    title_panel, window.custom_title_edit = components.create_title_input_panel()
    left_layout.addWidget(title_panel)
    
    # 选项
    options_panel, window.ppt_checkbox, window.mindmap_checkbox, window.rag_checkbox = components.create_options_panel()
    left_layout.addWidget(options_panel)
    
    # 处理按钮
    window.process_btn = components.create_process_button()
    window.process_btn.clicked.connect(window.start_processing)
    window.process_btn.setEnabled(False)
    left_layout.addWidget(window.process_btn)
    
    # 右侧面板 - Tab
    right_widget = QWidget()
    right_layout = QVBoxLayout(right_widget)
    right_layout.setContentsMargins(10, 20, 20, 20)
    right_layout.setSpacing(0)
    
    tab_widget = QTabWidget()
    
    # 日志 Tab
    log_panel, window.log_text = components.create_log_panel()
    tab_widget.addTab(log_panel, "📋 日志")
    
    # RAG Tab
    rag_panel, window.rag_db_combo, window.refresh_db_btn, window.query_input, window.query_btn, window.rag_result_text = components.create_rag_panel()
    window.refresh_db_btn.clicked.connect(window.load_rag_databases)
    window.query_btn.clicked.connect(window.execute_rag_query)
    window.query_input.returnPressed.connect(window.execute_rag_query)
    tab_widget.addTab(rag_panel, "🔍 RAG 问答")
    
    right_layout.addWidget(tab_widget)
    window.tab_widget = tab_widget
    
    # 添加分割器
    splitter.addWidget(left_widget)
    splitter.addWidget(right_widget)
    splitter.setStretchFactor(0, 1)
    splitter.setStretchFactor(1, 2)
    splitter.setHandleWidth(2)
    
    main_layout.addWidget(splitter)
    
    # 进度条
    window.progress_bar = components.create_progress_bar()
    window.progress_bar.setVisible(False)
    main_layout.addWidget(window.progress_bar)
    
    # 底部
    footer, window.status_label = components.create_footer()
    main_layout.addWidget(footer)
    
    return window
