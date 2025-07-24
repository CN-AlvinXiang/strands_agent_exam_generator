import logging
from flask import jsonify

def handle_error(error, workflow_id=None, step_id=None, task_manager=None):
    """处理错误并返回适当的响应
    
    Args:
        error: 错误对象
        workflow_id: 工作流ID（可选）
        step_id: 步骤ID（可选）
        task_manager: 任务管理器实例（可选）
        
    Returns:
        tuple: (响应对象, 状态码)
    """
    # 记录错误日志
    logging.error(f"错误: {str(error)}")
    
    # 如果有工作流ID和任务管理器，标记工作流失败
    if workflow_id and task_manager:
        if step_id:
            task_manager.fail_step(workflow_id, step_id, str(error))
        task_manager.fail_workflow(workflow_id, str(error))
    
    # 构建错误响应
    response = {
        "event": "workflow_finished",
        "data": {
            "outputs": {
                "body": {"error": str(error)}
            }
        }
    }
    
    return jsonify(response), 500

def handle_agent_error(error):
    """处理Agent错误
    
    Args:
        error: 错误对象
    
    Returns:
        str: 用户友好的错误消息
    """
    error_str = str(error)
    
    if "AccessDeniedException" in error_str:
        return "模型访问被拒绝，请检查AWS凭证和模型访问权限"
    elif "ValidationException" in error_str:
        return "模型请求验证失败，请检查请求参数"
    elif "ThrottlingException" in error_str:
        return "模型请求被限流，请稍后重试"
    elif "ServiceUnavailableException" in error_str:
        return "模型服务不可用，请稍后重试"
    elif "timeout" in error_str.lower():
        return "模型请求超时，请稍后重试"
    else:
        return f"Agent执行失败: {error_str}"
