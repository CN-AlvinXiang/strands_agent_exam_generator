#!/usr/bin/env python3
"""
调试脚本 - 测试后端服务的各个组件
"""

import sys
import os
import json
import traceback

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试所有必要的导入"""
    print("=== 测试导入 ===")
    try:
        print("1. 测试基础导入...")
        import logging
        from flask import Flask, request, jsonify
        from flask_cors import CORS
        import boto3
        print("✓ 基础导入成功")
        
        print("2. 测试配置导入...")
        from exam_generator.config import server_config, aws_config, llm_config, exam_config
        print("✓ 配置导入成功")
        
        print("3. 测试工具导入...")
        from exam_generator.utils import setup_logging, task_manager, handle_error, TaskStatus
        print("✓ 工具导入成功")
        
        print("4. 测试Agent导入...")
        from exam_generator.agent import generate_exam
        print("✓ Agent导入成功")
        
        print("5. 测试工具模块导入...")
        from exam_generator.tools import (
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
        print("✓ 工具模块导入成功")
        
        return True
    except Exception as e:
        print(f"✗ 导入失败: {str(e)}")
        traceback.print_exc()
        return False

def test_aws_config():
    """测试AWS配置"""
    print("\n=== 测试AWS配置 ===")
    try:
        from exam_generator.config import aws_config, llm_config
        
        print(f"AWS Access Key: {aws_config.access_key[:10]}..." if aws_config.access_key != "*" else "AWS Access Key: 未配置")
        print(f"AWS Secret Key: {aws_config.secret_key[:10]}..." if aws_config.secret_key != "*" else "AWS Secret Key: 未配置")
        print(f"AWS Region: {llm_config.region_name}")
        print(f"Model ID: {llm_config.model_id}")
        
        if aws_config.access_key == "*" or aws_config.secret_key == "*":
            print("⚠️  AWS凭证未配置，需要设置环境变量或修改config.py")
            return False
        
        print("✓ AWS配置检查通过")
        return True
    except Exception as e:
        print(f"✗ AWS配置检查失败: {str(e)}")
        traceback.print_exc()
        return False

def test_bedrock_connection():
    """测试Bedrock连接"""
    print("\n=== 测试Bedrock连接 ===")
    try:
        from exam_generator.config import aws_config, llm_config
        
        # 设置凭证
        aws_config.setup_credentials()
        
        # 创建Bedrock客户端
        client = boto3.client(
            service_name='bedrock-runtime',
            region_name=llm_config.region_name
        )
        
        # 测试简单的API调用
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 100,
            "temperature": 0.7,
            "messages": [
                {
                    "role": "user",
                    "content": "Hello, this is a test."
                }
            ]
        }
        
        response = client.invoke_model(
            modelId=llm_config.model_id,
            body=json.dumps(request_body)
        )
        
        print("✓ Bedrock连接测试成功")
        return True
    except Exception as e:
        print(f"✗ Bedrock连接测试失败: {str(e)}")
        traceback.print_exc()
        return False

def test_agent_creation():
    """测试Agent创建"""
    print("\n=== 测试Agent创建 ===")
    try:
        from exam_generator.agent import create_agent
        
        agent = create_agent()
        print("✓ Agent创建成功")
        return True
    except Exception as e:
        print(f"✗ Agent创建失败: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("开始诊断后端服务...")
    
    # 测试导入
    if not test_imports():
        print("\n❌ 导入测试失败，请检查依赖安装")
        return
    
    # 测试AWS配置
    if not test_aws_config():
        print("\n❌ AWS配置测试失败，请检查AWS凭证配置")
        return
    
    # 测试Bedrock连接
    if not test_bedrock_connection():
        print("\n❌ Bedrock连接测试失败，请检查AWS凭证和网络连接")
        return
    
    # 测试Agent创建
    if not test_agent_creation():
        print("\n❌ Agent创建测试失败")
        return
    
    print("\n✅ 所有测试通过！后端服务应该可以正常运行")

if __name__ == "__main__":
    main()