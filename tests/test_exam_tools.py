import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from exam_generator.tools.exam_tools import (
    generate_single_choice_question,
    generate_multiple_choice_question,
    generate_fill_blank_question,
    call_claude,
    get_bedrock_client,
    question_cache
)

class TestExamTools(unittest.TestCase):
    """测试题目生成工具"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 清空缓存
        if os.path.exists(question_cache.cache_dir):
            for file in os.listdir(question_cache.cache_dir):
                if file.endswith('.pkl'):
                    os.remove(os.path.join(question_cache.cache_dir, file))
    
    @patch('exam_generator.tools.exam_tools.call_claude')
    def test_generate_single_choice_question(self, mock_call_claude):
        """测试单选题生成"""
        # 模拟Claude API返回
        mock_call_claude.return_value = "## 单选题\n\n1+1=?\n\n- (x) 2\n- ( ) 3\n- ( ) 4\n- ( ) 5"
        
        # 调用函数
        result = generate_single_choice_question("加法", "easy")
        
        # 验证结果
        self.assertTrue(result.startswith("## 单选题"))
        self.assertIn("- (x)", result)
        self.assertIn("- ( )", result)
        
        # 验证调用参数
        mock_call_claude.assert_called_once()
        args, kwargs = mock_call_claude.call_args
        self.assertIn("加法", args[0])
        self.assertIn("easy", args[0])
    
    @patch('exam_generator.tools.exam_tools.call_claude')
    def test_generate_multiple_choice_question(self, mock_call_claude):
        """测试多选题生成"""
        # 模拟Claude API返回
        mock_call_claude.return_value = "## 多选题\n\n以下哪些是偶数？\n\n- [x] 2\n- [ ] 3\n- [x] 4\n- [ ] 5"
        
        # 调用函数
        result = generate_multiple_choice_question("偶数", "medium")
        
        # 验证结果
        self.assertTrue(result.startswith("## 多选题"))
        self.assertIn("- [x]", result)
        self.assertIn("- [ ]", result)
    
    @patch('exam_generator.tools.exam_tools.call_claude')
    def test_generate_fill_blank_question(self, mock_call_claude):
        """测试填空题生成"""
        # 模拟Claude API返回
        mock_call_claude.return_value = "## 填空题\n\n1+1=______\n\n- R:= 2"
        
        # 调用函数
        result = generate_fill_blank_question("加法", "easy")
        
        # 验证结果
        self.assertTrue(result.startswith("## 填空题"))
        self.assertIn("______", result)
        self.assertIn("- R:=", result)
    
    def test_question_cache(self):
        """测试题目缓存"""
        # 模拟一个题目
        question = "## 单选题\n\n1+1=?\n\n- (x) 2\n- ( ) 3\n- ( ) 4\n- ( ) 5"
        
        # 设置缓存
        question_cache.set("加法", "easy", "singleChoice", question)
        
        # 获取缓存
        cached = question_cache.get("加法", "easy", "singleChoice")
        
        # 验证缓存
        self.assertEqual(cached, question)
        
        # 测试不存在的缓存
        cached = question_cache.get("减法", "easy", "singleChoice")
        self.assertIsNone(cached)
    
    @patch('boto3.client')
    def test_get_bedrock_client(self, mock_client):
        """测试获取Bedrock客户端"""
        # 调用函数
        get_bedrock_client()
        
        # 验证调用
        mock_client.assert_called_once()
        args, kwargs = mock_client.call_args
        self.assertEqual(kwargs['service_name'], 'bedrock-runtime')

if __name__ == '__main__':
    unittest.main()
