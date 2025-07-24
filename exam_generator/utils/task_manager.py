import uuid
import logging
from datetime import datetime
import json

class TaskStatus:
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskManager:
    """任务管理器"""
    def __init__(self):
        self.tasks = {}  # workflow_id -> workflow_data
        self.current_workflow_id = None
    
    def start_workflow(self, name, description=None, input_data=None):
        """开始一个新的工作流"""
        workflow_id = str(uuid.uuid4())
        self.tasks[workflow_id] = {
            "id": workflow_id,
            "name": name,
            "description": description,
            "input_data": input_data,
            "status": TaskStatus.RUNNING,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "steps": []
        }
        self.current_workflow_id = workflow_id
        return workflow_id
    
    def complete_workflow(self, workflow_id, output_data=None):
        """完成工作流"""
        if workflow_id in self.tasks:
            self.tasks[workflow_id]["status"] = TaskStatus.COMPLETED
            self.tasks[workflow_id]["end_time"] = datetime.now().isoformat()
            self.tasks[workflow_id]["output_data"] = output_data
    
    def fail_workflow(self, workflow_id, error):
        """标记工作流失败"""
        if workflow_id in self.tasks:
            self.tasks[workflow_id]["status"] = TaskStatus.FAILED
            self.tasks[workflow_id]["end_time"] = datetime.now().isoformat()
            self.tasks[workflow_id]["error"] = str(error)
    
    def add_step(self, workflow_id, name, description=None):
        """添加工作流步骤"""
        if workflow_id in self.tasks:
            step_id = str(uuid.uuid4())
            step = {
                "id": step_id,
                "name": name,
                "description": description,
                "status": TaskStatus.PENDING,
                "tool_calls": []
            }
            self.tasks[workflow_id]["steps"].append(step)
            return step_id
        return None
    
    def start_step(self, workflow_id, step_id, input_data=None):
        """开始执行步骤"""
        if workflow_id in self.tasks:
            for step in self.tasks[workflow_id]["steps"]:
                if step["id"] == step_id:
                    step["status"] = TaskStatus.RUNNING
                    step["start_time"] = datetime.now().isoformat()
                    step["input_data"] = input_data
                    break
    
    def complete_step(self, workflow_id, step_id, output_data=None):
        """完成步骤"""
        if workflow_id in self.tasks:
            for step in self.tasks[workflow_id]["steps"]:
                if step["id"] == step_id:
                    step["status"] = TaskStatus.COMPLETED
                    step["end_time"] = datetime.now().isoformat()
                    step["output_data"] = output_data
                    break
    
    def fail_step(self, workflow_id, step_id, error):
        """标记步骤失败"""
        if workflow_id in self.tasks:
            for step in self.tasks[workflow_id]["steps"]:
                if step["id"] == step_id:
                    step["status"] = TaskStatus.FAILED
                    step["end_time"] = datetime.now().isoformat()
                    step["error"] = str(error)
                    break
    
    def record_tool_call(self, workflow_id, step_id, tool_name, input_data=None):
        """记录工具调用"""
        if workflow_id in self.tasks:
            for step in self.tasks[workflow_id]["steps"]:
                if step["id"] == step_id:
                    tool_call_id = str(uuid.uuid4())
                    tool_call = {
                        "id": tool_call_id,
                        "tool_name": tool_name,
                        "input_data": input_data,
                        "status": TaskStatus.RUNNING,
                        "start_time": datetime.now().isoformat()
                    }
                    step["tool_calls"].append(tool_call)
                    return tool_call_id
        return None
    
    def complete_tool_call(self, workflow_id, step_id, tool_call_id, output_data=None):
        """完成工具调用"""
        if workflow_id in self.tasks:
            for step in self.tasks[workflow_id]["steps"]:
                if step["id"] == step_id:
                    for tool_call in step["tool_calls"]:
                        if tool_call["id"] == tool_call_id:
                            tool_call["status"] = TaskStatus.COMPLETED
                            tool_call["end_time"] = datetime.now().isoformat()
                            tool_call["output_data"] = output_data
                            break
    
    def fail_tool_call(self, workflow_id, step_id, tool_call_id, error):
        """标记工具调用失败"""
        if workflow_id in self.tasks:
            for step in self.tasks[workflow_id]["steps"]:
                if step["id"] == step_id:
                    for tool_call in step["tool_calls"]:
                        if tool_call["id"] == tool_call_id:
                            tool_call["status"] = TaskStatus.FAILED
                            tool_call["end_time"] = datetime.now().isoformat()
                            tool_call["error"] = str(error)
                            break
    
    def get_workflow(self, workflow_id):
        """获取工作流数据"""
        return self.tasks.get(workflow_id)
    
    def get_workflows(self):
        """获取所有工作流数据"""
        return self.tasks
    
    def get_interrupted_workflows(self):
        """获取中断的工作流"""
        interrupted = []
        for wf_id, workflow in self.tasks.items():
            if workflow["status"] == TaskStatus.RUNNING:
                interrupted.append(workflow)
        return interrupted
    
    def _generate_workflow_report(self, workflow_id):
        """生成单个工作流的评估报告"""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return {"error": f"Workflow {workflow_id} not found"}
        
        # 收集工具调用数据
        tool_calls = []
        for step in workflow["steps"]:
            tool_calls.extend(step.get("tool_calls", []))
        
        # 计算工具调用统计
        total_tool_calls = len(tool_calls)
        successful_tool_calls = sum(1 for tc in tool_calls if tc.get("status") == TaskStatus.COMPLETED)
        failed_tool_calls = sum(1 for tc in tool_calls if tc.get("status") == TaskStatus.FAILED)
        
        # 计算工具调用分布
        tool_distribution = {}
        for tc in tool_calls:
            tool_name = tc["tool_name"]
            if tool_name not in tool_distribution:
                tool_distribution[tool_name] = {
                    "total": 0,
                    "successful": 0,
                    "failed": 0,
                    "execution_times": []  # 添加执行时间列表
                }
            tool_distribution[tool_name]["total"] += 1
            if tc.get("status") == TaskStatus.COMPLETED:
                tool_distribution[tool_name]["successful"] += 1
            elif tc.get("status") == TaskStatus.FAILED:
                tool_distribution[tool_name]["failed"] += 1
            
            # 计算并记录执行时间
            if tc.get("start_time") and tc.get("end_time"):
                start = datetime.fromisoformat(tc["start_time"])
                end = datetime.fromisoformat(tc["end_time"])
                execution_time = (end - start).total_seconds()
                tool_distribution[tool_name]["execution_times"].append(execution_time)
        
        # 计算每种工具的平均执行时间
        for tool_name, stats in tool_distribution.items():
            execution_times = stats.pop("execution_times", [])  # 移除执行时间列表
            avg_time = sum(execution_times) / len(execution_times) if execution_times else 0
            stats["average_execution_time"] = avg_time  # 添加平均执行时间
        
        # 计算步骤统计
        total_steps = len(workflow["steps"])
        completed_steps = sum(1 for s in workflow["steps"] if s.get("status") == TaskStatus.COMPLETED)
        failed_steps = sum(1 for s in workflow["steps"] if s.get("status") == TaskStatus.FAILED)
        
        # 计算性能指标
        tool_execution_times = []
        for tc in tool_calls:
            if tc.get("start_time") and tc.get("end_time"):
                start = datetime.fromisoformat(tc["start_time"])
                end = datetime.fromisoformat(tc["end_time"])
                tool_execution_times.append((end - start).total_seconds())
        
        avg_tool_time = sum(tool_execution_times) / len(tool_execution_times) if tool_execution_times else 0
        
        # 生成报告
        report = {
            "workflow_id": workflow_id,
            "workflow_name": workflow["name"],
            "status": workflow["status"],
            "execution_time": None,
            "tool_call_statistics": {
                "total": total_tool_calls,
                "successful": successful_tool_calls,
                "failed": failed_tool_calls,
                "success_rate": successful_tool_calls / total_tool_calls if total_tool_calls > 0 else 0
            },
            "tool_distribution": tool_distribution,
            "step_statistics": {
                "total": total_steps,
                "completed": completed_steps,
                "failed": failed_steps,
                "completion_rate": completed_steps / total_steps if total_steps > 0 else 0
            },
            "performance_metrics": {
                "average_tool_execution_time": avg_tool_time
            }
        }
        
        # 计算总执行时间
        if workflow.get("start_time") and workflow.get("end_time"):
            start = datetime.fromisoformat(workflow["start_time"])
            end = datetime.fromisoformat(workflow["end_time"])
            report["execution_time"] = (end - start).total_seconds()
        
        return report
    
    def generate_evaluation_report(self, workflow_id=None):
        """生成评估报告"""
        if workflow_id:
            return self._generate_workflow_report(workflow_id)
        else:
            reports = []
            for wf_id in self.tasks:
                reports.append(self._generate_workflow_report(wf_id))
            return reports

# 创建全局任务管理器实例
task_manager = TaskManager()

def create_task_tracking_callback(task_manager, workflow_id, step_id):
    """创建用于任务跟踪的回调函数"""
    
    tool_call_map = {}  # 工具调用ID到工具调用记录ID的映射
    
    def callback_handler(**kwargs):
        # 获取上一个工具调用ID
        last_tool_id = getattr(callback_handler, 'last_tool_id', None)
        # 添加调试日志，查看实际接收到的事件格式
        logging.debug(f"回调接收到事件: {kwargs.keys()}")
        
        if "data" in kwargs:
            # 记录模型生成的文本
            logging.debug(f"模型生成: {kwargs['data']}")
            
        elif "current_tool_use" in kwargs:
            tool_use = kwargs["current_tool_use"]
            tool_id = tool_use.get("toolUseId")
            tool_name = tool_use.get("name")
            tool_status = tool_use.get("status")
            
            logging.info(f"工具调用: {tool_name}, 状态: {tool_status}, ID: {tool_id}")
            
            # 如果状态为None，但有工具名称和ID，则视为工具调用开始
            if tool_status is None and tool_name and tool_id:
                # 如果有上一个工具调用，并且与当前不同，则自动完成上一个
                if last_tool_id and last_tool_id != tool_id and last_tool_id in tool_call_map:
                    prev_tool_call_id = tool_call_map[last_tool_id]
                    # 检查工具调用是否已经完成
                    is_completed = False
                    for step in task_manager.tasks[workflow_id]["steps"]:
                        for tool_call in step["tool_calls"]:
                            if tool_call["id"] == prev_tool_call_id and tool_call["status"] != TaskStatus.RUNNING:
                                is_completed = True
                                break
                        if is_completed:
                            break
                    
                    if not is_completed:
                        # 自动标记为完成
                        task_manager.complete_tool_call(
                            workflow_id=workflow_id,
                            step_id=step_id,
                            tool_call_id=prev_tool_call_id,
                            output_data="自动标记为完成"
                        )
                        logging.info(f"自动标记上一个工具调用完成: {last_tool_id}")
                
                # 更新上一个工具调用ID
                callback_handler.last_tool_id = tool_id
                
                # 检查这个工具ID是否已经记录过
                if tool_id not in tool_call_map:
                    # 记录工具调用开始
                    tool_call_id = task_manager.record_tool_call(
                        workflow_id=workflow_id,
                        step_id=step_id,
                        tool_name=tool_name,
                        input_data=tool_use.get("input")
                    )
                    tool_call_map[tool_id] = tool_call_id
                    logging.info(f"记录工具调用开始: {tool_name}, ID: {tool_call_id}")
                    
                    # 如果有输出，则视为工具调用完成
                    if "output" in tool_use and tool_use["output"] is not None:
                        task_manager.complete_tool_call(
                            workflow_id=workflow_id,
                            step_id=step_id,
                            tool_call_id=tool_call_id,
                            output_data=tool_use.get("output")
                        )
                        logging.info(f"记录工具调用完成: {tool_name}")
                    
                    # 如果有错误，则视为工具调用失败
                    elif "error" in tool_use and tool_use["error"] is not None:
                        task_manager.fail_tool_call(
                            workflow_id=workflow_id,
                            step_id=step_id,
                            tool_call_id=tool_call_id,
                            error=tool_use.get("error")
                        )
                        logging.info(f"记录工具调用失败: {tool_name}, 错误: {tool_use.get('error')}")
                else:
                    # 如果这个工具ID已经记录过，检查是否有新的输出或错误
                    tool_call_id = tool_call_map[tool_id]
                    if "output" in tool_use and tool_use["output"] is not None:
                        task_manager.complete_tool_call(
                            workflow_id=workflow_id,
                            step_id=step_id,
                            tool_call_id=tool_call_id,
                            output_data=tool_use.get("output")
                        )
                        logging.info(f"记录工具调用完成: {tool_name}")
                    elif "error" in tool_use and tool_use["error"] is not None:
                        task_manager.fail_tool_call(
                            workflow_id=workflow_id,
                            step_id=step_id,
                            tool_call_id=tool_call_id,
                            error=tool_use.get("error")
                        )
                        logging.info(f"记录工具调用失败: {tool_name}, 错误: {tool_use.get('error')}")
            
            # 保留原有的处理逻辑，以防Strands框架在未来版本中修复这个问题
            elif tool_status == "started":
                # 记录工具调用开始
                tool_call_id = task_manager.record_tool_call(
                    workflow_id=workflow_id,
                    step_id=step_id,
                    tool_name=tool_name,
                    input_data=tool_use.get("input")
                )
                tool_call_map[tool_id] = tool_call_id
                logging.info(f"记录工具调用开始: {tool_name}, ID: {tool_call_id}")
            
            elif tool_status == "completed" and tool_id in tool_call_map:
                # 记录工具调用完成
                task_manager.complete_tool_call(
                    workflow_id=workflow_id,
                    step_id=step_id,
                    tool_call_id=tool_call_map[tool_id],
                    output_data=tool_use.get("output")
                )
                logging.info(f"记录工具调用完成: {tool_name}")
            
            elif tool_status == "failed" and tool_id in tool_call_map:
                # 记录工具调用失败
                task_manager.fail_tool_call(
                    workflow_id=workflow_id,
                    step_id=step_id,
                    tool_call_id=tool_call_map[tool_id],
                    error=tool_use.get("error")
                )
                logging.info(f"记录工具调用失败: {tool_name}, 错误: {tool_use.get('error')}")
            
            # 如果工具ID不在映射中，但状态不是started，记录警告
            elif tool_id not in tool_call_map and tool_status != "started":
                logging.warning(f"收到未知工具调用的状态更新: {tool_name}, 状态: {tool_status}, ID: {tool_id}")
        
        # 记录其他类型的事件
        else:
            logging.debug(f"收到其他类型的事件: {kwargs.keys()}")
    
    return callback_handler
