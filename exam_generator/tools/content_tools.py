import re
import logging
from strands import tool
from ..config import exam_config

def standardize_question_format(question_type, content):
    """
    标准化题目格式
    
    Args:
        question_type: 题目类型（'singleChoice', 'multipleChoice', 'fillBlank'）
        content: 题目内容
        
    Returns:
        str: 标准化后的题目内容
    """
    content = content.strip()
    
    # 确保题目以正确的标题开始
    if question_type == 'singleChoice' and not content.startswith("## 单选题"):
        if content.lower().startswith("单选题") or "单选题" in content.lower().split("\n")[0]:
            content = "## 单选题\n\n" + "\n".join(content.split("\n")[1:])
        else:
            content = "## 单选题\n\n" + content
    
    elif question_type == 'multipleChoice' and not content.startswith("## 多选题"):
        if content.lower().startswith("多选题") or "多选题" in content.lower().split("\n")[0]:
            content = "## 多选题\n\n" + "\n".join(content.split("\n")[1:])
        else:
            content = "## 多选题\n\n" + content
    
    elif question_type == 'fillBlank' and not content.startswith("## 填空题"):
        if content.lower().startswith("填空题") or "填空题" in content.lower().split("\n")[0]:
            content = "## 填空题\n\n" + "\n".join(content.split("\n")[1:])
        else:
            content = "## 填空题\n\n" + content
    
    # 确保选项格式正确
    lines = content.split("\n")
    for i in range(len(lines)):
        # 单选题选项格式
        if question_type == 'singleChoice':
            if re.match(r'^\s*-\s*\(\s*x\s*\)', lines[i], re.IGNORECASE):
                lines[i] = re.sub(r'^\s*-\s*\(\s*x\s*\)', '- (x)', lines[i])
            elif re.match(r'^\s*-\s*\(\s*\)', lines[i], re.IGNORECASE):
                lines[i] = re.sub(r'^\s*-\s*\(\s*\)', '- ( )', lines[i])
        
        # 多选题选项格式
        elif question_type == 'multipleChoice':
            if re.match(r'^\s*-\s*\[\s*x\s*\]', lines[i], re.IGNORECASE):
                lines[i] = re.sub(r'^\s*-\s*\[\s*x\s*\]', '- [x]', lines[i])
            elif re.match(r'^\s*-\s*\[\s*\]', lines[i], re.IGNORECASE):
                lines[i] = re.sub(r'^\s*-\s*\[\s*\]', '- [ ]', lines[i])
        
        # 填空题答案格式
        elif question_type == 'fillBlank' and re.match(r'^\s*-\s*R\s*:=', lines[i], re.IGNORECASE):
            lines[i] = re.sub(r'^\s*-\s*R\s*:=', '- R:=', lines[i])
    
    return "\n".join(lines)

def fix_exam_format(markdown_content):
    """
    修复考试内容格式
    
    Args:
        markdown_content: Markdown格式的考试内容
        
    Returns:
        str: 修复后的考试内容
    """
    if not markdown_content:
        return markdown_content
    
    # 处理可能的一级标题
    lines = markdown_content.split('\n')
    if lines and lines[0].strip().startswith('# '):
        logging.info(f"移除一级标题: {lines[0]}")
        markdown_content = '\n'.join(lines[1:])
    
    # 分割成不同的题目
    sections = re.split(r'(?:^|\n)##\s+(?:单选题|多选题|填空题)(?:\d*)', markdown_content)
    headers = re.findall(r'(?:^|\n)(##\s+(?:单选题|多选题|填空题)(?:\d*))', markdown_content)
    
    # 跳过第一个元素（可能是空的）
    if sections and not sections[0].strip():
        sections = sections[1:]
    
    if not sections or not headers:
        # 如果没有找到题目，尝试按空行分割
        parts = markdown_content.split("\n\n")
        fixed_content = ""
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # 尝试判断题目类型
            if '- (x)' in part or '- ( )' in part:
                fixed_content += "\n\n## 单选题\n\n" + part
            elif '- [x]' in part or '- [ ]' in part:
                fixed_content += "\n\n## 多选题\n\n" + part
            elif '- R:=' in part:
                fixed_content += "\n\n## 填空题\n\n" + part
            else:
                # 无法判断题型，默认为单选题
                fixed_content += "\n\n## 单选题\n\n" + part
        
        return fixed_content.strip()
    
    # 重新组合题目，确保每个题目都有正确的标题
    fixed_content = ""
    for i in range(len(headers)):
        header = headers[i]
        content = sections[i] if i < len(sections) else ""
        
        # 确定题目类型
        question_type = None
        if '单选题' in header:
            question_type = 'singleChoice'
        elif '多选题' in header:
            question_type = 'multipleChoice'
        elif '填空题' in header:
            question_type = 'fillBlank'
        
        # 标准化题目格式
        if question_type:
            standardized_content = standardize_question_format(question_type, content)
            fixed_content += header + standardized_content + "\n\n"
        else:
            fixed_content += header + content + "\n\n"
    
    return fixed_content.strip()

@tool
def plan_exam_content(metadata: dict) -> dict:
    """
    规划考试内容结构。
    
    根据考试元数据（题型、题目数量等），规划考试内容的结构，包括：
    - 每种题型的题目数量
    - 题目的顺序
    - 题目的主题分配
    
    此工具用于处理复合题型的情况，确保生成的考试内容结构合理。
    
    Args:
        metadata: 考试元数据，包含题型、题目数量、难度等信息
        
    Returns:
        dict: 考试内容规划，包含每种题型的题目数量和主题分配
        
    示例:
        >>> plan_exam_content({"types": ["singleChoice", "multipleChoice"], "count": 5})
        {
            "plan": "生成3道单选题和2道多选题",
            "type_counts": {
                "singleChoice": 3,
                "multipleChoice": 2
            },
            "topics": ["主题1", "主题2", "主题3", "主题4", "主题5"]
        }
    """
    types = metadata.get('types', ['singleChoice'])
    count = metadata.get('count', 5)
    topics = metadata.get('topics', [])
    
    # 如果只有一种题型，直接返回
    if len(types) == 1:
        return {
            "plan": f"生成{count}道{_get_type_name(types[0])}",
            "type_counts": {types[0]: count},
            "topics": topics
        }
    
    # 如果有多种题型，需要分配题目数量
    questions_per_type = count // len(types)
    remainder = count % len(types)
    
    # 构建题型数量映射
    type_counts = {}
    for i, t in enumerate(types):
        type_counts[t] = questions_per_type + (1 if i < remainder else 0)
    
    # 构建规划描述
    plan_parts = []
    for t, c in type_counts.items():
        plan_parts.append(f"{c}道{_get_type_name(t)}")
    
    plan = "生成" + "和".join(plan_parts)
    
    return {
        "plan": plan,
        "type_counts": type_counts,
        "topics": topics
    }

def _get_type_name(type_code):
    """获取题型的中文名称"""
    type_names = {
        'singleChoice': '单选题',
        'multipleChoice': '多选题',
        'fillBlank': '填空题'
    }
    return type_names.get(type_code, type_code)

@tool
def validate_exam_format(markdown_content: str) -> bool:
    """
    验证考试内容格式是否正确。
    
    检查提供的Markdown内容是否符合考试格式要求，包括：
    1. 单选题格式：使用"- (x)"标记正确选项，"- ( )"标记错误选项
    2. 多选题格式：使用"- [x]"标记正确选项，"- [ ]"标记错误选项
    3. 填空题格式：使用"- R:="标记正确答案
    
    此工具会检查每种题型的格式，并验证是否存在格式错误，如：
    - 单选题有多个正确答案
    - 选项标记不一致
    - 缺少正确答案标记
    - Markdown语法错误
    
    Args:
        markdown_content: Markdown格式的考试内容
        
    Returns:
        bool: 如果格式完全正确返回True，否则返回False
        
    示例:
        >>> validate_exam_format("## 单选题\\n\\n问题\\n\\n- (x) 正确选项\\n- ( ) 错误选项")
        True
        >>> validate_exam_format("## 单选题\\n\\n问题\\n\\n- (x) 选项1\\n- (x) 选项2")
        False  # 单选题不应有多个正确答案
    """
    if not markdown_content:
        logging.warning("考试内容为空")
        return False
    
    # 处理可能的一级标题
    lines = markdown_content.split('\n')
    if lines and lines[0].strip().startswith('# '):
        logging.info(f"移除一级标题: {lines[0]}")
        markdown_content = '\n'.join(lines[1:])
    
    # 分割成不同的题目，支持多种标题格式
    questions = re.split(r'(?:^|\n)##\s+(?:单选题|多选题|填空题)(?:\d*)', markdown_content)
    
    # 跳过第一个元素（可能是空的）
    if questions and not questions[0].strip():
        questions = questions[1:]
    
    if not questions:
        logging.warning("未找到题目")
        return False
    
    # 提取题目类型
    types = re.findall(r'(?:^|\n)(##\s+(?:单选题|多选题|填空题)(?:\d*))', markdown_content)
    
    # 验证每个题目
    for i, question in enumerate(questions):
        question = question.strip()
        if not question:
            continue
        
        # 获取题目类型
        question_type = types[i] if i < len(types) else None
        
        # 根据题目类型或内容特征验证
        if question_type and '单选题' in question_type:
            if not _validate_single_choice(question):
                logging.warning(f"单选题格式错误: {question[:50]}...")
                return False
        elif question_type and '多选题' in question_type:
            if not _validate_multiple_choice(question):
                logging.warning(f"多选题格式错误: {question[:50]}...")
                return False
        elif question_type and '填空题' in question_type:
            if not _validate_fill_blank(question):
                logging.warning(f"填空题格式错误: {question[:50]}...")
                return False
        elif '- (x)' in question or '- ( )' in question:
            if not _validate_single_choice(question):
                logging.warning(f"单选题格式错误: {question[:50]}...")
                return False
        elif '- [x]' in question or '- [ ]' in question:
            if not _validate_multiple_choice(question):
                logging.warning(f"多选题格式错误: {question[:50]}...")
                return False
        elif '- R:=' in question:
            if not _validate_fill_blank(question):
                logging.warning(f"填空题格式错误: {question[:50]}...")
                return False
        else:
            # 如果无法确定题型，记录警告但不返回失败
            logging.warning(f"未知题型: {question[:50]}...")
            
    # 如果验证失败，尝试修复
    is_valid = True
    
    # 如果验证失败，尝试修复
    if not is_valid:
        logging.info("尝试修复考试内容格式")
        fixed_content = fix_exam_format(markdown_content)
        
        # 重新验证
        is_valid = validate_exam_format(fixed_content)
        if is_valid:
            # 将修复后的内容赋值给原始内容（通过引用传递）
            markdown_content = fixed_content
            logging.info("考试内容格式修复成功")
        else:
            logging.warning("考试内容格式修复失败")
            return False
    
    return True

def _validate_single_choice(question):
    """验证单选题格式"""
    # 检查选项格式
    options = re.findall(r'-\s*\((x| )\)', question)
    if not options:
        logging.warning("单选题未找到选项")
        return False
    
    # 检查是否有且仅有一个正确答案
    correct_count = sum(1 for opt in options if opt == 'x')
    if correct_count != 1:
        logging.warning(f"单选题正确答案数量错误: {correct_count}")
        return False
    
    return True

def _validate_multiple_choice(question):
    """验证多选题格式"""
    # 检查选项格式
    options = re.findall(r'-\s*\[(x| )\]', question)
    if not options:
        logging.warning("多选题未找到选项")
        return False
    
    # 检查是否至少有一个正确答案
    correct_count = sum(1 for opt in options if opt == 'x')
    if correct_count < 1:
        logging.warning("多选题没有正确答案")
        return False
    
    return True

def _validate_fill_blank(question):
    """验证填空题格式"""
    # 检查答案格式
    answers = re.findall(r'-\s*R:=', question)
    if not answers:
        logging.warning("填空题未找到答案")
        return False
    
    return True

@tool
def extract_exam_metadata(exam_request: dict) -> dict:
    """
    从请求中提取考试元数据。
    
    分析考试请求数据，提取并规范化所有相关的元数据，包括：
    - grade: 年级信息
    - subject: 科目信息
    - types: 题型列表（单选题、多选题、填空题等）
    - count: 题目数量
    - difficulty: 难度级别
    - topics: 主题列表
    - reference: 参考资料（如果有）
    - teacher_notes: 教师备注（如果有）
    
    此工具会处理各种输入格式，确保输出的元数据格式一致，并设置合理的默认值。
    
    Args:
        exam_request: 考试请求数据，通常是API请求的JSON对象
        
    Returns:
        dict: 提取和规范化后的元数据字典
        
    示例:
        >>> extract_exam_metadata({"inputs": {"grade": "5th", "subject": "Math", "count": 5}})
        {
            "grade": "5th",
            "subject": "Math",
            "types": ["singleChoice"],  # 默认题型
            "count": 5,
            "difficulty": "medium",  # 默认难度
            "topics": [],
            "reference": "",
            "teacher_notes": ""
        }
    """
    # 获取输入数据
    inputs = exam_request.get('inputs', {})
    
    # 提取并规范化元数据
    metadata = {
        "grade": inputs.get('grade', ''),
        "subject": inputs.get('subject', ''),
        "count": int(inputs.get('count', exam_config.default_question_count)),
        "difficulty": inputs.get('difficulty', exam_config.default_difficulty),
        "reference": inputs.get('reference', ''),
        "teacher_notes": inputs.get('teacher_notes', '')
    }
    
    # 处理题型
    types_str = inputs.get('types', 'singleChoice')
    if isinstance(types_str, str):
        types_list = [t.strip() for t in types_str.split(',')]
    elif isinstance(types_str, list):
        types_list = types_str
    else:
        types_list = ['singleChoice']
    
    # 规范化题型名称
    type_mapping = {
        'singlechoice': 'singleChoice',
        'single': 'singleChoice',
        'single_choice': 'singleChoice',
        'multiplechoice': 'multipleChoice',
        'multiple': 'multipleChoice',
        'multiple_choice': 'multipleChoice',
        'fillblank': 'fillBlank',
        'fill': 'fillBlank',
        'fill_blank': 'fillBlank'
    }
    
    normalized_types = []
    for t in types_list:
        t_lower = t.lower()
        if t_lower in type_mapping:
            normalized_types.append(type_mapping[t_lower])
        else:
            normalized_types.append(t)
    
    metadata['types'] = normalized_types
    
    # 处理主题
    topics = inputs.get('topics', '')
    if isinstance(topics, str):
        topics_list = [t.strip() for t in topics.split(',') if t.strip()]
    elif isinstance(topics, list):
        topics_list = topics
    else:
        topics_list = []
    
    metadata['topics'] = topics_list
    
    return metadata
