#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
将评估报告JSON数据转换为QuickSight可用的CSV文件
生成两个CSV文件：
1. workflow_table.csv - 工作流表
2. tool_call_table.csv - 工具调用表
"""

import json
import csv
import os
from datetime import datetime

# 示例JSON数据 - 实际使用时可以从文件读取
SAMPLE_JSON = '''
{
  "report": [
    {
      "execution_time": 57.709012,
      "performance_metrics": {
        "average_tool_execution_time": 5.2745411
      },
      "status": "completed",
      "step_statistics": {
        "completed": 1,
        "completion_rate": 1,
        "failed": 0,
        "total": 1
      },
      "tool_call_statistics": {
        "failed": 0,
        "success_rate": 1,
        "successful": 10,
        "total": 10
      },
      "tool_distribution": {
        "extract_exam_metadata": {
          "average_execution_time": 4.868112,
          "failed": 0,
          "successful": 1,
          "total": 1
        },
        "generate_fill_blank_question": {
          "average_execution_time": 3.708187,
          "failed": 0,
          "successful": 1,
          "total": 1
        },
        "generate_multiple_choice_question": {
          "average_execution_time": 3.47331866666667,
          "failed": 0,
          "successful": 3,
          "total": 3
        },
        "generate_single_choice_question": {
          "average_execution_time": 3.528803,
          "failed": 0,
          "successful": 3,
          "total": 3
        },
        "plan_exam_content": {
          "average_execution_time": 4.543524,
          "failed": 0,
          "successful": 1,
          "total": 1
        },
        "validate_exam_format": {
          "average_execution_time": 18.619223,
          "failed": 0,
          "successful": 1,
          "total": 1
        }
      },
      "workflow_id": "32013399-d744-4775-8d50-7fa46d3d711c",
      "workflow_name": "考试生成"
    },
    {
      "execution_time": 3.84583,
      "performance_metrics": {
        "average_tool_execution_time": 0
      },
      "status": "failed",
      "step_statistics": {
        "completed": 0,
        "completion_rate": 0,
        "failed": 1,
        "total": 1
      },
      "tool_call_statistics": {
        "failed": 0,
        "success_rate": 0,
        "successful": 0,
        "total": 0
      },
      "tool_distribution": {

      },
      "workflow_id": "f49f46ac-490a-42a8-915b-c65275fe961c",
      "workflow_name": "考试生成"
    },
    {
      "execution_time": 81.031083,
      "performance_metrics": {
        "average_tool_execution_time": 7.5285068
      },
      "status": "completed",
      "step_statistics": {
        "completed": 1,
        "completion_rate": 1,
        "failed": 0,
        "total": 1
      },
      "tool_call_statistics": {
        "failed": 0,
        "success_rate": 1,
        "successful": 10,
        "total": 10
      },
      "tool_distribution": {
        "extract_exam_metadata": {
          "average_execution_time": 5.994742,
          "failed": 0,
          "successful": 2,
          "total": 2
        },
        "generate_fill_blank_question": {
          "average_execution_time": 6.359602,
          "failed": 0,
          "successful": 1,
          "total": 1
        },
        "generate_multiple_choice_question": {
          "average_execution_time": 8.083026,
          "failed": 0,
          "successful": 2,
          "total": 2
        },
        "generate_single_choice_question": {
          "average_execution_time": 6.57154866666667,
          "failed": 0,
          "successful": 3,
          "total": 3
        },
        "plan_exam_content": {
          "average_execution_time": 4.724832,
          "failed": 0,
          "successful": 1,
          "total": 1
        },
        "validate_exam_format": {
          "average_execution_time": 16.330452,
          "failed": 0,
          "successful": 1,
          "total": 1
        }
      },
      "workflow_id": "06def76c-719a-4ebd-b7b9-24973e8af0ea",
      "workflow_name": "考试生成"
    }
  ],
  "status": "success"
}
'''

def create_workflow_table(data):
    """
    创建工作流表数据
    
    Args:
        data: 解析后的JSON数据
        
    Returns:
        list: 包含表头和数据行的列表
    """
    # 定义表头
    headers = [
        'workflow_id', 'workflow_name', 'status', 'execution_time',
        'average_tool_execution_time', 'total_steps', 'completed_steps',
        'failed_steps', 'step_completion_rate', 'total_tool_calls',
        'successful_tool_calls', 'failed_tool_calls', 'tool_call_success_rate',
        'timestamp'
    ]
    
    rows = [headers]  # 第一行是表头
    
    # 当前时间作为默认时间戳
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 处理每个工作流
    for workflow in data['report']:
        row = [
            workflow['workflow_id'],
            workflow['workflow_name'],
            workflow['status'],
            workflow['execution_time'],
            workflow['performance_metrics'].get('average_tool_execution_time', 0),
            workflow['step_statistics']['total'],
            workflow['step_statistics']['completed'],
            workflow['step_statistics']['failed'],
            workflow['step_statistics']['completion_rate'],
            workflow['tool_call_statistics']['total'],
            workflow['tool_call_statistics']['successful'],
            workflow['tool_call_statistics']['failed'],
            workflow['tool_call_statistics'].get('success_rate', 0),
            current_time  # 使用当前时间作为时间戳
        ]
        rows.append(row)
    
    return rows

def create_tool_call_table(data):
    """
    创建工具调用表数据
    
    Args:
        data: 解析后的JSON数据
        
    Returns:
        list: 包含表头和数据行的列表
    """
    # 定义表头
    headers = [
        'workflow_id', 'workflow_name', 'tool_name', 'total_calls',
        'successful_calls', 'failed_calls', 'success_rate',
        'average_execution_time', 'status'
    ]
    
    rows = [headers]  # 第一行是表头
    
    # 处理每个工作流
    for workflow in data['report']:
        workflow_id = workflow['workflow_id']
        workflow_name = workflow['workflow_name']
        status = workflow['status']
        
        # 处理每个工具
        for tool_name, tool_data in workflow['tool_distribution'].items():
            row = [
                workflow_id,
                workflow_name,
                tool_name,
                tool_data['total'],
                tool_data['successful'],
                tool_data['failed'],
                tool_data['successful'] / tool_data['total'] if tool_data['total'] > 0 else 0,
                tool_data['average_execution_time'],
                status
            ]
            rows.append(row)
    
    return rows

def write_csv(rows, filename):
    """
    将数据写入CSV文件
    
    Args:
        rows: 包含表头和数据行的列表
        filename: 输出文件名
    """
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    
    print(f"已创建文件: {filename}")

def main(json_data=None, input_file=None):
    """
    主函数
    
    Args:
        json_data: JSON字符串
        input_file: 输入JSON文件路径
    """
    # 确定数据来源
    if input_file:
        print(f"从文件读取数据: {input_file}")
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    elif json_data:
        print("使用提供的JSON字符串")
        data = json.loads(json_data)
    else:
        print("使用示例JSON数据")
        data = json.loads(SAMPLE_JSON)
    
    # 创建输出目录
    output_dir = "quicksight_data"
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建并写入工作流表
    workflow_rows = create_workflow_table(data)
    workflow_file = os.path.join(output_dir, "workflow_table.csv")
    write_csv(workflow_rows, workflow_file)
    
    # 创建并写入工具调用表
    tool_call_rows = create_tool_call_table(data)
    tool_call_file = os.path.join(output_dir, "tool_call_table.csv")
    write_csv(tool_call_rows, tool_call_file)
    
    print(f"\n数据已成功转换为CSV文件，保存在 {output_dir} 目录中")
    print(f"- 工作流表: {workflow_file}")
    print(f"- 工具调用表: {tool_call_file}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='将评估报告JSON数据转换为QuickSight可用的CSV文件')
    parser.add_argument('-f', '--file', help='输入JSON文件路径')
    args = parser.parse_args()
    
    main(input_file=args.file)
