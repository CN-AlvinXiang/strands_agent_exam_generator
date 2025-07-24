import logging
import requests
import re
from ..config import server_config

def send_to_flask_service(markdown_content: str) -> dict:
    """
    发送Markdown内容到Flask渲染服务。
    
    将生成的Markdown格式考试内容发送到Flask渲染服务，由渲染服务转换为交互式HTML。
    渲染服务会处理Markdown格式，生成包含交互元素的HTML页面，并返回访问URL。
    
    Args:
        markdown_content: Markdown格式的考试内容
        
    Returns:
        dict: 渲染服务的响应，包含生成的HTML页面URL
        
    示例响应:
    {
        "message": "保存成功\n查看链接http://localhost:5006/get_html/abc123"
    }
    """
    try:
        logging.info("发送Markdown内容到Flask渲染服务")
        
        # 确保markdown_content是字符串
        if isinstance(markdown_content, list):
            # 如果是列表，尝试提取文本内容
            content_str = ""
            for item in markdown_content:
                if isinstance(item, dict) and "text" in item:
                    content_str += item["text"]
                elif isinstance(item, str):
                    content_str += item
            markdown_content = content_str
        elif isinstance(markdown_content, dict) and "content" in markdown_content:
            # 如果是字典，尝试提取content字段
            markdown_content = markdown_content["content"]
        
        # 确保是字符串类型
        if not isinstance(markdown_content, str):
            markdown_content = str(markdown_content)
        
        # 处理可能的格式问题
        # 如果内容不是以"## "开头，检查是否有总结性文本
        if not markdown_content.strip().startswith("## "):
            # 尝试查找第一个"## "的位置
            pos = markdown_content.find("\n## ")
            if pos > 0:
                # 移除前面的总结性文本
                markdown_content = markdown_content[pos+1:]
                logging.info("移除了考试内容前的总结性文本")
        
        # 确保缩进格式正确（3个空格后跟减号会被Flask服务替换为4个空格）
        markdown_content = re.sub(r"^\s{3}-", "    -", markdown_content, flags=re.MULTILINE)
        
        # 发送请求到Flask服务
        response = requests.post(
            server_config.flask_service_url,
            data=markdown_content.encode('utf-8'),  # 确保数据是字节类型
            headers={"Content-Type": "text/plain; charset=utf-8"},
            timeout=10
        )
        
        # 检查响应状态
        response.raise_for_status()
        
        # 解析响应
        result = response.json()
        logging.info(f"渲染服务响应: {result}")
        
        return result
    except requests.exceptions.RequestException as e:
        logging.error(f"调用渲染服务失败: {str(e)}")
        raise Exception(f"调用渲染服务失败: {str(e)}")
    except ValueError as e:
        logging.error(f"解析渲染服务响应失败: {str(e)}")
        raise Exception(f"解析渲染服务响应失败: {str(e)}")
    except Exception as e:
        logging.error(f"渲染服务错误: {str(e)}")
        raise Exception(f"渲染服务错误: {str(e)}")
