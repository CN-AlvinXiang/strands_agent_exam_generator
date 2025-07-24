import logging
import json
import time
from strands import Agent, tool
from strands.models import BedrockModel

# 启用Strands的调试日志
logging.getLogger("strands").setLevel(logging.DEBUG)
from .config import llm_config, exam_config
from .utils import handle_agent_error, create_task_tracking_callback, task_manager
from .tools import (
    process_reference,
    fetch_url_content,
    validate_exam_format,
    extract_exam_metadata,
    generate_single_choice_question,
    generate_multiple_choice_question,
    generate_fill_blank_question,
    send_to_flask_service,
    plan_exam_content
)

def create_agent(workflow_id=None, step_id=None, custom_tools=None, custom_prompt=None):
    """创建Agent实例
    
    Args:
        workflow_id: 工作流ID，用于任务跟踪
        step_id: 步骤ID，用于任务跟踪
        custom_tools: 自定义工具列表，如果提供则覆盖默认工具
        custom_prompt: 自定义系统提示词，如果提供则覆盖默认提示词
    
    Returns:
        Agent: 配置好的Agent实例
    """
    # 创建回调处理器（如果提供了工作流ID和步骤ID）
    callback = None
    if workflow_id and step_id:
        callback = create_task_tracking_callback(task_manager, workflow_id, step_id)
        logging.info(f"为工作流 {workflow_id} 步骤 {step_id} 创建回调处理器")
    
    # 确定使用的工具
    tools = custom_tools if custom_tools is not None else [
        fetch_url_content,
        process_reference,
        generate_single_choice_question,
        generate_multiple_choice_question,
        generate_fill_blank_question,
        validate_exam_format,
        extract_exam_metadata,
        plan_exam_content
    ]
    
    # 确定使用的系统提示词
    system_prompt = custom_prompt if custom_prompt is not None else exam_config.system_prompt
    
    try:
        # 创建 BedrockModel
        bedrock_model = BedrockModel(
            model_id=llm_config.model_id,
            region_name=llm_config.region_name,
            temperature=llm_config.temperature,
            max_tokens=llm_config.max_tokens
        )
        
        # 创建Agent
        agent = Agent(
            name="ExamGeneratorAgent",
            model=bedrock_model,  # 使用配置好的BedrockModel
            system_prompt=system_prompt,
            tools=tools,
            callback_handler=callback
        )
        
        return agent
    except Exception as e:
        logging.error(f"创建Agent失败: {str(e)}")
        raise Exception(f"创建Agent失败: {str(e)}")

def create_exam_generation_prompt(exam_request):
    """创建考试生成提示词模板
    
    Args:
        exam_request: 考试请求数据
        
    Returns:
        str: 格式化的提示词
    """
    return f"""
    请根据以下要求生成一份考试：
    
    {json.dumps(exam_request.get('inputs', {}), ensure_ascii=False, indent=2)}
    
    请按照系统提示中的指导使用提供的工具来生成考试内容。
    记住，使用generate_single_choice_question、generate_multiple_choice_question和generate_fill_blank_question工具来生成题目，而不是自己直接生成题目内容。
    如果有多种题型，请先使用plan_exam_content工具规划考试内容结构。
    """

def generate_exam(exam_request, workflow_id):
    """生成考试内容
    
    让Agent自主决定执行流程，根据系统提示词和工具描述来完成考试生成任务。
    
    Args:
        exam_request: 考试请求数据
        workflow_id: 工作流ID
    
    Returns:
        dict: 生成的考试内容和元数据
    """
    max_retries = 3
    initial_retry_delay = 5  # 初始重试延迟（秒）
    
    for attempt in range(max_retries):
        try:
            # 创建考试生成步骤
            step_id = task_manager.add_step(workflow_id, "生成考试")
            task_manager.start_step(workflow_id, step_id)
            
            # 创建Agent
            agent = create_agent(workflow_id, step_id)
            
            # 构建用户提示词
            prompt = create_exam_generation_prompt(exam_request)
            
            # 让Agent自主执行考试生成流程
            result = agent(prompt)  # 直接调用Agent实例，符合Strands Agent框架标准用法
            
            # 从结果中提取考试内容
            # 检查result.message的类型，如果是字典，则提取content字段
            if isinstance(result.message, dict) and "content" in result.message:
                exam_content = result.message["content"]
            elif isinstance(result.message, list) and len(result.message) > 0 and isinstance(result.message[0], dict) and "text" in result.message[0]:
                # 如果是列表，提取第一个元素的text字段
                exam_content = result.message[0]["text"]
            else:
                # 否则直接使用message
                exam_content = result.message
            
            # 发送到渲染服务
            render_result = send_to_flask_service(exam_content)
            
            # 完成步骤
            task_manager.complete_step(workflow_id, step_id, output_data={
                "exam_content": exam_content,
                "render_result": render_result
            })
            
            return {
                "exam_content": exam_content,
                "render_result": render_result
            }
        except Exception as e:
            # 检查是否是限流错误
            if "throttlingException" in str(e) or "Too many requests" in str(e):
                if attempt < max_retries - 1:
                    # 计算指数退避时间
                    retry_delay = initial_retry_delay * (2 ** attempt)
                    logging.warning(f"API限流，等待{retry_delay}秒后重试 ({attempt+1}/{max_retries}): {str(e)}")
                    time.sleep(retry_delay)
                    # 如果有step_id，标记为失败
                    if 'step_id' in locals() and step_id:
                        task_manager.fail_step(workflow_id, step_id, f"API限流，正在重试 ({attempt+1}/{max_retries})")
                else:
                    logging.error(f"生成考试失败，已达到最大重试次数: {str(e)}")
                    if 'step_id' in locals() and step_id:
                        task_manager.fail_step(workflow_id, step_id, str(e))
                    raise Exception(f"生成考试失败: {str(e)}")
            else:
                # 其他类型的错误
                logging.error(f"生成考试失败: {str(e)}")
                if 'step_id' in locals() and step_id:
                    task_manager.fail_step(workflow_id, step_id, str(e))
                raise Exception(f"生成考试失败: {str(e)}")
