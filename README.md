# 学术论文智能解析器

基于 PyQt6 的桌面应用程序，采用 **Google Gemini 风格 Liquid Glass UI**，用于学术论文的智能解析与内容生成。

## ✨ 界面特色

### 🎨 Gemini 风格 Liquid Glass UI

- **蓝紫渐变色系**: 采用 Google Gemini 品牌色彩
  - 明亮蓝 `#4796E3`
  - 柔和紫 `#9177C7`
  - 青绿色 `#40C080`
- **玻璃质感设计**: 半透明卡片、柔和阴影、圆角边框
- **渐变效果**: 按钮、进度条、复选框均使用蓝紫渐变
- **浅色主题**: 舒适的浅灰蓝背景，长时间使用不疲劳

![UI Preview](docs/ui_preview.png)

## 🚀 功能特性

- **📄 PDF 解析**: 支持本地 pdfplumber 和智谱 AI OCR
- **📝 笔记生成**: Wiki LLM 风格的逐级解析，生成结构化 Markdown 笔记，兼容 Obsidian
- **📊 PPT 生成**: 基于笔记自动生成 HTML 演示文稿（支持 Kimi、Gamma、Canva 等）
- **🧠 思维导图**: 自动生成 Markmap 格式的交互式思维导图
- **🔍 RAG 问答**: 构建向量数据库，支持基于论文内容的智能问答
- **⚙️ 多模型支持**: 支持 OpenAI、Claude 及多种国产大模型
- **🔧 灵活配置**: 每个模块可独立配置不同的模型和 API Key

## 🤖 支持的 LLM 提供商

### 国际模型
- **OpenAI**: GPT-4, GPT-3.5 Turbo
- **Anthropic**: Claude 3 Opus, Claude 3 Sonnet, Claude 3 Haiku

### 国产大模型
- **百度文心一言**: ERNIE 4.0, ERNIE 3.5, ERNIE Speed
- **阿里通义千问**: Qwen Max, Qwen Plus, Qwen Turbo
- **智谱 GLM**: GLM-4, GLM-4 Air, GLM-4 Flash
- **DeepSeek**: DeepSeek Chat, DeepSeek Coder
- **Kimi (月之暗面)**: Moonshot v1 8K/32K/128K

## 📦 安装

### 环境要求

- Python 3.9+
- Windows / Mac / Linux

### 安装依赖

```bash
pip install -r requirements.txt
```

## 🎯 使用方法

### 运行应用

```bash
python main.py
```

### 首次运行

首次运行时会显示配置向导，需要为以下模块配置 LLM 提供商：

1. **笔记生成**: 选择用于生成笔记的模型
2. **PPT 生成**: 选择用于生成 PPT 的模型（支持 Kimi、Gamma、Canva、Beautiful.ai 等）
3. **思维导图**: 选择用于生成思维导图的模型
4. **RAG 构建**: 选择用于 RAG 问答的模型
5. **嵌入模型**: 选择用于文本嵌入的模型

### 处理流程

1. 点击"📄 添加文件"选择 PDF 文件
2. （可选）输入自定义标题
3. 选择生成选项（PPT、思维导图、RAG）
4. 点击"▶ 开始处理"开始解析
5. 处理完成后，输出文件保存在 `storage/outputs` 目录

### 输出文件

- `*_notes.md`: Markdown 格式的学习笔记
- `*_ppt.html`: HTML 格式的演示文稿（或自动打开在线 PPT 工具）
- `*_markmap.html`: 交互式思维导图
- `*_rag_db/`: RAG 向量数据库

## 📁 项目结构

```
paper-to-ppt/
├── main.py                    # 主程序入口
├── config.py                  # 配置管理
├── requirements.txt           # 依赖列表
├── launcher.py                # 启动器
│
├── ui/                        # UI 模块
│   ├── main_window.py         # 主窗口
│   ├── main_window_apple.py   # 苹果风格布局
│   ├── liquid_glass_style.py  # Gemini 风格样式系统 ⭐
│   ├── config_wizard.py       # 配置向导
│   ├── settings_dialog.py     # 设置对话框
│   ├── ppt_settings_widget.py # PPT 设置
│   └── ocr_settings_widget.py # OCR 设置
│
├── core/                      # 核心功能
│   ├── pdf_parser.py          # PDF 解析
│   ├── zhipu_pdf_parser.py    # 智谱 OCR 解析
│   ├── note_generator.py      # 笔记生成
│   ├── ppt_generator.py       # PPT 生成
│   ├── mindmap_generator.py   # 思维导图生成
│   └── rag_builder.py         # RAG 构建
│
├── llm/                       # LLM 提供商
│   ├── base.py                # 基础接口
│   ├── factory.py             # 提供商工厂
│   ├── openai_provider.py     # OpenAI
│   ├── anthropic_provider.py  # Claude
│   ├── kimi_provider.py       # Kimi
│   ├── zhipu_provider.py      # 智谱
│   ├── deepseek_provider.py   # DeepSeek
│   ├── alibaba_provider.py    # 阿里
│   └── baidu_provider.py      # 百度
│
├── models/                    # 数据模型
│   ├── paper.py               # 论文数据
│   └── config.py              # 配置数据
│
├── storage/                   # 存储目录
│   ├── uploads/               # 上传文件
│   ├── outputs/               # 输出文件
│   └── config/                # 配置文件
│
└── docs/                      # 文档
    ├── 国产大模型配置指南.md
    ├── 国产大模型对比.md
    └── mindmap_generation_rules.md
```

## 🛠️ 技术栈

- **UI 框架**: PyQt6 + Gemini 风格 Liquid Glass UI
- **PDF 解析**: pdfplumber / 智谱 AI OCR
- **LLM 集成**: 多提供商统一接口
- **向量数据库**: ChromaDB
- **思维导图**: Markmap.js
- **PPT 生成**: HTML + Reveal.js / 在线工具集成

## ⚙️ 配置说明

配置文件位于 `storage/config/config.ini`，API 密钥使用系统密钥环安全存储。

### PPT 提供商配置

支持多种 PPT 生成方式：
- **Kimi PPT**: https://www.kimi.com/slides
- **Gamma**: https://gamma.app
- **Canva**: https://www.canva.com
- **Beautiful.ai**: https://www.beautiful.ai
- **本地 HTML**: 使用 Reveal.js 生成本地演示文稿

## 🎨 UI 样式系统

### LiquidGlassStyle 使用

```python
from ui.liquid_glass_style import LiquidGlassStyle

# 应用全局样式
app = QApplication(sys.argv)
LiquidGlassStyle.apply_to_app(app)
```

### 自定义控件

- **GlassButton**: 带阴影和悬停动画的玻璃按钮
- **GlassCard**: 带悬浮阴影的玻璃卡片

## 📝 注意事项

1. 首次运行需要配置 LLM 提供商和 API 密钥
2. 处理大文件可能需要较长时间
3. 确保有足够的磁盘空间存储输出文件
4. 建议使用 GPT-4、Claude 3 或 Kimi 等高质量模型以获得最佳效果
5. 使用智谱 OCR 时会产生 API 调用费用

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 🔗 相关链接

- [Gemini 品牌色彩](https://www.brandcolorcode.com/gemini)
- [Markmap 思维导图](https://markmap.js.org/)
- [Reveal.js](https://revealjs.com/)
