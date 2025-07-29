import logging
import json
from datetime import datetime
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
    workflow_id = None
    try:
        # 获取请求数据
        logger.info("开始处理考试生成请求")
        exam_request = request.json
        logger.info(f"收到考试生成请求: {json.dumps(exam_request, ensure_ascii=False)}")
        
        # 验证请求参数
        if not exam_request or not isinstance(exam_request, dict):
            logger.error("请求格式无效")
            return handle_error(ValueError("无效的请求格式"))
        
        # 验证必要的输入参数
        inputs = exam_request.get('inputs', {})
        if not inputs:
            logger.error("缺少inputs参数")
            return handle_error(ValueError("缺少inputs参数"))
        
        logger.info(f"解析的输入参数: {json.dumps(inputs, ensure_ascii=False)}")
        
        # 创建工作流记录
        workflow_id = task_manager.start_workflow("考试生成", input_data=exam_request)
        logger.info(f"创建工作流: {workflow_id}")
        
        # 设置AWS凭证
        logger.info("设置AWS凭证")
        try:
            aws_config.setup_credentials()
            logger.info("AWS凭证设置成功")
        except Exception as aws_error:
            logger.error(f"AWS凭证设置失败: {str(aws_error)}")
            raise aws_error
        
        # 生成考试内容
        logger.info("开始生成考试内容")
        result = generate_exam(exam_request, workflow_id)
        logger.info(f"考试生成结果: {json.dumps(result, ensure_ascii=False, default=str)}")
        
        # 从渲染结果中获取URL
        render_result = result.get("render_result", {})
        message = render_result.get("message", "")
        logger.info(f"渲染结果消息: {message}")
        
        # 完成工作流之前，检查是否有未完成的工具调用
        if workflow_id in task_manager.tasks:
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
        
        logger.info(f"考试生成完成: {workflow_id}, 响应: {json.dumps(response, ensure_ascii=False)}")
        return jsonify(response)
    except Exception as e:
        logger.error(f"考试生成失败: {str(e)}", exc_info=True)
        logger.error(f"错误类型: {type(e).__name__}")
        logger.error(f"错误详情: {str(e)}")
        if workflow_id:
            try:
                task_manager.fail_workflow(workflow_id, error_message=str(e))
            except Exception as task_error:
                logger.error(f"标记工作流失败时出错: {str(task_error)}")
        return handle_error(e, workflow_id, task_manager=task_manager)

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    try:
        # 检查基本配置
        health_info = {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "server_config": {
                "host": server_config.host,
                "port": server_config.port,
                "debug": server_config.debug
            },
            "aws_config": {
                "region": llm_config.region_name,
                "model_id": llm_config.model_id
            }
        }
        logger.info(f"健康检查通过: {health_info}")
        return jsonify(health_info)
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

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
