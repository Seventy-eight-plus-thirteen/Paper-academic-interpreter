"""论文数据模型"""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class Section:
    """论文章节"""
    title: str
    content: str
    level: int
    subsections: List['Section'] = field(default_factory=list)
    page_start: Optional[int] = None
    page_end: Optional[int] = None


@dataclass
class Paper:
    """论文数据模型"""
    title: str
    authors: List[str]
    abstract: str
    sections: List[Section]
    keywords: List[str] = field(default_factory=list)
    doi: Optional[str] = None
    publication: Optional[str] = None
    year: Optional[int] = None
    file_path: str = ""
    total_pages: int = 0
    created_at: datetime = field(default_factory=datetime.now)
