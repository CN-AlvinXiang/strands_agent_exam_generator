import logging
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
from .config import server_config, aws_config
from .utils import setup_logging, task_manager, handle_error, TaskStatus
from .agent import generate_exam

# 初始化Flask应用
app = Flask(__name__)
# 启用CORS
CORS(app)

# 初始化日志系统
setup_logging()
logger = logging.getLogger(__name__)

@app.route('/workflows/run', methods=['POST'])
def run_workflow():
    """处理考试生成请求"""
    try:
        # 获取请求数据
        exam_request = request.json
        logger.info(f"收到考试生成请求: {json.dumps(exam_request, ensure_ascii=False)}")
        
        # 验证请求参数
        if not exam_request or not isinstance(exam_request, dict):
            return handle_error(ValueError("无效的请求格式"))
        
        # 创建工作流记录
        workflow_id = task_manager.start_workflow("考试生成", input_data=exam_request)
        logger.info(f"创建工作流: {workflow_id}")
        
        # 设置AWS凭证
        aws_config.setup_credentials()
        
        # 生成考试内容
        result = generate_exam(exam_request, workflow_id)
        
        # 从渲染结果中获取URL
        render_result = result.get("render_result", {})
        message = render_result.get("message", "")
        
        # 完成工作流之前，检查是否有未完成的工具调用
        for step in task_manager.tasks[workflow_id]["steps"]:
            for tool_call in step["tool_calls"]:
                if tool_call["status"] == TaskStatus.RUNNING:
                    # 自动标记为完成
                    task_manager.complete_tool_call(
                        workflow_id=workflow_id,
                        step_id=step["id"],
                        tool_call_id=tool_call["id"],
                        output_data="自动标记为完成"
                    )
                    logger.info(f"自动标记最后的工具调用完成: {tool_call['tool_name']}")
        
        # 完成工作流
        task_manager.complete_workflow(workflow_id, output_data=result)
        
        # 构建响应
        response = {
            "event": "workflow_finished",
            "data": {
                "outputs": {
                    "body": json.dumps({"message": message})
                }
            }
        }
        
        logger.info(f"考试生成完成: {workflow_id}")
        return jsonify(response)
    except Exception as e:
        logger.error(f"考试生成失败: {str(e)}", exc_info=True)
        return handle_error(e, workflow_id, task_manager=task_manager)

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({"status": "ok"})

@app.route('/evaluation/report', methods=['GET'])
def get_evaluation_report():
    """获取评估报告"""
    try:
        workflow_id = request.args.get('workflow_id')
        report = task_manager.generate_evaluation_report(workflow_id)
        return jsonify({"status": "success", "report": report})
    except Exception as e:
        logger.error(f"获取评估报告失败: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

def run_server():
    """启动服务器"""
    logger.info(f"启动服务器: {server_config.host}:{server_config.port}")
    app.run(
        host=server_config.host,
        port=server_config.port,
        debug=server_config.debug
    )

if __name__ == '__main__':
    run_server()
