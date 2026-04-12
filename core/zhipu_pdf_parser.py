"""智谱 AI 文件解析 API - PDF 解析模块"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
import time
from typing import List, Optional
import re
from models.paper import Paper, Section


class ZhipuPDFParser:
    """智谱 AI PDF 解析器 - 使用文件解析 API"""
    
    def __init__(self, api_key: str):
        """初始化智谱 PDF 解析器
        
        Args:
            api_key: 智谱 AI API Key
        """
        self.api_key = api_key
        self.base_url = "https://open.bigmodel.cn/api/paas/v4/files/parser"
        self.ocr_url = "https://open.bigmodel.cn/api/paas/v4/files/ocr"
        
    def parse(self, file_path: str, tool_type: str = "expert") -> Paper:
        """解析 PDF 文件
        
        Args:
            file_path: PDF 文件路径
            tool_type: 解析工具类型 (lite, expert, prime)
                - lite: 快速版，适合简单文档
                - expert: 专业版，性价比高，推荐
                - prime: 高级版，精度最高
            
        Returns:
            Paper: 解析后的论文对象
        """
        print(f"开始使用智谱 AI 解析 PDF: {Path(file_path).name}")
        print(f"  解析模式：{tool_type}")
        
        # 调用智谱文件解析 API
        content = self._parse_with_api(file_path, tool_type)
        
        if not content:
            raise Exception("智谱 AI 解析失败，未获取到内容")
        
        print(f"  ✓ 解析成功：{len(content)} 字符，{len(content.splitlines())} 行")
        
        # 从解析内容中提取论文信息
        title = self._extract_title(content)
        authors = self._extract_authors(content)
        abstract = self._extract_abstract(content)
        sections = self._extract_sections(content)
        
        return Paper(
            title=title,
            authors=authors,
            abstract=abstract,
            sections=sections,
            file_path=file_path,
            total_pages=0  # API 不提供页数信息
        )
    
    def _parse_with_api(self, file_path: str, tool_type: str) -> Optional[str]:
        """调用智谱文件解析 API
        
        Args:
            file_path: PDF 文件路径
            tool_type: 解析工具类型
            
        Returns:
            Optional[str]: 解析后的文本内容，失败返回 None
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}'
        }
        
        # 1. 创建解析任务
        create_url = f"{self.base_url}/create"
        
        with open(file_path, 'rb') as f:
            files = {
                'file': (Path(file_path).name, f, 'application/pdf')
            }
            
            data = {
                'tool_type': tool_type,
                'file_type': 'PDF'
            }
            
            print(f"  正在上传 PDF 文件...")
            response = requests.post(create_url, headers=headers, files=files, data=data, timeout=120)
            result = response.json()
            
            if response.status_code != 200:
                error_msg = result.get('error', {}).get('message', str(result))
                print(f"  ✗ 上传失败：{error_msg}")
                return None
            
            task_id = result.get('task_id')
            if not task_id:
                print(f"  ✗ 未获取到 task_id")
                return None
            
            print(f"  ✓ 任务创建成功：task_id={task_id}")
        
        # 2. 轮询获取解析结果
        result_url = f"{self.base_url}/result/{task_id}/text"
        print(f"  正在等待解析完成...")
        
        max_retries = 60  # 最多等待 60*2=120 秒
        for i in range(max_retries):
            time.sleep(2)
            
            response = requests.get(result_url, headers=headers, timeout=60)
            result = response.json()
            
            status = result.get('status', 'processing')
            
            if status == 'succeeded':
                # 获取解析内容
                content = result.get('content')
                if content:
                    print(f"  ✓ 解析完成")
                    return content
                else:
                    # 尝试下载链接
                    download_link = result.get('download_link')
                    if download_link:
                        response = requests.get(download_link, timeout=60)
                        return response.text
            
            elif status == 'failed':
                print(f"  ✗ 解析失败")
                return None
        
        print(f"  ⚠ 等待超时")
        return None
    
    def _extract_title(self, content: str) -> str:
        """从解析内容中提取标题"""
        lines = content.split('\n')[:20]
        
        # 第一行通常就是标题
        if lines and len(lines[0].strip()) > 10:
            return lines[0].strip()
        
        # 排除的元数据关键词
        exclude_keywords = [
            'received', 'accepted', 'published', 'doi', 'copyright',
            'keywords', 'correspondence', 'email', 'address',
            'volume', 'issue', 'pages', 'issn', 'isbn',
            'article', 'history', 'dates', 'google', 'brain', 'research'
        ]
        
        for line in lines:
            line = line.strip()
            # 标题通常是最长的一行且足够长
            if len(line) < 15 or len(line) > 300:
                continue
            
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in exclude_keywords):
                continue
            
            # 标题通常包含多个单词且不是邮箱
            if '@' in line:
                continue
                
            words = line.split()
            if len(words) >= 4:
                return line
        
        # 如果找不到，返回第一行非空文本
        for line in lines:
            line = line.strip()
            if len(line) >= 15 and len(line) < 200:
                return line
        
        return "Untitled Paper"
    
    def _extract_authors(self, content: str) -> List[str]:
        """从解析内容中提取作者列表"""
        lines = content.split('\n')[:30]
        authors = []
        
        # 查找包含邮箱的行，提取上一行作为作者
        for i, line in enumerate(lines):
            line = line.strip()
            if '@' in line:
                # 找到邮箱，尝试从上一行提取作者
                if i > 0:
                    prev_line = lines[i-1].strip()
                    # 移除特殊符号 * † ‡
                    prev_line = prev_line.replace('*', '').replace('†', '').replace('‡', '').strip()
                    if prev_line and len(prev_line) < 100:
                        # 分割作者（通常用逗号或"and"分隔）
                        authors.extend([a.strip() for a in prev_line.split('and')])
                        authors.extend([a.strip() for a in prev_line.split(',')])
        
        # 过滤和去重
        authors = [a for a in authors if a and len(a) > 2 and '@' not in a]
        authors = [a for a in authors if not any(k in a.lower() for k in ['google', 'brain', 'research', 'university'])]
        return list(set(authors))[:10]
    
    def _extract_abstract(self, content: str) -> str:
        """从解析内容中提取摘要"""
        # 查找 Abstract 关键词
        abstract_match = re.search(
            r'(?i)^abstract\s*$[\s\S]*?(?=\n\s*(?:introduction|keywords|\d+\.))',
            content,
            re.DOTALL | re.MULTILINE
        )
        
        if abstract_match:
            abstract = abstract_match.group(0).strip()
            # 移除 "Abstract" 标题
            abstract = re.sub(r'(?i)^abstract\s*$', '', abstract).strip()
            return abstract[:2000]
        
        # 尝试查找 "Abstract" 单独一行的情况
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().lower() == 'abstract':
                # 收集后续内容直到遇到下一个章节
                abstract_lines = []
                for j in range(i+1, min(i+15, len(lines))):
                    next_line = lines[j].strip()
                    if next_line.lower() in ['introduction', 'keywords'] or re.match(r'^\d+\.', next_line) or next_line.startswith('∗'):
                        break
                    abstract_lines.append(next_line)
                
                abstract = '\n'.join(abstract_lines).strip()
                if abstract and len(abstract) > 100:
                    return abstract[:2000]
        
        return ""
    
    def _extract_sections(self, content: str) -> List[Section]:
        """从解析内容中提取章节结构"""
        sections = []
        lines = content.split('\n')
        
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
        
        # 一级标题关键词
        section_keywords = [
            'abstract', 'introduction', 'related work', 'method', 'methodology',
            'approach', 'results', 'discussion', 'conclusion', 'references',
            'acknowledgments', 'future work', 'experiments', 'background'
        ]
        
        if line_lower in section_keywords:
            return 1
        
        # 数字编号的标题
        if re.match(r'^\d+\.\s+[A-Z]', line):
            return 1
        
        if re.match(r'^\d+\.\d+\s+', line):
            return 2
        
        if re.match(r'^\d+\.\d+\.\d+\s+', line):
            return 3
        
        # 大写字母开头的短行可能是标题
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
