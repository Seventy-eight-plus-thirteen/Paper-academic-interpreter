# Paper-to-PPT 学术论文智能解析器

基于 AI 的学术论文解析工具，支持 PDF 解析、笔记生成、思维导图生成和 PPT 生成。

## 功能特性

- **PDF 解析**: 支持本地解析和 OCR 识别
- **笔记生成**: 自动生成中文 Wiki 风格笔记
- **思维导图**: 生成 Markmap 格式交互式思维导图
- **PPT 生成**: 集成 Kimi PPT 助手，自动生成演示文稿
- **RAG 支持**: 构建论文知识库，支持问答检索

## 支持的 LLM 提供商

- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- 智谱 AI (GLM-4)
- 百度 (文心一言)
- 阿里 (通义千问)
- DeepSeek
- Kimi (Moonshot)
- 自定义/本地模型

## 安装

1. 克隆仓库
```bash
git clone https://github.com/yourusername/paper-to-ppt.git
cd paper-to-ppt
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置 API 密钥
```bash
# 复制示例配置文件
cp storage/config/config.ini.example storage/config/config.ini

# 编辑配置文件，填入你的 API 密钥
# Windows: 使用系统密钥管理器存储 API 密钥
# macOS/Linux: 使用 keyring 存储 API 密钥
```

## 使用

### 启动 GUI
```bash
python main.py
```

### 首次配置
1. 点击设置按钮
2. 选择 LLM 提供商并配置 API 密钥
3. 配置 OCR 设置（可选）
4. 保存配置

### 解析论文
1. 点击上传论文选择 PDF 文件
2. 选择需要生成的内容（笔记/思维导图/PPT/RAG）
3. 点击开始处理
4. 查看生成的文件

## 项目结构

```
paper-to-ppt/
├── core/               # 核心功能模块
│   ├── note_generator.py      # 笔记生成
│   ├── mindmap_generator.py   # 思维导图生成
│   ├── pdf_parser.py          # PDF 解析
│   ├── ppt_generator.py       # PPT 生成
│   └── rag_builder.py         # RAG 构建
├── llm/                # LLM 提供商接口
│   ├── base.py
│   ├── factory.py
│   └── *_provider.py   # 各提供商实现
├── models/             # 数据模型
│   ├── config.py
│   └── paper.py
├── ui/                 # 用户界面
│   ├── main_window.py
│   └── settings_dialog.py
├── utils/              # 工具函数
│   └── helpers.py
├── storage/            # 存储目录
│   ├── config/        # 配置文件
│   ├── uploads/       # 上传文件
│   └── outputs/       # 输出文件
├── main.py            # 程序入口
├── launcher.py        # 启动器
└── requirements.txt   # 依赖列表
```

## 配置说明

### API 密钥配置

API 密钥通过系统密钥管理器存储，不在配置文件中明文保存。

**Windows**: 使用 Windows Credential Manager
**macOS**: 使用 Keychain
**Linux**: 使用 Secret Service API

配置示例：
```ini
[note_generator]
provider = zhipu
model = glm-4-flash
```

然后在程序中通过设置对话框输入 API 密钥。

## 许可证

MIT License
