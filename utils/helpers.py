"""通用工具函数"""


def sanitize_filename(filename: str) -> str:
    """清理文件名，移除Windows非法字符
    
    Args:
        filename: 原始文件名
        
    Returns:
        str: 清理后的安全文件名
    """
    if not filename:
        return "untitled"
    
    # Windows非法字符: < > : " / \ | ? *
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # 替换其他可能导致问题的字符
    filename = filename.replace('\n', '_').replace('\r', '_').replace('\t', '_')
    
    # 移除首尾空格并替换中间空格
    filename = filename.strip().replace(' ', '_')
    
    # 限制长度
    if len(filename) > 100:
        filename = filename[:100]
    
    # 确保不为空
    return filename if filename else "untitled"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """截断文本到指定长度
    
    Args:
        text: 原始文本
        max_length: 最大长度
        suffix: 截断后缀
        
    Returns:
        str: 截断后的文本
    """
    if not text or len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小
    
    Args:
        size_bytes: 文件大小（字节）
        
    Returns:
        str: 格式化后的大小字符串
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"
