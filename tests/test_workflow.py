import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from exam_generator.agent import generate_exam
from exam_generator.tools.content_tools import extract_exam_metadata, plan_exam_content
from exam_generator.tools.exam_tools import (
    generate_single_choice_question,
    generate_multiple_choice_question,
    generate_fill_blank_question
)
from exam_generator.tools.render_tools import send_to_flask_service

class TestWorkflow(unittest.TestCase):
    """测试完整工作流程"""
    
    @patch('exam_generator.tools.exam_tools.call_claude')
    @patch('exam_generator.tools.render_tools.requests.post')
    def test_single_question_workflow(self, mock_post, mock_call_claude):
        """测试单个题目的工作流程"""
        # 模拟Claude API返回
        mock_call_claude.return_value = "## 单选题\n\n1+1=?\n\n- (x) 2\n- ( ) 3\n- ( ) 4\n- ( ) 5"
        
        # 模拟Flask服务响应
        mock_response = MagicMock()
        mock_response.json.return_value = {"message": "保存成功\n查看链接http://localhost:5006/get_html/test"}
        mock_post.return_value = mock_response
        
        # 创建测试请求
        exam_request = {
            "inputs": {
                "grade": "1st",
                "subject": "Mathematics",
                "count": 1,
                "types": "singleChoice",
                "topics": "加法",
                "difficulty": "easy"
            }
        }
        
        # 提取元数据
        metadata = extract_exam_metadata(exam_request)
        
        # 规划考试内容
        plan = plan_exam_content(metadata)
        
        # 生成题目
        question = generate_single_choice_question(plan["topics"][0], metadata["difficulty"])
        
        # 发送到Flask服务
        result = send_to_flask_service(question)
        
        # 验证结果
        self.assertIn("保存成功", result["message"])
        self.assertIn("http://", result["message"])
    
    @patch('exam_generator.agent.create_agent')
    @patch('exam_generator.tools.render_tools.requests.post')
    def test_generate_exam(self, mock_post, mock_create_agent):
        """测试generate_exam函数"""
        # 模拟Agent返回
        mock_agent = MagicMock()
        mock_agent.return_value.message = "## 单选题\n\n1+1=?\n\n- (x) 2\n- ( ) 3\n- ( ) 4\n- ( ) 5"
        mock_create_agent.return_value = mock_agent
        
        # 模拟Flask服务响应
        mock_response = MagicMock()
        mock_response.json.return_value = {"message": "保存成功\n查看链接http://localhost:5006/get_html/test"}
        mock_post.return_value = mock_response
        
        # 创建测试请求
        exam_request = {
            "inputs": {
                "grade": "1st",
                "subject": "Mathematics",
                "count": 1,
                "types": "singleChoice",
                "topics": "加法",
                "difficulty": "easy"
            }
        }
        
        # 调用函数
        result = generate_exam(exam_request, "test-workflow-id")
        
        # 验证结果
        self.assertIn("exam_content", result)
        self.assertIn("render_result", result)
        self.assertIn("message", result["render_result"])
    
    @patch('exam_generator.tools.exam_tools.call_claude')
    def test_parallel_question_generation(self, mock_call_claude):
        """测试并行生成题目"""
        from exam_generator.tools.exam_tools import generate_questions_parallel
        
        # 模拟Claude API返回
        mock_call_claude.return_value = "## 单选题\n\n1+1=?\n\n- (x) 2\n- ( ) 3\n- ( ) 4\n- ( ) 5"
        
        # 创建题目规格
        question_specs = [
            {"type": "singleChoice", "topic": "加法", "difficulty": "easy"},
            {"type": "singleChoice", "topic": "减法", "difficulty": "easy"},
            {"type": "multipleChoice", "topic": "数字", "difficulty": "medium"}
        ]
        
        # 调用函数
        results = generate_questions_parallel(question_specs)
        
        # 验证结果
        self.assertEqual(len(results), 3)
        self.assertTrue(all(isinstance(result, str) for result in results))
        self.assertTrue(any("## 单选题" in result for result in results))

if __name__ == '__main__':
    unittest.main()
