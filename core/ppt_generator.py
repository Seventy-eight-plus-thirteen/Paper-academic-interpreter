"""PPT生成模块 - 优化版"""
import sys
from pathlib import Path
import urllib.parse
import webbrowser
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import List, Dict
from models.paper import Paper
from llm.factory import LLMProviderFactory


class PPTGenerator:
    """优化版PPT生成器 - 美观设计 + 深度内容"""
    
    def __init__(self, llm_config=None):
        """初始化PPT生成器
        
        Args:
            llm_config: LLM配置（可选，用于智能生成PPT内容）
        """
        if llm_config:
            self.llm = LLMProviderFactory.create(llm_config)
        else:
            self.llm = None
    
    def generate(self, paper: Paper, note: str = None) -> str:
        """基于笔记智能生成HTML PPT
        
        使用LLM智能提取和优化内容，生成专业美观的PPT
        
        Args:
            paper: 论文对象
            note: Markdown笔记
            
        Returns:
            str: HTML格式的PPT文件路径
        """
        print(f"开始生成优化版PPT: {paper.title}")
        
        # 提取深度内容
        content = self._extract_deep_content(paper, note)
        
        # 生成幻灯片
        if self.llm and note:
            slides = self._generate_slides_with_llm(content, paper)
        else:
            slides = self._generate_slides_from_content(content, paper)
        
        # 包装成完整HTML
        html = self._wrap_in_html(paper.title, slides)
        
        # 保存文件
        output_path = self._save_html(html, paper.title)
        
        print(f"优化版PPT生成完成: {output_path}")
        return output_path
    
    def generate_kimi_ppt_link(self, paper: Paper, note: str = None) -> Dict[str, str]:
        """生成Kimi PPT助手的链接和提示词
        
        将笔记内容转换为Kimi PPT助手可用的格式，
        生成可以直接访问的链接和复制粘贴的提示词
        
        Args:
            paper: 论文对象
            note: Markdown笔记
            
        Returns:
            Dict: 包含url和prompt的字典
        """
        print(f"生成Kimi PPT助手链接: {paper.title}")
        
        # Kimi PPT助手基础URL
        kimi_base_url = "https://www.kimi.com/slides"
        
        # 构建提示词
        prompt = self._build_kimi_prompt(paper, note)
        
        # 由于Kimi不支持直接通过URL参数传递内容，
        # 我们返回基础URL和提示词，用户需要手动复制粘贴
        result = {
            'url': kimi_base_url,
            'prompt': prompt,
            'instructions': """
使用步骤：
1. 点击上方链接打开 Kimi PPT 助手
2. 在输入框中粘贴下方提示词
3. 点击生成按钮，等待PPT生成
4. 选择喜欢的模板风格
5. 下载或在线编辑PPT
"""
        }
        
        print("Kimi PPT助手链接生成完成")
        return result
    
    def open_kimi_ppt_with_clipboard(self, paper: Paper, note: str = None) -> bool:
        """打开Kimi PPT助手并自动复制提示词到剪贴板
        
        一键操作：生成提示词 -> 复制到剪贴板 -> 打开浏览器
        如果剪贴板复制失败，会自动保存到临时文件
        
        Args:
            paper: 论文对象
            note: Markdown笔记
            
        Returns:
            bool: 操作是否成功
        """
        print(f"\n🚀 正在准备Kimi PPT助手...")
        
        try:
            # 1. 生成提示词
            result = self.generate_kimi_ppt_link(paper, note)
            prompt = result['prompt']
            url = result['url']
            
            # 2. 尝试复制到剪贴板
            clipboard_success = self._copy_to_clipboard(prompt)
            
            # 3. 如果剪贴板失败，保存到临时文件
            temp_file_path = None
            if not clipboard_success:
                temp_file_path = self._save_prompt_to_temp_file(prompt, paper.title)
            
            # 4. 打开浏览器
            print(f"🌐 正在打开浏览器...")
            webbrowser.open(url)
            
            # 5. 显示操作结果
            print("\n" + "=" * 60)
            print("✅ 操作完成！")
            print("=" * 60)
            
            if clipboard_success:
                print("📋 提示词已自动复制到剪贴板")
                print("👉 请直接在Kimi PPT助手输入框中按 Ctrl+V 粘贴")
            elif temp_file_path:
                print("⚠️  剪贴板复制失败，提示词已保存到临时文件")
                print(f"📄 文件路径: {temp_file_path}")
                print("👉 请打开该文件，复制内容后粘贴到Kimi")
                # 自动打开临时文件
                webbrowser.open(f"file:///{temp_file_path}")
            else:
                print("⚠️  自动复制失败，请手动复制下方提示词")
                print("\n" + "-" * 60)
                print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
                print("-" * 60)
            
            print(f"\n🔗 Kimi PPT助手已打开: {url}")
            print("\n📋 使用步骤:")
            print("   1. 在Kimi页面中找到输入框")
            print("   2. 粘贴提示词 (Ctrl+V)")
            print("   3. 点击生成按钮")
            print("   4. 选择喜欢的模板")
            
            return True
            
        except Exception as e:
            print(f"❌ 操作失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _save_prompt_to_temp_file(self, prompt: str, title: str) -> str:
        """将提示词保存到临时文件
        
        Args:
            prompt: 提示词内容
            title: 论文标题
            
        Returns:
            str: 临时文件路径
        """
        import tempfile
        import time
        
        # 创建临时文件
        safe_title = "".join(c for c in title[:30] if c.isalnum() or c in (' ', '-', '_')).strip()
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"kimi_prompt_{safe_title}_{timestamp}.txt"
        
        temp_dir = Path(tempfile.gettempdir())
        temp_file = temp_dir / filename
        
        # 写入文件
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("Kimi PPT 助手 - 提示词\n")
            f.write("=" * 60 + "\n\n")
            f.write(prompt)
            f.write("\n\n" + "=" * 60 + "\n")
            f.write("使用说明：\n")
            f.write("1. 复制上方所有内容\n")
            f.write("2. 打开 https://www.kimi.com/slides\n")
            f.write("3. 粘贴到输入框中\n")
            f.write("4. 点击生成按钮\n")
            f.write("=" * 60 + "\n")
        
        return str(temp_file)
    
    def _copy_to_clipboard(self, text: str) -> bool:
        """将文本复制到剪贴板
        
        尝试多种方法复制到剪贴板，支持Windows、macOS、Linux
        
        Args:
            text: 要复制的文本
            
        Returns:
            bool: 是否复制成功
        """
        # 方法1: 使用 pyperclip (如果已安装)
        try:
            import pyperclip
            pyperclip.copy(text)
            return True
        except ImportError:
            pass
        
        # 方法2: Windows 使用 ctypes
        if sys.platform == 'win32':
            try:
                import ctypes
                from ctypes import wintypes
                
                # 打开剪贴板
                if ctypes.windll.user32.OpenClipboard(None):
                    ctypes.windll.user32.EmptyClipboard()
                    
                    # 分配内存
                    text_bytes = text.encode('utf-8')
                    h_global = ctypes.windll.kernel32.GlobalAlloc(0x2000, len(text_bytes) + 1)
                    if h_global:
                        lp_global = ctypes.windll.kernel32.GlobalLock(h_global)
                        if lp_global:
                            ctypes.memmove(lp_global, text_bytes, len(text_bytes))
                            ctypes.windll.kernel32.GlobalUnlock(h_global)
                            ctypes.windll.user32.SetClipboardData(1, h_global)  # 1 = CF_TEXT
                    
                    ctypes.windll.user32.CloseClipboard()
                    return True
            except Exception:
                pass
        
        # 方法3: macOS 使用 pbcopy
        elif sys.platform == 'darwin':
            try:
                import subprocess
                process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
                process.communicate(text.encode('utf-8'))
                return True
            except Exception:
                pass
        
        # 方法4: Linux 使用 xclip 或 xsel
        elif sys.platform.startswith('linux'):
            try:
                import subprocess
                # 尝试 xclip
                process = subprocess.Popen(['xclip', '-selection', 'clipboard'], 
                                          stdin=subprocess.PIPE)
                process.communicate(text.encode('utf-8'))
                return True
            except Exception:
                try:
                    # 尝试 xsel
                    import subprocess
                    process = subprocess.Popen(['xsel', '-b', '-i'], 
                                              stdin=subprocess.PIPE)
                    process.communicate(text.encode('utf-8'))
                    return True
                except Exception:
                    pass
        
        # 所有方法都失败
        return False
    
    def _build_kimi_prompt(self, paper: Paper, note: str = None) -> str:
        """构建Kimi PPT助手的提示词
        
        只提供PPT结构和版式建议，不包含原始笔记内容
        
        Args:
            paper: 论文对象
            note: Markdown笔记（用于提取关键信息，但不放入提示词）
            
        Returns:
            str: 格式化的提示词
        """
        # 从笔记中提取关键信息（用于理解论文类型）
        content_preview = note[:500] if note else (paper.abstract or '')[:500]
        
        # 判断论文类型
        is_medical = any(keyword in content_preview.lower() for keyword in 
                        ['临床', '患者', '疾病', '治疗', '医学', '医院', '药物', '手术', 
                         'patient', 'disease', 'treatment', 'clinical', 'medical'])
        
        is_cs = any(keyword in content_preview.lower() for keyword in 
                   ['算法', '模型', '网络', '深度学习', '机器学习', 'ai', 'artificial intelligence',
                    'neural network', 'deep learning', 'model', 'algorithm'])
        
        # 根据论文类型选择配色和风格
        if is_medical:
            style_guide = """
## 设计风格
- **配色方案**: 医疗蓝(#4A90E2) + 白色 + 浅灰，专业可靠
- **字体**: 标题用思源黑体Bold，正文用思源黑体Regular
- **布局**: 左侧导航栏，右侧内容区，清晰分明
- **图标**: 使用医疗相关图标（心电图、DNA、显微镜等）
- **图片**: 建议添加医疗器械、实验室场景图片
"""
        elif is_cs:
            style_guide = """
## 设计风格
- **配色方案**: 科技蓝(#667EEA) + 紫色(#764BA2)渐变，现代感强
- **字体**: 标题用Montserrat Bold，正文用Open Sans
- **布局**: 居中对称，代码块用深色背景高亮
- **图标**: 使用科技图标（芯片、代码、网络节点等）
- **图片**: 建议添加架构图、流程图、数据可视化图表
"""
        else:
            style_guide = """
## 设计风格
- **配色方案**: 学术蓝(#2C5F8D) + 金色(#D4AF37)，庄重典雅
- **字体**: 标题用思源宋体，正文用思源黑体
- **布局**: 经典学术风格，留白充足
- **图标**: 简洁线条图标
- **图片**: 建议添加研究场景、实验设备图片
"""
        
        prompt = f"""请为以下学术论文生成一份专业的学术汇报PPT。

## 论文信息
- **标题**：{paper.title}
- **作者**：{', '.join(paper.authors[:3])}{' 等' if len(paper.authors) > 3 else '' if paper.authors else '未知'}
- **发表**：{paper.publication or '未知'} {paper.year or ''}

## PPT结构要求
请生成 **10-12页** PPT，包含以下章节：

### 第1页：封面
- 论文标题（大字号，居中）
- 作者信息
- 发表期刊/会议
- 日期

### 第2页：目录
- 清晰列出各章节标题

### 第3页：研究背景
- 领域现状
- 存在的问题
- 研究动机

### 第4页：研究目标
- 核心问题
- 研究假设
- 预期贡献

### 第5-6页：研究方法
- 方法概述
- 技术路线
- 创新点

### 第7-8页：实验设计
- 数据集介绍
- 评估指标
- 对比方法

### 第9页：主要结果
- 关键数据（用图表展示）
- 性能对比
- 显著性分析

### 第10页：结论
- 主要发现
- 理论贡献
- 实践意义

### 第11页：局限与展望
- 研究局限
- 未来方向

### 第12页：致谢/问答
- 感谢语
- 联系方式

{style_guide}

## 版式要求
1. **每页布局**：
   - 标题区：顶部，字号32-36pt
   - 内容区：中部，分2-3栏或列表
   - 页脚：页码和论文标题缩写

2. **文字规范**：
   - 每页不超过6个要点
   - 每点不超过2行
   - 字号：标题32pt，正文18-24pt

3. **图表要求**：
   - 数据用柱状图/折线图展示
   - 流程用流程图
   - 对比用表格

4. **动画效果**：
   - 简洁的淡入效果
   - 避免花哨动画

## 输出要求
请直接生成PPT，我会根据你的设计选择合适的模板。"""
        
        return prompt
    
    def _extract_deep_content(self, paper: Paper, note: str = None) -> Dict:
        """深度提取论文内容"""
        content = {
            'title': paper.title,
            'authors': paper.authors,
            'abstract': paper.abstract or '',
            'publication': paper.publication or '',
            'year': paper.year or '',
            'doi': paper.doi or '',
            'sections': []
        }
        
        # 优先使用笔记内容
        source_text = note if note else paper.abstract
        
        if source_text:
            content['sections'] = self._parse_content_structure(source_text)
        
        # 如果没有提取到内容，使用论文章节
        if not content['sections'] and paper.sections:
            for section in paper.sections[:6]:
                content['sections'].append({
                    'title': section.title,
                    'points': self._extract_points_from_text(section.content or '')
                })
        
        return content
    
    def _parse_content_structure(self, text: str) -> List[Dict]:
        """解析内容结构，提取章节和要点"""
        sections = []
        lines = text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检测章节标题
            if line.startswith('#'):
                if current_section:
                    sections.append(current_section)
                
                title = line.lstrip('#').strip()
                current_section = {
                    'title': title,
                    'points': []
                }
            
            # 检测要点（以-或*开头）
            elif line.startswith(('- ', '* ')) and current_section:
                point = line[2:].strip()
                if len(point) > 5:
                    current_section['points'].append(point)
            
            # 检测编号列表（1. 2. 等）
            elif len(line) > 2 and line[0].isdigit() and line[1] == '.' and current_section:
                point = line[2:].strip()
                if len(point) > 5:
                    current_section['points'].append(point)
        
        if current_section:
            sections.append(current_section)
        
        return sections[:8]  # 最多8个章节
    
    def _extract_points_from_text(self, text: str) -> List[str]:
        """从文本中提取要点"""
        if not text:
            return []
        
        import re
        sentences = re.split(r'[。！？.!?]', text)
        points = [s.strip() for s in sentences if len(s.strip()) > 15]
        return points[:5]
    
    def _generate_slides_from_content(self, content: Dict, paper: Paper) -> List[str]:
        """基于内容生成幻灯片（回退方法）"""
        slides = []
        
        # 1. 封面页
        slides.append(self._generate_cover_slide(content))
        
        # 2. 研究背景
        slides.append(self._generate_background_slide(content))
        
        # 3. 核心内容页（每个章节一页）
        for section in content['sections'][:6]:
            slide = self._generate_content_slide(section)
            if slide:
                slides.append(slide)
        
        # 4. 总结页
        slides.append(self._generate_summary_slide())
        
        return slides
    
    def _generate_slides_with_llm(self, content: Dict, paper: Paper) -> List[str]:
        """使用LLM生成幻灯片"""
        # 暂时使用回退方法，后续可以添加LLM优化
        return self._generate_slides_from_content(content, paper)
    
    def _generate_cover_slide(self, content: Dict) -> str:
        """生成精美封面页"""
        authors = ', '.join(content['authors'][:3]) if content['authors'] else 'Unknown'
        if len(content['authors']) > 3:
            authors += ' et al.'
        
        return f'''<section class="cover-slide">
    <div class="cover-content">
        <div class="cover-badge">学术论文</div>
        <h1 class="cover-title">{content['title']}</h1>
        <div class="cover-divider"></div>
        <p class="cover-authors">{authors}</p>
        <p class="cover-meta">{content['publication']} {content['year']}</p>
    </div>
    <div class="cover-decoration">
        <div class="circle circle-1"></div>
        <div class="circle circle-2"></div>
        <div class="circle circle-3"></div>
    </div>
</section>'''
    
    def _generate_background_slide(self, content: Dict) -> str:
        """生成研究背景页"""
        abstract = content.get('abstract', '')
        
        import re
        sentences = re.split(r'[。！？.!?]', abstract)
        key_points = [s.strip() for s in sentences[:3] if len(s.strip()) > 10]
        
        if not key_points:
            key_points = ['研究背景介绍', '核心问题阐述', '研究意义说明']
        
        points_html = '\n'.join([f'<li class="bg-point">{p}</li>' for p in key_points])
        
        return f'''<section class="bg-slide">
    <h2 class="section-title">
        <span class="title-icon">💡</span>
        研究背景与动机
    </h2>
    <div class="bg-content">
        <ul class="bg-list">
            {points_html}
        </ul>
    </div>
</section>'''
    
    def _generate_content_slide(self, section: Dict) -> str:
        """生成内容页 - 深度展示"""
        title = section.get('title', '内容')
        points = section.get('points', [])
        
        if not points:
            return None
        
        # 根据要点数量选择布局
        if len(points) <= 3:
            return self._generate_card_layout(title, points)
        else:
            return self._generate_list_layout(title, points)
    
    def _generate_card_layout(self, title: str, points: List[str]) -> str:
        """卡片式布局 - 适合少量要点"""
        cards_html = ''
        icons = ['🔬', '📊', '⚡', '🎯', '💡']
        
        for i, point in enumerate(points[:3]):
            icon = icons[i % len(icons)]
            # 提取标题和描述
            if ':' in point or '：' in point:
                parts = point.replace('：', ':').split(':', 1)
                card_title = parts[0].strip()[:20]
                card_desc = parts[1].strip()[:80]
            else:
                card_title = point[:20] if len(point) > 20 else point
                card_desc = point[:80]
            
            cards_html += f'''
            <div class="content-card">
                <div class="card-icon">{icon}</div>
                <h3 class="card-title">{card_title}</h3>
                <p class="card-desc">{card_desc}</p>
            </div>'''
        
        return f'''<section class="content-slide card-layout">
    <h2 class="section-title">{title}</h2>
    <div class="cards-container">
        {cards_html}
    </div>
</section>'''
    
    def _generate_list_layout(self, title: str, points: List[str]) -> str:
        """列表式布局 - 适合多个要点"""
        items_html = ''
        
        for i, point in enumerate(points[:5]):
            # 提取要点标题
            if ':' in point or '：' in point:
                parts = point.replace('：', ':').split(':', 1)
                item_title = parts[0].strip()[:25]
                item_desc = parts[1].strip()[:60]
            else:
                item_title = point[:30]
                item_desc = point[30:90] if len(point) > 30 else ''
            
            items_html += f'''
            <div class="list-item">
                <div class="item-number">{i+1}</div>
                <div class="item-content">
                    <h4 class="item-title">{item_title}</h4>
                    <p class="item-desc">{item_desc}</p>
                </div>
            </div>'''
        
        return f'''<section class="content-slide list-layout">
    <h2 class="section-title">{title}</h2>
    <div class="list-container">
        {items_html}
    </div>
</section>'''
    
    def _generate_summary_slide(self) -> str:
        """生成总结页"""
        return '''<section class="summary-slide">
    <div class="summary-content">
        <h2 class="summary-title">总结与展望</h2>
        <div class="summary-divider"></div>
        <div class="summary-points">
            <div class="sum-point">
                <div class="sum-icon">✓</div>
                <span>核心贡献</span>
            </div>
            <div class="sum-point">
                <div class="sum-icon">✓</div>
                <span>技术创新</span>
            </div>
            <div class="sum-point">
                <div class="sum-icon">✓</div>
                <span>应用价值</span>
            </div>
        </div>
        <p class="summary-thanks">谢谢观看 · Q&A</p>
    </div>
</section>'''
    
    def _wrap_in_html(self, title: str, slides: List[str]) -> str:
        """包装成完整HTML - 现代化美观设计"""
        slides_html = '\n'.join(slides)
        
        return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.5.0/reveal.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #667eea;
            --primary-dark: #5a67d8;
            --secondary: #764ba2;
            --accent: #f093fb;
            --dark: #1a202c;
            --light: #f7fafc;
            --gray: #718096;
            --success: #48bb78;
        }}
        
        .reveal {{
            font-family: 'Noto Sans SC', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        
        .reveal .slides {{
            text-align: left;
        }}
        
        .reveal section {{
            padding: 0;
            height: 100%;
            display: flex;
            flex-direction: column;
            background: white;
        }}
        
        /* 封面页样式 */
        .cover-slide {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            overflow: hidden;
        }}
        
        .cover-content {{
            text-align: center;
            z-index: 10;
            padding: 40px;
        }}
        
        .cover-badge {{
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 8px 20px;
            border-radius: 20px;
            font-size: 0.9em;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
        }}
        
        .cover-title {{
            font-size: 2.2em;
            font-weight: 700;
            margin: 0 0 20px 0;
            line-height: 1.3;
            color: white;
        }}
        
        .cover-divider {{
            width: 80px;
            height: 4px;
            background: rgba(255,255,255,0.5);
            margin: 20px auto;
            border-radius: 2px;
        }}
        
        .cover-authors {{
            font-size: 1.2em;
            margin: 20px 0 10px 0;
            opacity: 0.9;
            color: white;
        }}
        
        .cover-meta {{
            font-size: 1em;
            opacity: 0.7;
            color: white;
        }}
        
        .cover-decoration {{
            position: absolute;
            width: 100%;
            height: 100%;
            top: 0;
            left: 0;
        }}
        
        .circle {{
            position: absolute;
            border-radius: 50%;
            background: rgba(255,255,255,0.1);
        }}
        
        .circle-1 {{
            width: 300px;
            height: 300px;
            top: -100px;
            right: -100px;
        }}
        
        .circle-2 {{
            width: 200px;
            height: 200px;
            bottom: -50px;
            left: -50px;
        }}
        
        .circle-3 {{
            width: 150px;
            height: 150px;
            bottom: 100px;
            right: 10%;
        }}
        
        /* 通用标题样式 */
        .section-title {{
            font-size: 1.8em;
            font-weight: 600;
            color: var(--dark);
            margin: 40px 40px 30px 40px;
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        .title-icon {{
            font-size: 1.2em;
        }}
        
        /* 背景页样式 */
        .bg-slide {{
            background: linear-gradient(180deg, #f7fafc 0%, #edf2f7 100%);
        }}
        
        .bg-content {{
            padding: 0 60px;
            flex: 1;
            display: flex;
            align-items: center;
        }}
        
        .bg-list {{
            list-style: none;
            padding: 0;
            margin: 0;
            width: 100%;
        }}
        
        .bg-point {{
            background: white;
            padding: 25px 30px;
            margin-bottom: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            font-size: 1.1em;
            line-height: 1.6;
            border-left: 4px solid var(--primary);
        }}
        
        /* 内容页 - 卡片布局 */
        .content-slide {{
            background: #f7fafc;
        }}
        
        .cards-container {{
            display: flex;
            gap: 30px;
            padding: 20px 40px 40px 40px;
            justify-content: center;
            flex: 1;
            align-items: center;
        }}
        
        .content-card {{
            background: white;
            border-radius: 16px;
            padding: 35px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            flex: 1;
            max-width: 320px;
            text-align: center;
            transition: transform 0.3s ease;
        }}
        
        .content-card:hover {{
            transform: translateY(-10px);
        }}
        
        .card-icon {{
            font-size: 3em;
            margin-bottom: 20px;
        }}
        
        .card-title {{
            font-size: 1.3em;
            font-weight: 600;
            color: var(--dark);
            margin: 0 0 15px 0;
        }}
        
        .card-desc {{
            font-size: 0.95em;
            color: var(--gray);
            line-height: 1.6;
            margin: 0;
        }}
        
        /* 内容页 - 列表布局 */
        .list-container {{
            padding: 0 60px 40px 60px;
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        
        .list-item {{
            display: flex;
            align-items: flex-start;
            gap: 20px;
            background: white;
            padding: 25px 30px;
            margin-bottom: 15px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.06);
        }}
        
        .item-number {{
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 1.1em;
            flex-shrink: 0;
        }}
        
        .item-content {{
            flex: 1;
        }}
        
        .item-title {{
            font-size: 1.2em;
            font-weight: 600;
            color: var(--dark);
            margin: 0 0 8px 0;
        }}
        
        .item-desc {{
            font-size: 0.95em;
            color: var(--gray);
            line-height: 1.5;
            margin: 0;
        }}
        
        /* 总结页样式 */
        .summary-slide {{
            background: linear-gradient(135deg, var(--dark) 0%, #2d3748 100%);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .summary-content {{
            text-align: center;
        }}
        
        .summary-title {{
            font-size: 2.5em;
            font-weight: 700;
            margin: 0 0 20px 0;
            color: white;
        }}
        
        .summary-divider {{
            width: 60px;
            height: 4px;
            background: linear-gradient(90deg, var(--primary), var(--accent));
            margin: 0 auto 40px auto;
            border-radius: 2px;
        }}
        
        .summary-points {{
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-bottom: 50px;
        }}
        
        .sum-point {{
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 1.2em;
        }}
        
        .sum-icon {{
            width: 30px;
            height: 30px;
            background: var(--success);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.9em;
        }}
        
        .summary-thanks {{
            font-size: 1.5em;
            opacity: 0.8;
            margin-top: 30px;
        }}
    </style>
</head>
<body>
    <div class="reveal">
        <div class="slides">
            {slides_html}
        </div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.5.0/reveal.min.js"></script>
    <script>
        Reveal.initialize({{
            hash: true,
            slideNumber: 'c/t',
            transition: 'slide',
            transitionSpeed: 'default',
            backgroundTransition: 'fade',
            controls: true,
            progress: true,
            center: false,
            width: 1200,
            height: 700,
            margin: 0.04
        }});
    </script>
</body>
</html>'''
    
    def _save_html(self, html: str, title: str) -> str:
        """保存HTML文件"""
        from utils.helpers import sanitize_filename
        
        output_dir = Path("outputs/ppts")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        safe_title = sanitize_filename(title[:50])
        output_file = output_dir / f"{safe_title}.html"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return str(output_file)
