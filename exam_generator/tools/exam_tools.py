import logging
import boto3
import json
import time
import concurrent.futures
import os
import pickle
import hashlib
import re
from datetime import datetime, timedelta
from strands import tool
from ..config import llm_config, aws_config
from .content_tools import standardize_question_format

def get_bedrock_client():
    """获取Bedrock客户端"""
    return boto3.client(
        service_name='bedrock-runtime',
        region_name=llm_config.region_name,
        aws_access_key_id=aws_config.access_key,
        aws_secret_access_key=aws_config.secret_key
    )

def call_claude(prompt, max_tokens=1000, temperature=0.7, max_retries=3, initial_retry_delay=2):
    """
    调用Claude模型生成内容，带有指数退避重试策略
    
    Args:
        prompt: 提示词
        max_tokens: 最大生成token数
        temperature: 温度参数，控制随机性
        max_retries: 最大重试次数
        initial_retry_delay: 初始重试延迟（秒）
        
    Returns:
        str: 生成的内容
    """
    client = get_bedrock_client()
    
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    # 添加指数退避重试逻辑
    for attempt in range(max_retries):
        try:
            response = client.invoke_model(
                modelId=llm_config.model_id,
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read().decode('utf-8'))
            return response_body['content'][0]['text']
        except Exception as e:
            # 检查是否是限流错误
            if "throttlingException" in str(e) or "Too many requests" in str(e):
                if attempt < max_retries - 1:
                    # 计算指数退避时间
                    retry_delay = initial_retry_delay * (2 ** attempt)
                    logging.warning(f"API限流，等待{retry_delay}秒后重试 ({attempt+1}/{max_retries}): {str(e)}")
                    time.sleep(retry_delay)
                else:
                    logging.error(f"API限流，已达到最大重试次数: {str(e)}")
                    raise
            else:
                # 其他类型的错误
                if attempt < max_retries - 1:
                    logging.warning(f"调用Claude失败，尝试重试 ({attempt+1}/{max_retries}): {str(e)}")
                    time.sleep(initial_retry_delay)
                else:
                    logging.error(f"调用Claude失败，已达到最大重试次数: {str(e)}")
                    raise

class QuestionCache:
    """题目缓存类"""
    
    def __init__(self, cache_dir="./cache", ttl_days=30):
        """
        初始化缓存
        
        Args:
            cache_dir: 缓存目录
            ttl_days: 缓存有效期（天）
        """
        self.cache_dir = cache_dir
        self.ttl = timedelta(days=ttl_days)
        
        # 确保缓存目录存在
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_key(self, topic, difficulty, question_type, reference=None):
        """生成缓存键"""
        # 构建用于哈希的字符串
        hash_str = f"{topic}|{difficulty}|{question_type}"
        if reference:
            # 如果参考资料太长，只使用前500个字符
            hash_str += f"|{reference[:500]}"
        
        # 生成MD5哈希
        return hashlib.md5(hash_str.encode()).hexdigest()
    
    def get(self, topic, difficulty, question_type, reference=None):
        """
        获取缓存的题目
        
        Args:
            topic: 题目主题
            difficulty: 难度级别
            question_type: 题目类型
            reference: 参考资料
            
        Returns:
            str: 缓存的题目，如果没有缓存或缓存过期则返回None
        """
        key = self._get_cache_key(topic, difficulty, question_type, reference)
        cache_file = os.path.join(self.cache_dir, f"{key}.pkl")
        
        if not os.path.exists(cache_file):
            return None
        
        try:
            with open(cache_file, "rb") as f:
                cache_data = pickle.load(f)
            
            # 检查缓存是否过期
            if datetime.now() - cache_data["timestamp"] > self.ttl:
                return None
            
            return cache_data["question"]
        except Exception as e:
            logging.warning(f"读取缓存失败: {str(e)}")
            return None
    
    def set(self, topic, difficulty, question_type, question, reference=None):
        """
        设置缓存
        
        Args:
            topic: 题目主题
            difficulty: 难度级别
            question_type: 题目类型
            question: 题目内容
            reference: 参考资料
        """
        key = self._get_cache_key(topic, difficulty, question_type, reference)
        cache_file = os.path.join(self.cache_dir, f"{key}.pkl")
        
        cache_data = {
            "timestamp": datetime.now(),
            "question": question
        }
        
        try:
            with open(cache_file, "wb") as f:
                pickle.dump(cache_data, f)
        except Exception as e:
            logging.warning(f"写入缓存失败: {str(e)}")

# 创建全局缓存实例
question_cache = QuestionCache()

def generate_questions_parallel(question_specs):
    """
    并行生成多个题目
    
    Args:
        question_specs: 题目规格列表，每个元素是一个字典，包含type, topic, difficulty等
        
    Returns:
        list: 生成的题目列表
    """
    results = []
    
    # 限制并发数量为3，避免API限流
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        # 创建Future对象
        future_to_spec = {}
        for spec in question_specs:
            if spec['type'] == 'singleChoice':
                future = executor.submit(
                    generate_single_choice_question, 
                    spec['topic'], 
                    spec['difficulty'], 
                    spec.get('reference')
                )
            elif spec['type'] == 'multipleChoice':
                future = executor.submit(
                    generate_multiple_choice_question, 
                    spec['topic'], 
                    spec['difficulty'], 
                    spec.get('reference')
                )
            elif spec['type'] == 'fillBlank':
                future = executor.submit(
                    generate_fill_blank_question, 
                    spec['topic'], 
                    spec['difficulty'], 
                    spec.get('reference')
                )
            future_to_spec[future] = spec
        
        # 获取结果
        for future in concurrent.futures.as_completed(future_to_spec):
            spec = future_to_spec[future]
            try:
                question = future.result()
                results.append(question)
            except Exception as e:
                logging.error(f"生成题目失败: {str(e)}")
                # 使用备用题目
                if spec['type'] == 'singleChoice':
                    results.append(f"## 单选题\n\n关于{spec['topic']}的问题，难度为{spec['difficulty']}。\n\n- (x) 正确选项\n- ( ) 错误选项1\n- ( ) 错误选项2\n- ( ) 错误选项3")
                elif spec['type'] == 'multipleChoice':
                    results.append(f"## 多选题\n\n关于{spec['topic']}的问题，难度为{spec['difficulty']}。\n\n- [x] 正确选项1\n- [ ] 错误选项1\n- [x] 正确选项2\n- [ ] 错误选项2")
                elif spec['type'] == 'fillBlank':
                    results.append(f"## 填空题\n\n关于{spec['topic']}的问题，难度为{spec['difficulty']}。______\n\n- R:= 正确答案")
    
    return results

@tool
def generate_single_choice_question(topic: str, difficulty: str, reference: str = None) -> str:
    """
    生成单选题。
    
    根据指定的主题、难度和参考资料（如果提供），生成一道高质量的单选题。
    单选题将包含一个问题和4-5个选项，其中只有一个选项是正确的。
    
    难度级别会影响问题的复杂性和选项的设计：
    - easy: 基础概念，直接从参考资料中提取，选项区分度高
    - medium: 需要理解和应用概念，选项更具迷惑性
    - hard: 需要分析和评估，可能涉及多个概念的综合，选项非常接近
    
    Args:
        topic: 题目主题，指定问题应该关注的具体领域或概念
        difficulty: 难度级别，可选值为"easy"、"medium"或"hard"
        reference: 参考资料（可选），用于提供问题内容的背景信息
        
    Returns:
        生成的单选题Markdown文本，格式如下：
        
        ## 单选题
        
        问题描述
        
        - (x) 正确选项
        - ( ) 错误选项1
        - ( ) 错误选项2
        - ( ) 错误选项3
    """
    logging.info(f"生成单选题，主题: {topic}, 难度: {difficulty}")
    
    # 尝试从缓存获取
    cached_question = question_cache.get(topic, difficulty, "singleChoice", reference)
    if cached_question:
        logging.info("使用缓存的单选题")
        return cached_question
    
    # 构建提示词
    prompt = f"""
    请生成一道关于"{topic}"的单选题，难度级别为"{difficulty}"。
    
    题目要求：
    1. 题目应该清晰、准确，没有歧义
    2. 提供4个选项，其中只有1个正确答案
    3. 选项应该合理，不要有明显错误或不相关的选项
    4. 难度应该符合"{difficulty}"级别
    
    请严格使用以下格式：
    
    ## 单选题
    
    [题目描述]
    
    - (x) [正确选项]
    - ( ) [错误选项1]
    - ( ) [错误选项2]
    - ( ) [错误选项3]
    
    不要添加任何额外的标题、编号或解释。不要添加"单选题1"这样的编号，就是"## 单选题"。
    """
    
    if reference:
        prompt += f"\n\n参考以下资料生成题目：\n{reference}"
    
    try:
        # 调用Claude生成内容
        question = call_claude(
            prompt, 
            max_tokens=llm_config.max_tokens, 
            temperature=llm_config.temperature
        )
        
        # 标准化格式
        question = standardize_question_format('singleChoice', question)
        
        # 缓存结果
        question_cache.set(topic, difficulty, "singleChoice", question, reference)
        
        return question
    except Exception as e:
        logging.error(f"生成单选题失败: {str(e)}")
        # 返回一个基本的示例题目
        return f"""## 单选题

关于{topic}的问题，难度为{difficulty}。

- (x) 正确选项
- ( ) 错误选项1
- ( ) 错误选项2
- ( ) 错误选项3
"""

@tool
def generate_multiple_choice_question(topic: str, difficulty: str, reference: str = None) -> str:
    """
    生成多选题。
    
    根据指定的主题、难度和参考资料（如果提供），生成一道高质量的多选题。
    多选题将包含一个问题和4-6个选项，其中2-4个选项是正确的。
    
    难度级别会影响问题的复杂性和正确选项的数量：
    - easy: 基础概念，2个正确答案，选项区分度高
    - medium: 需要理解和应用概念，2-3个正确答案，选项更具迷惑性
    - hard: 需要分析和评估，3-4个正确答案，选项非常接近
    
    Args:
        topic: 题目主题，指定问题应该关注的具体领域或概念
        difficulty: 难度级别，可选值为"easy"、"medium"或"hard"
        reference: 参考资料（可选），用于提供问题内容的背景信息
        
    Returns:
        生成的多选题Markdown文本，格式如下：
        
        ## 多选题
        
        问题描述
        
        - [x] 正确选项1
        - [ ] 错误选项1
        - [x] 正确选项2
        - [ ] 错误选项2
    """
    logging.info(f"生成多选题，主题: {topic}, 难度: {difficulty}")
    
    # 尝试从缓存获取
    cached_question = question_cache.get(topic, difficulty, "multipleChoice", reference)
    if cached_question:
        logging.info("使用缓存的多选题")
        return cached_question
    
    # 构建提示词
    prompt = f"""
    请生成一道关于"{topic}"的多选题，难度级别为"{difficulty}"。
    
    题目要求：
    1. 题目应该清晰、准确，没有歧义
    2. 提供4-6个选项，其中2-4个是正确答案
    3. 选项应该合理，不要有明显错误或不相关的选项
    4. 难度应该符合"{difficulty}"级别
    
    请严格使用以下格式：
    
    ## 多选题
    
    [题目描述]
    
    - [x] [正确选项1]
    - [ ] [错误选项1]
    - [x] [正确选项2]
    - [ ] [错误选项2]
    
    不要添加任何额外的标题、编号或解释。不要添加"多选题1"这样的编号，就是"## 多选题"。
    """
    
    if reference:
        prompt += f"\n\n参考以下资料生成题目：\n{reference}"
    
    try:
        # 调用Claude生成内容
        question = call_claude(
            prompt, 
            max_tokens=llm_config.max_tokens, 
            temperature=llm_config.temperature
        )
        
        # 标准化格式
        question = standardize_question_format('multipleChoice', question)
        
        # 缓存结果
        question_cache.set(topic, difficulty, "multipleChoice", question, reference)
        
        return question
    except Exception as e:
        logging.error(f"生成多选题失败: {str(e)}")
        # 返回一个基本的示例题目
        return f"""## 多选题

关于{topic}的问题，难度为{difficulty}。

- [x] 正确选项1
- [ ] 错误选项1
- [x] 正确选项2
- [ ] 错误选项2
"""

@tool
def generate_fill_blank_question(topic: str, difficulty: str, reference: str = None) -> str:
    """
    生成填空题。
    
    根据指定的主题、难度和参考资料（如果提供），生成一道高质量的填空题。
    填空题将包含一个或多个需要填写的空白处，并提供正确答案。
    
    难度级别会影响问题的复杂性和空白数量：
    - easy: 基础概念，单个空白，答案明确
    - medium: 需要理解和应用概念，1-2个空白，答案可能需要推导
    - hard: 需要分析和评估，多个空白，答案需要综合多个概念
    
    Args:
        topic: 题目主题，指定问题应该关注的具体领域或概念
        difficulty: 难度级别，可选值为"easy"、"medium"或"hard"
        reference: 参考资料（可选），用于提供问题内容的背景信息
        
    Returns:
        生成的填空题Markdown文本，格式如下：
        
        ## 填空题
        
        问题描述，包含______需要填写的部分。
        
        - R:= 正确答案
    """
    logging.info(f"生成填空题，主题: {topic}, 难度: {difficulty}")
    
    # 尝试从缓存获取
    cached_question = question_cache.get(topic, difficulty, "fillBlank", reference)
    if cached_question:
        logging.info("使用缓存的填空题")
        return cached_question
    
    # 构建提示词
    prompt = f"""
    请生成一道关于"{topic}"的填空题，难度级别为"{difficulty}"。
    
    题目要求：
    1. 题目应该清晰、准确，没有歧义
    2. 使用下划线（______）表示需要填写的空白处
    3. 提供正确答案
    4. 难度应该符合"{difficulty}"级别
    
    请严格使用以下格式：
    
    ## 填空题
    
    [题目描述，包含______需要填写的部分]
    
    - R:= [正确答案]
    
    不要添加任何额外的标题、编号或解释。不要添加"填空题1"这样的编号，就是"## 填空题"。
    """
    
    if reference:
        prompt += f"\n\n参考以下资料生成题目：\n{reference}"
    
    try:
        # 调用Claude生成内容
        question = call_claude(
            prompt, 
            max_tokens=llm_config.max_tokens, 
            temperature=llm_config.temperature
        )
        
        # 标准化格式
        question = standardize_question_format('fillBlank', question)
        
        # 缓存结果
        question_cache.set(topic, difficulty, "fillBlank", question, reference)
        
        return question
    except Exception as e:
        logging.error(f"生成填空题失败: {str(e)}")
        # 返回一个基本的示例题目
        return f"""## 填空题

关于{topic}的问题，难度为{difficulty}。______

- R:= 正确答案
"""
