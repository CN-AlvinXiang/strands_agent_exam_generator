#!/usr/bin/env python
import unittest
import sys
import os

def run_tests():
    """运行所有测试"""
    # 确保tests目录存在
    if not os.path.exists('tests'):
        os.makedirs('tests')
        # 创建__init__.py文件
        with open(os.path.join('tests', '__init__.py'), 'w') as f:
            pass
    
    # 发现并加载所有测试
    test_suite = unittest.defaultTestLoader.discover('tests', pattern='test_*.py')
    
    # 运行测试
    result = unittest.TextTestRunner(verbosity=2).run(test_suite)
    
    # 根据测试结果设置退出码
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_tests())
