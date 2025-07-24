from flask import Flask, request, send_from_directory, jsonify

import os
import markdown
import time
from jinja2 import Environment, PackageLoader, select_autoescape
import re
import uuid
import requests

app = Flask(__name__)

# 配置文件夹路径
UPLOAD_FOLDER = './markdown-quiz-files'
OUTPUT_FOLDER = 'data'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

# 确保文件夹存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def get_host_address():
    """获取主机地址，优先使用本地地址"""
    try:
        # 首先尝试获取本地IP地址
        import socket
        hostname = socket.gethostname()
        # 尝试获取本地IP地址
        local_ip = socket.gethostbyname(hostname)
        return local_ip
    except:
        # 如果获取本地IP失败，则使用localhost
        return "localhost"


@app.route('/upload_markdown', methods=['POST'])
def upload_markdown():
    host_ip = get_host_address()
    content = request.get_data(as_text=True)
    content = re.sub( r"^\s{3}-","    -",content,flags=re.MULTILINE)
    if content is None:
        return jsonify({"error": "Invalid input"}), 400
    """Render quiz in Markdown format to HTML."""
    
    # 添加调试信息
    print("原始Markdown内容:")
    print(content)
    
    # 确保题目被正确包装在<p>标签中
    # 在每个题目标题后添加一个空行，确保Markdown解析器将题目内容包装在<p>标签中
    content = re.sub(r'(## [^\n]+)\n', r'\1\n\n', content)
    
    extensions = [
        "tables", "app.extensions.checkbox", "app.extensions.radio",
        "app.extensions.textbox"
    ]
    html = markdown.markdown(content,
                             extensions=extensions,
                             output_format="html5")
    
    # 添加调试信息
    print("生成的HTML内容:")
    print(html)
    
    # 确保每个题目都被包装在一个div中，方便JavaScript识别
    html = re.sub(r'<h2>([^<]+)</h2>', r'<div class="question-container"><h2>\1</h2>', html)
    html = re.sub(r'(<ul class="(?:radio-list|checklist|textbox)">[^<]*(?:<li>.*?</li>\s*)+</ul>)', r'\1</div>', html)
    env = Environment(loader=PackageLoader('app', 'static'),
                      autoescape=select_autoescape(['html', 'xml']))
    javascript = env.get_template('app.js').render()
    test_html = env.get_template('base.html').render(content=html,
                                                     javascript=javascript)
    
    # 添加调试信息
    print("最终HTML内容:")
    print(test_html)
    test_html = env.get_template('wrapper.html').render(content=test_html)
    filename = str(uuid.uuid4())
    with open(os.path.join(OUTPUT_FOLDER, f"{filename}.html"),
              "w+",
              encoding='utf-8') as f:  # create final file
        f.write(test_html)

    return jsonify(
        {"message":
         f"保存成功\n查看链接http://{host_ip}:5006/get_html/{filename}"}), 200


@app.route('/get_html/<filename>', methods=['GET'])
def get_html(filename):
    if not filename.endswith('.html'):
        filename += '.html'

    file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True, port=5006, host='0.0.0.0')
