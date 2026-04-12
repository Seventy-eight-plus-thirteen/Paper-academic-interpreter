"""PDF解析模块"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pdfplumber
from typing import List, Optional
import re
from models.paper import Paper, Section


class PDFParser:
    """PDF解析器"""
    
    def __init__(self):
        self.title_patterns = [
            r'^[A-Z][^.!?]*(?:\s+[A-Z][^.!?]*)*$',  # 全大写标题
            r'^\d+\.\s+[A-Z]',  # 数字开头的标题
            r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$',  # 首字母大写的标题
        ]
        self.section_keywords = [
            'abstract', 'introduction', 'related work', 'method', 'methodology',
            'approach', 'results', 'discussion', 'conclusion', 'references',
            'acknowledgments', 'future work', 'experiments', 'background'
        ]
    
    def parse(self, file_path: str) -> Paper:
        """解析PDF文件
        
        Args:
            file_path: PDF文件路径
            
        Returns:
            Paper: 解析后的论文对象
        """
        with pdfplumber.open(file_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
            
            title = self._extract_title(text, pdf.pages[0])
            authors = self._extract_authors(text)
            abstract = self._extract_abstract(text)
            sections = self._extract_sections(text)
            
            return Paper(
                title=title,
                authors=authors,
                abstract=abstract,
                sections=sections,
                file_path=file_path,
                total_pages=len(pdf.pages)
            )
    
    def _extract_title(self, text: str, first_page) -> str:
        """提取标题"""
        lines = text.split('\n')[:15]  # 增加搜索行数
        
        # 排除的元数据关键词
        exclude_keywords = [
            'received', 'accepted', 'published', 'doi', 'copyright',
            'keywords', 'correspondence', 'email', 'address',
            'volume', 'issue', 'pages', 'issn', 'isbn',
            'article', 'history', 'dates'
        ]
        
        for line in lines:
            line = line.strip()
            # 基本长度检查
            if len(line) < 10 or len(line) > 300:
                continue
            
            # 排除包含元数据关键词的行
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in exclude_keywords):
                continue
            
            # 排除纯数字或日期格式的行
            if re.match(r'^(\d+[:/-])+\d+$', line):
                continue
            
            # 检查是否符合标题模式
            if any(re.match(pattern, line) for pattern in self.title_patterns):
                # 进一步验证：标题通常包含多个单词
                words = line.split()
                if len(words) >= 3:
                    return line
        
        # 如果找不到合适的标题，返回第一行非空且足够长的行
        for line in lines:
            line = line.strip()
            if len(line) >= 10 and len(line) < 200:
                line_lower = line.lower()
                if not any(keyword in line_lower for keyword in exclude_keywords):
                    return line
        
        return "Untitled Paper"
    
    def _extract_authors(self, text: str) -> List[str]:
        """提取作者列表"""
        lines = text.split('\n')[:20]
        authors = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if '@' in line or 'university' in line.lower():
                prev_line = lines[i-1].strip() if i > 0 else ""
                if prev_line and len(prev_line) < 200:
                    authors.extend([a.strip() for a in prev_line.split('and')])
                    authors.extend([a.strip() for a in prev_line.split(',')])
                    break
        
        return list(set([a for a in authors if a and len(a) > 2]))[:10]
    
    def _extract_abstract(self, text: str) -> str:
        """提取摘要"""
        abstract_match = re.search(
            r'(?i)abstract\s*:?\s*(.*?)(?=\n\s*(?:introduction|keywords|\d+\.))',
            text,
            re.DOTALL
        )
        
        if abstract_match:
            abstract = abstract_match.group(1).strip()
            return abstract[:2000]
        
        return ""
    
    def _extract_sections(self, text: str) -> List[Section]:
        """提取章节结构"""
        sections = []
        lines = text.split('\n')
        
        current_section = None
        current_content = []
        current_level = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            level = self._detect_heading_level(line)
            
            if level > 0:
                if current_section:
                    current_section.content = '\n'.join(current_content).strip()
                    sections.append(current_section)
                
                current_section = Section(
                    title=line,
                    content="",
                    level=level,
                    subsections=[]
                )
                current_content = []
            elif current_section:
                current_content.append(line)
        
        if current_section:
            current_section.content = '\n'.join(current_content).strip()
            sections.append(current_section)
        
        return self._build_section_tree(sections)
    
    def _detect_heading_level(self, line: str) -> int:
        """检测标题级别"""
        line_lower = line.lower()
        
        if line_lower in self.section_keywords:
            return 1
        
        if re.match(r'^\d+\.\s+[A-Z]', line):
            return 1
        
        if re.match(r'^\d+\.\d+\s+', line):
            return 2
        
        if re.match(r'^\d+\.\d+\.\d+\s+', line):
            return 3
        
        if len(line) < 100 and line[0].isupper() and line[-1] not in '.!?':
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
