#!/bin/bash
# 测试考试生成器API

echo "发送测试请求到考试生成器API..."

# 检查服务是否运行
if [ ! -f agent.pid ]; then
    echo "警告: Agent服务可能未运行，请先运行 './start_agent.sh'"
fi

# 发送测试请求
curl -X POST http://localhost:5001/workflows/run \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": {
      "grade": "5th",
      "subject": "Math",
      "count": 3,
      "types": "singleChoice,multipleChoice",
      "difficulty": "medium",
      "topics": "基础计算",
      "teacher_notes": "测试请求"
    },
    "response_mode": "streaming",
    "user": "test-user"
  }'

echo -e "\n测试请求已发送。"
