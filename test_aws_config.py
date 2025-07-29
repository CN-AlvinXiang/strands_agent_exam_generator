#!/usr/bin/env python3
"""
测试AWS配置脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_aws_config():
    """测试AWS配置"""
    print("=== 测试AWS配置 ===")
    
    try:
        from exam_generator.config import aws_config, llm_config
        
        print(f"Profile: {aws_config.profile_name}")
        print(f"Access Key: {aws_config.access_key[:10]}..." if aws_config.access_key else "Access Key: 未设置")
        print(f"Secret Key: {aws_config.secret_key[:10]}..." if aws_config.secret_key else "Secret Key: 未设置")
        print(f"Region: {aws_config.region}")
        print(f"LLM Region: {llm_config.region_name}")
        print(f"Model ID: {llm_config.model_id}")
        
        if aws_config.access_key and aws_config.secret_key:
            print("\n✓ AWS凭证配置成功")
            
            # 测试设置环境变量
            aws_config.setup_credentials()
            print("✓ 环境变量设置成功")
            
            # 验证环境变量
            print(f"环境变量 AWS_ACCESS_KEY_ID: {os.environ.get('AWS_ACCESS_KEY_ID', '未设置')[:10]}...")
            print(f"环境变量 AWS_SECRET_ACCESS_KEY: {os.environ.get('AWS_SECRET_ACCESS_KEY', '未设置')[:10]}...")
            print(f"环境变量 AWS_DEFAULT_REGION: {os.environ.get('AWS_DEFAULT_REGION', '未设置')}")
            
            return True
        else:
            print("\n❌ AWS凭证未配置")
            print("\n请运行以下命令配置AWS凭证:")
            print("aws configure")
            print("\n或者设置环境变量:")
            print("export AWS_ACCESS_KEY_ID=your_access_key")
            print("export AWS_SECRET_ACCESS_KEY=your_secret_key")
            print("export AWS_DEFAULT_REGION=us-east-1")
            return False
            
    except Exception as e:
        print(f"❌ 测试AWS配置失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_bedrock_connection():
    """测试Bedrock连接"""
    print("\n=== 测试Bedrock连接 ===")
    
    try:
        import boto3
        import json
        from exam_generator.config import aws_config, llm_config
        
        # 设置凭证
        aws_config.setup_credentials()
        
        # 创建Bedrock客户端
        client = boto3.client(
            service_name='bedrock-runtime',
            region_name=llm_config.region_name
        )
        
        print(f"正在测试连接到 {llm_config.model_id}...")
        
        # 测试简单的API调用
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 50,
            "temperature": 0.7,
            "messages": [
                {
                    "role": "user",
                    "content": "Hello, please respond with 'Connection test successful'"
                }
            ]
        }
        
        response = client.invoke_model(
            modelId=llm_config.model_id,
            body=json.dumps(request_body)
        )
        
        # 解析响应
        response_body = json.loads(response['body'].read())
        content = response_body.get('content', [])
        if content and len(content) > 0:
            message = content[0].get('text', '')
            print(f"模型响应: {message}")
        
        print("✓ Bedrock连接测试成功")
        return True
        
    except Exception as e:
        print(f"❌ Bedrock连接测试失败: {str(e)}")
        
        # 提供具体的错误建议
        error_str = str(e)
        if "AccessDeniedException" in error_str:
            print("\n建议:")
            print("1. 检查AWS凭证是否正确")
            print("2. 确保AWS账户有访问Bedrock的权限")
            print("3. 确保在正确的区域启用了Claude模型")
        elif "ValidationException" in error_str:
            print("\n建议:")
            print("1. 检查模型ID是否正确")
            print("2. 确保模型在当前区域可用")
        elif "throttlingException" in error_str:
            print("\n建议:")
            print("1. 请求过于频繁，请稍后重试")
        
        return False

def main():
    """主函数"""
    print("开始测试AWS配置...")
    
    # 测试AWS配置
    if not test_aws_config():
        return
    
    # 测试Bedrock连接
    test_bedrock_connection()

if __name__ == "__main__":
    main()