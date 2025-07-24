import logging
import os
from ..config import log_config

def setup_logging():
    """设置日志配置"""
    # 创建日志目录（如果需要）
    log_dir = os.path.dirname(log_config.file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 配置根日志记录器
    logging.basicConfig(
        level=getattr(logging, log_config.level),
        format=log_config.format,
        handlers=[
            logging.FileHandler(log_config.file),
            logging.StreamHandler()
        ]
    )
    
    # 配置Strands日志记录器
    strands_logger = logging.getLogger("strands")
    strands_logger.setLevel(getattr(logging, log_config.level))
    
    # 配置请求日志记录器
    requests_logger = logging.getLogger("requests")
    requests_logger.setLevel(logging.WARNING)
    
    # 配置urllib3日志记录器
    urllib3_logger = logging.getLogger("urllib3")
    urllib3_logger.setLevel(logging.WARNING)
    
    logging.info("日志系统初始化完成")

def get_logger(name):
    """获取指定名称的日志记录器"""
    return logging.getLogger(name)
