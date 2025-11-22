# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import os
import model.service as service
from flask_cors import CORS  
from flask import Flask, request, jsonify, send_from_directory, Response, stream_with_context
import requests
import datetime
import urllib.parse
import pathlib
os.environ["CUDA_VISIBLE_DEVICES"] = "2"

app = Flask(__name__, static_folder='static')

CORS(app, resources={
    r"/*": {
        "origins": [
            "http://218.199.69.86:5001",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://shizi.hzau.edu.cn:5001"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
}, supports_credentials=True)

# 文件资源路径
RESOURCES_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources/files')
if not os.path.exists(RESOURCES_FOLDER):
    os.makedirs(RESOURCES_FOLDER)

@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')


@app.route('/getMessage', methods=['POST'])
def get_message():
    data = request.get_json()
    message = data.get('userMessage')
    history = data.get('history', [])

    response_generator = service.answer(message, history)

    def generate():
        try:
            for chunk in response_generator:
                yield getattr(chunk, 'content', str(chunk))
        except Exception as e:
            print(f"流式响应出错: {str(e)}")
            yield f"出错: {str(e)}"

    return Response(stream_with_context(generate()), mimetype='text/plain')


@app.route('/getMessageWeb', methods=['POST'])
def get_message_web():
    data = request.get_json()
    message = data.get('userMessage')
    history = data.get('history', [])

    response_generator = service.answer_web(message, history)

    def generate():
        try:
            for chunk in response_generator:
                yield getattr(chunk, 'content', str(chunk))
        except Exception as e:
            print(f"流式响应出错: {str(e)}")
            yield f"出错: {str(e)}"

    return Response(stream_with_context(generate()), mimetype='text/plain')

# 代理请求
@app.route('/proxy', methods=['POST'])
def proxy():
    data = request.get_json()

    target_url = "https://www.hzau.edu.cn/aop_views/search/modules/resultpcall/searchList"
    headers = {
        "Content-Type": "application/json",
        "Referer": "https://www.hzau.edu.cn/",
        "User-Agent": "Mozilla/5.0"
    }

    resp = requests.post(target_url, json=data, headers=headers)
    result_json = resp.json()

    try:
        first_url = result_json["data"]["list"][0]["url"]
        full_url = "https://www.hzau.edu.cn" + first_url
        return jsonify({"redirect_url": full_url})
    except Exception as e:
        return jsonify({"error": "No result found", "details": str(e)}), 400


# 新增接口：获取所有资源文件列表
@app.route('/api/files', methods=['GET'])
def get_files():
    try:
        files_info = []
        print("RESOURCES_FOLDER",RESOURCES_FOLDER)
        
        # 遍历resources文件夹中的所有文件
        for filename in os.listdir(RESOURCES_FOLDER):
            file_path = os.path.join(RESOURCES_FOLDER, filename)
            
            # 确保是文件而不是目录
            if os.path.isfile(file_path):
                # 获取文件大小
                file_size = os.path.getsize(file_path)
                size_str = format_file_size(file_size)
                
                # 获取文件最后修改时间
                mod_time = os.path.getmtime(file_path)
                update_date = datetime.datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d')
                
                # 获取文件格式（扩展名）
                file_ext = os.path.splitext(filename)[1].lower().replace('.', '')
                if not file_ext:
                    file_ext = 'unknown'
                
                # 确定文件类型
                file_type = get_file_type(file_ext)
                
                # 添加文件信息到列表
                files_info.append({
                    'name': filename,
                    'type': file_type,
                    'format': file_ext,
                    'size': size_str,
                    'updateDate': update_date
                })
        
        response = jsonify({
            'code': 200, 
            'message': 'success', 
            'data': files_info
        })
        
        # 添加CORS响应头
        # response.headers.add('Access-Control-Allow-Origin', 'http://218.199.69.86:5001','http://shizi.hzau.edu.cn:5001')
        # response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        # response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        # response.headers.add('Access-Control-Allow-Credentials', 'true')
        
        return response
        
    except Exception as e:
        print(f"获取文件列表出错: {str(e)}")
        response = jsonify({
            'code': 500, 
            'message': f'获取文件列表失败: {str(e)}', 
            'data': []
        })
        
        # # 添加CORS响应头
        # response.headers.add('Access-Control-Allow-Origin', 'http://218.199.69.86:5001','http://shizi.hzau.edu.cn:5001')
        # response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        # response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        # response.headers.add('Access-Control-Allow-Credentials', 'true')
        
        return response, 500


# 新增接口：获取文件下载链接
@app.route('/api/files/download', methods=['POST'])
def get_file_download_url():
    try:
        data = request.get_json()
        filename = data.get('filename')
        print("filename",filename)
        
        if not filename:
            response = jsonify({
                'code': 400, 
                'message': '文件名不能为空', 
                'data': None
            })
            # 添加CORS响应头
            # response.headers.add('Access-Control-Allow-Origin', 'http://218.199.69.86:5001','http://shizi.hzau.edu.cn:5001')
            # response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
            # response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            # response.headers.add('Access-Control-Allow-Credentials', 'true')
            return response, 400
        
        # 确保文件名安全，防止目录遍历攻击
        safe_filename = os.path.basename(filename)
        file_path = os.path.join(RESOURCES_FOLDER, safe_filename)
        
        # 检查文件是否存在
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            response = jsonify({
                'code': 404, 
                'message': f'文件 {safe_filename} 不存在', 
                'data': None
            })
            # 添加CORS响应头
            # response.headers.add('Access-Control-Allow-Origin', 'http://218.199.69.86:5001','http://shizi.hzau.edu.cn:5001')
            # response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
            # response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            # response.headers.add('Access-Control-Allow-Credentials', 'true')
            return response, 404
        
        # 生成下载URL
        encoded_filename = urllib.parse.quote(safe_filename)
        download_url = f'/api/files/download/{encoded_filename}'
        
        response = jsonify({
            'code': 200, 
            'message': 'success', 
            'data': {
                'downloadUrl': download_url,
                'fileName': safe_filename
            }
        })
        # 添加CORS响应头
        # response.headers.add('Access-Control-Allow-Origin', 'http://218.199.69.86:5001','http://shizi.hzau.edu.cn:5001')
        # response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        # response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        # response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
        
    except Exception as e:
        print(f"获取下载链接出错: {str(e)}")
        response = jsonify({
            'code': 500, 
            'message': f'获取下载链接失败: {str(e)}', 
            'data': None
        })
        # 添加CORS响应头
        # response.headers.add('Access-Control-Allow-Origin', 'http://218.199.69.86:5001','http://shizi.hzau.edu.cn:5001')
        # response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        # response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        # response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response, 500


# 实际文件下载处理
@app.route('/api/files/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        response = send_from_directory(
            RESOURCES_FOLDER, 
            filename, 
            as_attachment=True
        )
        # 添加CORS响应头
        # response.headers.add('Access-Control-Allow-Origin', 'http://218.199.69.86:5001','http://shizi.hzau.edu.cn:5001')
        # response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        # response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        # response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
    except Exception as e:
        print(f"下载文件出错: {str(e)}")
        response = jsonify({
            'code': 500,
            'message': f'下载文件失败: {str(e)}'
        })
        # 添加CORS响应头
        # response.headers.add('Access-Control-Allow-Origin', 'http://218.199.69.86:5001','http://shizi.hzau.edu.cn:5001')
        # response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        # response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        # response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response, 500


# 工具函数：格式化文件大小
def format_file_size(size_in_bytes):
    # 如果小于1KB
    if size_in_bytes < 1024:
        return f"{size_in_bytes}B"
    # 如果小于1MB
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.1f}KB"
    # 如果小于1GB
    elif size_in_bytes < 1024 * 1024 * 1024:
        return f"{size_in_bytes / (1024 * 1024):.1f}MB"
    # 如果大于等于1GB
    else:
        return f"{size_in_bytes / (1024 * 1024 * 1024):.1f}GB"


# 工具函数：根据文件扩展名确定文件类型
def get_file_type(extension):
    # 学术文档类型
    academic_extensions = ['pdf', 'doc', 'docx', 'ppt', 'pptx', 'tex']
    # 行政文件类型
    administration_extensions = ['xlsx', 'xls', 'csv', 'txt']
    # 学生事务类型
    student_extensions = ['pdf', 'doc', 'docx']
    # 教学类型
    teaching_extensions = ['pdf', 'ppt', 'pptx']
    
    # 简单根据扩展名分类，实际应用可能需要更复杂的逻辑
    if extension in academic_extensions:
        return 'academic'
    elif extension in administration_extensions:
        return 'administration'
    elif extension in student_extensions:
        return 'student'
    elif extension in teaching_extensions:
        return 'teaching'
    else:
        return 'other'


# 处理预检请求的OPTIONS方法
@app.route('/getMessage', methods=['OPTIONS'])
def options_getMessage():
    response = app.make_default_options_response()
    # response.headers.add('Access-Control-Allow-Origin', 'http://218.199.69.86:5001','http://shizi.hzau.edu.cn:5001')
    # response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
    # response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    # response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

@app.route('/getMessageWeb', methods=['OPTIONS'])
def options_getMessageWeb():
    response = app.make_default_options_response()
    # response.headers.add('Access-Control-Allow-Origin', 'http://218.199.69.86:5001','http://shizi.hzau.edu.cn:5001')
    # response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
    # response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    # response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

@app.route('/api/files', methods=['OPTIONS'])
def options_files():
    response = app.make_default_options_response()
    # response.headers.add('Access-Control-Allow-Origin', 'http://218.199.69.86:5001','http://shizi.hzau.edu.cn:5001')
    # response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
    # response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    # response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

@app.route('/api/files/download', methods=['OPTIONS'])
def options_files_download():
    response = app.make_default_options_response()
    # response.headers.add('Access-Control-Allow-Origin', 'http://218.199.69.86:5001','http://shizi.hzau.edu.cn:5001')
    # response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
    # response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    # response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# 运行 Flask 应用
if __name__ == '__main__':
    # # 设置自动打开浏览器
    # def open_browser():
    #     webbrowser.open_new("http://127.0.0.1:5000/")
    #
    # Timer(1, open_browser).start()  # 延迟1秒打开，确保服务器先启动
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"
    app.run(host="0.0.0.0",port=5001)
