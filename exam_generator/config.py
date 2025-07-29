import os
import configparser
from pathlib import Path
from dataclasses import dataclass

@dataclass
class LLMConfig:
    """LLM配置"""
    model_id: str = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
    region_name: str = "us-east-1"  # 使用us-east-1区域
    max_tokens: int = 4000
    temperature: float = 0.7

@dataclass
class AWSConfig:
    """AWS配置"""
    profile_name: str = "default"  # AWS配置文件名称
    access_key: str = ""  # AWS访问密钥ID
    secret_key: str = ""  # AWS秘密访问密钥
    region: str = ""  # AWS区域
    
    def __post_init__(self):
        """初始化后自动加载AWS凭证"""
        self.load_aws_credentials()
    
    def load_aws_credentials(self):
        """从AWS配置文件加载凭证"""
        try:
            # 首先尝试从环境变量获取
            if os.environ.get("AWS_ACCESS_KEY_ID") and os.environ.get("AWS_SECRET_ACCESS_KEY"):
                self.access_key = os.environ.get("AWS_ACCESS_KEY_ID")
                self.secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
                self.region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
                print(f"✓ 从环境变量加载AWS凭证")
                return
            
            # 尝试从AWS配置文件加载
            aws_config_path = Path.home() / ".aws" / "credentials"
            aws_config_config_path = Path.home() / ".aws" / "config"
            
            if aws_config_path.exists():
                config = configparser.ConfigParser()
                config.read(aws_config_path)
                
                if self.profile_name in config:
                    profile = config[self.profile_name]
                    self.access_key = profile.get("aws_access_key_id", "")
                    self.secret_key = profile.get("aws_secret_access_key", "")
                    print(f"✓ 从AWS凭证文件加载配置 (profile: {self.profile_name})")
                else:
                    print(f"⚠️  AWS凭证文件中未找到profile: {self.profile_name}")
            
            # 尝试从AWS config文件加载区域
            if aws_config_config_path.exists():
                config = configparser.ConfigParser()
                config.read(aws_config_config_path)
                
                profile_section = f"profile {self.profile_name}" if self.profile_name != "default" else "default"
                if profile_section in config:
                    self.region = config[profile_section].get("region", "us-east-1")
                    print(f"✓ 从AWS配置文件加载区域: {self.region}")
            
            if not self.region:
                self.region = "us-east-1"  # 默认区域
                
        except Exception as e:
            print(f"⚠️  加载AWS配置时出错: {str(e)}")
    
    def setup_credentials(self):
        """设置AWS凭证到环境变量"""
        if not self.access_key or not self.secret_key:
            raise ValueError(
                "AWS凭证未配置。请确保:\n"
                "1. 运行 'aws configure' 配置AWS凭证，或\n"
                "2. 设置环境变量 AWS_ACCESS_KEY_ID 和 AWS_SECRET_ACCESS_KEY，或\n"
                "3. 在config.py中直接配置凭证"
            )
        
        # 设置环境变量
        os.environ["AWS_ACCESS_KEY_ID"] = self.access_key
        os.environ["AWS_SECRET_ACCESS_KEY"] = self.secret_key
        os.environ["AWS_DEFAULT_REGION"] = self.region
        
        print(f"✓ AWS凭证已设置到环境变量 (region: {self.region})")

@dataclass
class ServerConfig:
    """服务器配置"""
    host: str = "0.0.0.0"
    port: int = 5001
    debug: bool = False
    flask_service_url: str = "http://localhost:5006/upload_markdown"

@dataclass
class LogConfig:
    """日志配置"""
    level: str = os.environ.get("LOG_LEVEL", "INFO")
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: str = "agent.log"

@dataclass
class ExamConfig:
    """考试生成配置"""
    max_reference_length: int = 5000
    default_question_count: int = 5
    default_difficulty: str = "medium"
    system_prompt: str = """
    你是一个专业的考试生成助手，能够根据用户需求生成高质量的考试内容。

    ## 执行流程
    1. 分析用户请求，提取考试元数据（年级、科目、题型、题目数量、难度、主题等）
    2. 如果提供了参考资料，处理参考资料（如果是URL，获取内容；如果是文本，直接使用）
    3. 根据元数据和参考资料，生成符合要求的考试题目
    4. 验证生成的考试内容格式是否正确
    5. 如果格式不正确，修复格式问题

    ## 可用工具及用途
    - extract_exam_metadata: 从用户请求中提取考试元数据（年级、科目、题型等）
    - fetch_url_content: 获取URL内容，用于处理参考资料
    - process_reference: 处理参考资料，提取关键信息
    - plan_exam_content: 规划考试内容结构，处理复合题型的情况
    - generate_single_choice_question: 生成单选题，接受主题、难度和参考资料参数
    - generate_multiple_choice_question: 生成多选题，接受主题、难度和参考资料参数
    - generate_fill_blank_question: 生成填空题，接受主题、难度和参考资料参数
    - validate_exam_format: 验证生成的考试内容格式是否正确

    ## 工具使用指南
    - 使用extract_exam_metadata提取用户请求中的元数据
    - 如果有多种题型，必须首先使用plan_exam_content工具规划考试内容结构
      * 这一步很重要，它会确保合理分配每种题型的题目数量
      * 例如，如果用户要求生成5道题目，包括单选题和多选题，plan_exam_content会决定生成3道单选题和2道多选题
    - 如果有参考资料，使用fetch_url_content和process_reference处理
    - 根据plan_exam_content的规划结果，使用对应的生成工具：
      * 单选题：使用generate_single_choice_question
      * 多选题：使用generate_multiple_choice_question
      * 填空题：使用generate_fill_blank_question
    - 使用validate_exam_format验证生成的内容格式

    ## 复合题型处理流程
    1. 使用extract_exam_metadata提取元数据
    2. 使用plan_exam_content规划考试内容结构
    3. 按照规划结果，依次生成各种题型的题目
    4. 将所有题目组合成一个完整的考试
    5. 使用validate_exam_format验证最终内容

    ## 考试格式要求
    生成的考试需要符合markdown格式，包含正确答案标记：
    - 单选题的选项：- (x) 正确选项 或 - ( ) 错误选项
    - 多选题的选项：- [x] 正确选项 或 - [ ] 错误选项
    - 填空题：- R:= 正确答案

    ## 注意事项
    - 根据年级和科目调整题目难度和内容
    - 确保题目内容准确、清晰、无歧义
    - 不要包含任何额外的解释，直接输出考试内容
    - 确保生成的考试内容格式正确，可以被Markdown解析器正确解析
    - 如果参考资料内容过长，优先使用重要和相关的部分
    - 每个题目都应该使用二级标题（##）开头，不要添加额外的一级标题或编号
    - 不要在题目标题中添加编号，例如使用"## 单选题"而不是"## 单选题1"
    - 不要在考试开头添加总标题，直接从第一个题目开始
    """

# 创建配置实例
aws_config = AWSConfig()  # 先创建AWS配置
llm_config = LLMConfig()
# 如果AWS配置中有区域信息，使用它
if aws_config.region:
    llm_config.region_name = aws_config.region

server_config = ServerConfig()
log_config = LogConfig()
exam_config = ExamConfig()
