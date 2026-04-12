"""增强版 PDF 解析器 - 保留标题层级、表格、列表等结构"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pdfplumber
from typing import List, Dict, Optional, Tuple
import re
from models.paper import Paper, Section


class EnhancedPDFParser:
    """增强版 PDF 解析器 - 使用 pdfplumber 布局分析"""
    
    def __init__(self):
        # 标题识别模式
        self.title_patterns = [
            r'^[A-Z][^.!?]*(?:\s+[A-Z][^.!?]*)*$',  # 全大写标题
            r'^\d+\.\s+[A-Z]',  # 数字开头的标题
            r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$',  # 首字母大写的标题
        ]
        
        # 章节关键词
        self.section_keywords = [
            'abstract', 'introduction', 'related work', 'method', 'methodology',
            'approach', 'results', 'discussion', 'conclusion', 'references',
            'acknowledgments', 'future work', 'experiments', 'background',
            'model', 'architecture', 'analysis', 'evaluation', 'dataset',
            'implementation', 'training', 'inference', 'performance'
        ]
        
        # 列表标记
        self.list_patterns = [
            r'^\s*[-•●○■□▪▸▹]\s+',  # 项目符号
            r'^\s*\d+[.)\s]',  # 数字列表
            r'^\s*[a-z][.)\s]',  # 字母列表
            r'^\s*\([a-z0-9]+\)',  # 括号列表
        ]
    
    def parse(self, file_path: str) -> Paper:
        """解析 PDF 文件
        
        Args:
            file_path: PDF 文件路径
            
        Returns:
            Paper: 解析后的论文对象
        """
        with pdfplumber.open(file_path) as pdf:
            # 提取每页的文本和布局信息
            pages_data = []
            for page in pdf.pages:
                page_data = self._extract_page_data(page)
                pages_data.append(page_data)
            
            # 合并所有页面数据
            full_text = self._merge_pages(pages_data)
            
            # 提取元信息
            title = self._extract_title(pages_data)
            authors = self._extract_authors(pages_data)
            abstract = self._extract_abstract(pages_data)
            
            # 提取结构化章节
            sections = self._extract_structured_sections(pages_data)
            
            # 提取表格
            tables = self._extract_tables(pdf)
            
            paper = Paper(
                title=title,
                authors=authors,
                abstract=abstract,
                sections=sections,
                file_path=file_path,
                total_pages=len(pdf.pages)
            )
            
            # 将表格信息附加到 sections 中
            if tables:
                tables_section = Section(
                    title="Tables",
                    content="\n\n".join([t['markdown'] for t in tables]),
                    level=1
                )
                paper.sections.append(tables_section)
            
            return paper
    
    def _extract_page_data(self, page) -> Dict:
        """提取页面数据（文本 + 布局信息）"""
        # 提取文本
        text = page.extract_text()
        
        # 提取字符级别的详细信息（字体大小、粗细等）
        chars = page.chars
        
        # 分析字体大小
        font_sizes = {}
        for char in chars:
            size = char.get('size', 12)
            font_sizes[size] = font_sizes.get(size, 0) + 1
        
        # 找到主要字体大小（正文）
        main_font_size = max(font_sizes.items(), key=lambda x: x[1])[0] if font_sizes else 12
        
        # 识别标题（字体较大的文本）
        title_lines = []
        body_lines = []
        
        if text:
            lines = text.split('\n')
            y_positions = page.chars
            if y_positions:
                # 按 y 坐标分组字符（同一行）
                rows = {}
                for char in y_positions:
                    y = round(char.get('top', 0), 1)
                    if y not in rows:
                        rows[y] = []
                    rows[y].append(char)
                
                # 分析每行的字体大小
                for y, row_chars in rows.items():
                    avg_size = sum(c.get('size', 12) for c in row_chars) / len(row_chars)
                    line_text = ''.join(c.get('text', '') for c in row_chars).strip()
                    
                    if avg_size > main_font_size * 1.2 and line_text:  # 字体较大，可能是标题
                        title_lines.append({
                            'text': line_text,
                            'y': y,
                            'font_size': avg_size
                        })
                    elif line_text:
                        body_lines.append({
                            'text': line_text,
                            'y': y,
                            'font_size': avg_size
                        })
        
        return {
            'page_number': page.page_number,
            'text': text,
            'chars': chars,
            'font_sizes': font_sizes,
            'main_font_size': main_font_size,
            'title_lines': title_lines,
            'body_lines': body_lines,
            'width': page.width,
            'height': page.height
        }
    
    def _merge_pages(self, pages_data: List[Dict]) -> str:
        """合并页面文本"""
        return '\n\n'.join([p['text'] for p in pages_data if p['text']])
    
    def _extract_title(self, pages_data: List[Dict]) -> str:
        """从第一页提取标题"""
        if not pages_data:
            return "Untitled Paper"
        
        first_page = pages_data[0]
        
        # 优先使用识别到的标题行
        if first_page.get('title_lines'):
            # 找到 y 坐标最小的标题（最上面的）
            title_candidates = sorted(first_page['title_lines'], key=lambda x: x['y'])
            if title_candidates:
                title = title_candidates[0]['text']
                if len(title) > 5 and len(title) < 200:
                    return title
        
        # 回退到文本分析
        text = first_page.get('text', '')
        lines = text.split('\n')[:20]
        
        exclude_keywords = [
            'received', 'accepted', 'published', 'doi', 'copyright',
            'keywords', 'correspondence', 'email', 'address',
            'volume', 'issue', 'pages', 'issn', 'isbn',
            'article', 'history', 'dates'
        ]
        
        for line in lines:
            line = line.strip()
            if len(line) < 10 or len(line) > 300:
                continue
            
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in exclude_keywords):
                continue
            
            if re.match(r'^(\d+[:/-])+\d+$', line):
                continue
            
            if any(re.match(pattern, line) for pattern in self.title_patterns):
                words = line.split()
                if len(words) >= 3:
                    return line
        
        # 默认返回
        for line in lines:
            line = line.strip()
            if len(line) >= 10 and len(line) < 200:
                line_lower = line.lower()
                if not any(keyword in line_lower for keyword in exclude_keywords):
                    return line
        
        return "Untitled Paper"
    
    def _extract_authors(self, pages_data: List[Dict]) -> List[str]:
        """提取作者信息"""
        if not pages_data:
            return []
        
        first_page = pages_data[0]
        text = first_page.get('text', '')
        lines = text.split('\n')[:30]
        
        authors = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if '@' in line or 'university' in line.lower() or 'institute' in line.lower():
                # 检查前一行
                prev_line = lines[i-1].strip() if i > 0 else ""
                if prev_line and len(prev_line) < 200:
                    # 分割作者
                    potential_authors = []
                    for sep in ['and', ',', '\n']:
                        if sep in prev_line:
                            potential_authors.extend([a.strip() for a in prev_line.split(sep)])
                    
                    if not potential_authors:
                        potential_authors = [prev_line]
                    
                    # 过滤
                    for author in potential_authors:
                        if author and len(author) > 2 and len(author) < 100:
                            authors.append(author)
                
                break
        
        return list(set(authors))[:10]
    
    def _extract_abstract(self, pages_data: List[Dict]) -> str:
        """提取摘要"""
        if not pages_data:
            return ""
        
        # 合并前两页的文本
        text = ""
        for page_data in pages_data[:2]:
            text += page_data.get('text', '') + "\n"
        
        # 查找 Abstract
        abstract_match = re.search(
            r'(?i)abstract\s*:?\s*(.*?)(?=\n\s*(?:introduction|keywords|\d+\.|1\s+Introduction))',
            text,
            re.DOTALL
        )
        
        if abstract_match:
            abstract = abstract_match.group(1).strip()
            return abstract[:2000]
        
        return ""
    
    def _extract_structured_sections(self, pages_data: List[Dict]) -> List[Section]:
        """提取结构化的章节"""
        if not pages_data:
            return []
        
        # 合并所有文本
        full_text = ""
        for page_data in pages_data:
            full_text += page_data.get('text', '') + "\n"
        
        # 识别章节
        sections = []
        lines = full_text.split('\n')
        
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_section:
                    # 空行可能表示段落结束
                    if current_content and current_content[-1] != '':
                        current_content.append('')
                continue
            
            # 检测是否是章节标题
            level = self._detect_heading_level(line)
            
            if level > 0:
                # 保存之前的章节
                if current_section:
                    current_section.content = '\n'.join(current_content).strip()
                    sections.append(current_section)
                
                # 创建新章节
                current_section = Section(
                    title=line,
                    content="",
                    level=level,
                    subsections=[]
                )
                current_content = []
            elif current_section:
                current_content.append(line)
        
        # 保存最后一个章节
        if current_section:
            current_section.content = '\n'.join(current_content).strip()
            sections.append(current_section)
        
        # 构建章节树
        return self._build_section_tree(sections)
    
    def _detect_heading_level(self, line: str) -> int:
        """检测标题级别"""
        line_lower = line.lower()
        
        # 一级标题：主要章节
        if line_lower in self.section_keywords:
            return 1
        
        # 数字编号的标题
        if re.match(r'^\d+\s+[A-Z]', line):  # 1 Introduction
            return 1
        
        if re.match(r'^\d+\.\d+\s+', line):  # 1.1 Background
            return 2
        
        if re.match(r'^\d+\.\d+\.\d+\s+', line):  # 1.1.1 Detail
            return 3
        
        # 全大写的短行可能是标题
        if line.isupper() and len(line) < 100 and len(line) > 5:
            return 2
        
        return 0
    
    def _build_section_tree(self, sections: List[Section]) -> List[Section]:
        """构建章节树"""
        if not sections:
            return []
        
        root_sections = []
        stack = []
        
        for section in sections:
            while stack and stack[-1].level >= section.level:
                stack.pop()
            
            if stack:
                stack[-1].subsections.append(section)
            else:
                root_sections.append(section)
            
            stack.append(section)
        
        return root_sections
    
    def _extract_tables(self, pdf) -> List[Dict]:
        """提取表格"""
        tables = []
        
        for page in pdf.pages:
            page_tables = page.extract_tables()
            for i, table in enumerate(page_tables):
                if table:
                    tables.append({
                        'page': page.page_number,
                        'table_index': i,
                        'data': table,
                        'markdown': self._table_to_markdown(table)
                    })
        
        return tables
    
    def _table_to_markdown(self, table_data: List[List[str]]) -> str:
        """将表格转换为 Markdown 格式"""
        if not table_data:
            return ""
        
        lines = []
        
        # 表头
        if table_data[0]:
            header = " | ".join([str(cell).strip() if cell else "" for cell in table_data[0]])
            lines.append(f"| {header} |")
            
            # 分隔线
            separator = " | ".join(["---"] * len(table_data[0]))
            lines.append(f"| {separator} |")
        
        # 表体
        for row in table_data[1:]:
            if row:
                cells = " | ".join([str(cell).strip() if cell else "" for cell in row])
                lines.append(f"| {cells} |")
        
        return "\n".join(lines)
    
    def parse_to_markdown(self, file_path: str) -> str:
        """解析 PDF 并生成 Markdown 格式"""
        with pdfplumber.open(file_path) as pdf:
            pages_data = []
            for page in pdf.pages:
                page_data = self._extract_page_data(page)
                pages_data.append(page_data)
            
            # 生成 Markdown
            markdown_parts = []
            
            # 标题
            title = self._extract_title(pages_data)
            markdown_parts.append(f"# {title}\n")
            
            # 作者
            authors = self._extract_authors(pages_data)
            if authors:
                markdown_parts.append(f"**Authors**: {', '.join(authors)}\n")
            
            # 摘要
            abstract = self._extract_abstract(pages_data)
            if abstract:
                markdown_parts.append("## Abstract\n")
                markdown_parts.append(f"{abstract}\n")
            
            # 章节
            sections = self._extract_structured_sections(pages_data)
            for section in sections:
                markdown_parts.append(self._section_to_markdown(section))
            
            # 表格
            tables = self._extract_tables(pdf)
            if tables:
                markdown_parts.append("## Tables\n")
                for table in tables:
                    markdown_parts.append(f"### Table {table['table_index']} (Page {table['page']})\n")
                    markdown_parts.append(table['markdown'])
                    markdown_parts.append("\n")
            
            return "\n".join(markdown_parts)
    
    def _section_to_markdown(self, section: Section) -> str:
        """将章节转换为 Markdown"""
        prefix = "#" * (section.level + 1)
        markdown = f"{prefix} {section.title}\n\n"
        
        if section.content:
            # 识别内容中的列表
            lines = section.content.split('\n')
            formatted_lines = []
            
            for line in lines:
                if self._is_list_item(line):
                    formatted_lines.append(f"- {line.strip()}")
                else:
                    formatted_lines.append(line)
            
            markdown += "\n".join(formatted_lines)
            markdown += "\n\n"
        
        # 子章节
        for subsection in section.subsections:
            markdown += self._section_to_markdown(subsection)
        
        return markdown
    
    def _is_list_item(self, line: str) -> bool:
        """检查是否是列表项"""
        line = line.strip()
        return any(re.match(pattern, line) for pattern in self.list_patterns)


# 测试函数
def test_enhanced_parser(pdf_path: str):
    """测试增强版解析器"""
    print(f"\n{'='*60}")
    print(f"测试增强版 PDF 解析器")
    print(f"{'='*60}\n")
    
    parser = EnhancedPDFParser()
    
    # 解析 PDF
    paper = parser.parse(pdf_path)
    
    print(f"✓ 解析完成")
    print(f"  标题：{paper.title}")
    print(f"  作者：{len(paper.authors)} 位")
    print(f"  摘要：{len(paper.abstract)} 字符")
    print(f"  章节：{len(paper.sections)} 个")
    
    # 生成 Markdown
    markdown = parser.parse_to_markdown(pdf_path)
    
    # 保存
    output_file = Path(pdf_path).parent / f"{Path(pdf_path).stem}_enhanced.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    print(f"\n✓ Markdown 已保存到：{output_file}")
    print(f"  长度：{len(markdown)} 字符")
    print(f"  行数：{len(markdown.splitlines())} 行")
    
    # 分析结构
    print(f"\n{'='*60}")
    print("Markdown 结构分析:")
    print(f"{'='*60}")
    
    lines = markdown.splitlines()[:100]
    h1 = len([l for l in lines if l.startswith('# ')])
    h2 = len([l for l in lines if l.startswith('## ')])
    h3 = len([l for l in lines if l.startswith('### ')])
    tables = len([l for l in lines if l.startswith('|')])
    lists = len([l for l in lines if l.strip().startswith('- ')])
    
    print(f"  H1: {h1} 个")
    print(f"  H2: {h2} 个")
    print(f"  H3: {h3} 个")
    print(f"  表格行：{tables} 行")
    print(f"  列表项：{lists} 个")
    
    # 预览
    print(f"\n{'='*60}")
    print("Markdown 预览（前 50 行）:")
    print(f"{'='*60}")
    for i, line in enumerate(lines[:50], 1):
        print(f"{i:3d} | {line}")
    
    print(f"\n{'='*60}")
    print("测试完成!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        test_enhanced_parser(sys.argv[1])
    else:
        print("请提供 PDF 文件路径")
