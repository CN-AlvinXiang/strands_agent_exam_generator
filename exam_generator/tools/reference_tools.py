import logging
import re
import requests
from bs4 import BeautifulSoup
from strands import tool
from ..config import exam_config

def is_url(text):
    """
    检查文本是否为URL
    
    Args:
        text: 要检查的文本
        
    Returns:
        bool: 如果文本是URL则返回True，否则返回False
    """
    url_pattern = re.compile(
        r'^(?:http|https)://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain
        r'l*|'  # *
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or ipv4
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return bool(url_pattern.match(text))

def limit_reference_size(text, max_length):
    """
    限制参考资料文本大小
    
    Args:
        text: 原始文本
        max_length: 最大长度
        
    Returns:
        str: 截断后的文本
    """
    if len(text) <= max_length:
        return text
    
    # 截断文本，并添加提示信息
    truncated_text = text[:max_length]
    truncated_text += f"\n\n[内容已截断，原始长度: {len(text)}字符，已截断至: {max_length}字符]"
    
    return truncated_text

@tool
def process_reference(reference: str) -> str:
    """
    处理参考资料，判断是否为URL并获取内容。
    
    如果输入是URL，将获取URL内容并提取文本；
    如果输入是普通文本，将直接返回文本内容。
    
    处理过程会限制内容大小，并处理可能的错误。
    
    Args:
        reference: 参考资料文本或URL
        
    Returns:
        处理后的参考资料内容
        
    示例:
        >>> process_reference("https://example.com/article")
        "这是从URL获取的文章内容..."
        >>> process_reference("这是一段参考文本")
        "这是一段参考文本"
    """
    # 检查是否为空
    if not reference or not reference.strip():
        return ""
    
    # 检查是否为URL
    if is_url(reference):
        try:
            # 使用工具调用而不是直接函数调用
            return fetch_url_content(reference)
        except Exception as e:
            logging.warning(f"URL处理失败，将使用原始文本: {str(e)}")
            return reference
    
    return reference

@tool
def fetch_url_content(url: str) -> str:
    """
    获取URL内容并提取文本。
    
    此工具会访问指定的URL，下载内容，并提取其中的文本。
    支持各种网页格式，会自动处理HTML标签和格式。
    
    Args:
        url: 需要获取内容的URL，必须是完整的URL（包含http://或https://）
        
    Returns:
        提取的文本内容，已去除HTML标签和多余空白
        
    示例:
        >>> fetch_url_content("https://en.wikipedia.org/wiki/Python_(programming_language)")
        "Python is a high-level, general-purpose programming language..."
    """
    try:
        # 发送请求
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # 提取文本内容
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 移除脚本和样式元素
        for script_or_style in soup(["script", "style"]):
            script_or_style.extract()
        
        # 获取文本
        text = soup.get_text(separator='\n', strip=True)
        
        # 处理多余的空行
        lines = (line.strip() for line in text.splitlines())
        text = '\n'.join(line for line in lines if line)
        
        # 限制内容大小
        return limit_reference_size(text, exam_config.max_reference_length)
    except Exception as e:
        logging.error(f"获取URL内容失败: {str(e)}")
        raise Exception(f"获取URL内容失败: {str(e)}")
