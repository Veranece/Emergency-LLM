"""
应急智能体 Web API 服务
提供前端调用的 RESTful API 接口
"""
import sys
import os
from flask import Flask, request, Response, jsonify, stream_with_context
from flask_cors import CORS
import json

# 添加 new_main 目录到路径，以便导入 service 模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'new_main'))

from model.service import answer

app = Flask(__name__, static_folder='static', static_url_path='')

# 配置 CORS，允许跨域请求
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})


@app.route('/')
def index():
    """返回主页"""
    return app.send_static_file('test.html')
 

@app.route('/getMessageWeb', methods=['POST', 'OPTIONS'])
def get_message_web():
    """
    获取智能体回复的 API 接口（流式响应）
    
    请求格式:
    {
        "userMessage": "用户消息内容",
        "history": [
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "..."}
        ]
    }
    
    响应: 流式返回 AI 回复的文本内容
    """
    # 处理 OPTIONS 预检请求
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        # 获取请求数据
        data = request.get_json()
        
        if not data or 'userMessage' not in data:
            return jsonify({'error': '缺少必要参数 userMessage'}), 400
        
        user_message = data.get('userMessage', '')
        history = data.get('history', [])
        
        # 验证输入
        if not user_message.strip():
            return jsonify({'error': '消息内容不能为空'}), 400
        
        print(f"\n[收到请求] 用户消息: {user_message}")
        print(f"[历史记录] 条数: {len(history)}")
        
        # 定义流式生成器函数
        def generate():
            """流式生成 AI 回复"""
            try:
                print(f"[开始调用] service.answer() 函数")
                
                # 调用 service.py 的 answer 函数
                response = answer(user_message, history)
                
                print(f"[返回类型] {type(response)}")
                
                # 如果返回的是生成器（支持流式）
                if hasattr(response, '__iter__') and not isinstance(response, (str, bytes)):
                    chunk_count = 0
                    for chunk in response:
                        try:
                            # 处理 OpenAI Stream 对象
                            # 提取 chunk.choices[0].delta.content
                            content = None
                            if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                                delta = chunk.choices[0].delta
                                # 尝试获取 content 字段
                                if hasattr(delta, 'content') and delta.content:
                                    content = delta.content
                                # 尝试获取 reasoning_content 字段（Qwen3 模型）
                                elif hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                                    content = delta.reasoning_content
                            
                            if content:
                                chunk_count += 1
                                # 将字符串编码为 UTF-8 字节
                                yield content.encode('utf-8')
                        except Exception as chunk_error:
                            print(f"[警告] 处理数据块出错: {chunk_error}")
                            continue
                    
                    print(f"[响应完成] 已发送 {chunk_count} 个数据块")
                else:
                    # 如果返回的是完整字符串，逐字输出模拟流式效果
                    response_text = str(response)
                    print(f"[响应长度] {len(response_text)} 字符")
                    chunk_size = 10  # 每次发送的字符数
                    for i in range(0, len(response_text), chunk_size):
                        yield response_text[i:i+chunk_size].encode('utf-8')
                    print("[响应完成] 完整响应已发送")
                
            except ImportError as e:
                error_msg = f"模块导入错误: {str(e)}"
                print(f"[导入错误] {error_msg}")
                import traceback
                traceback.print_exc()
                yield f"\n\n[系统错误: {error_msg}]\n请检查 service.py 和相关依赖是否正确安装".encode('utf-8')
            except Exception as e:
                error_msg = f"生成回复时出错: {str(e)}"
                print(f"[错误] {error_msg}")
                import traceback
                traceback.print_exc()
                yield f"\n\n[系统错误: {error_msg}]".encode('utf-8')
        
        # 返回流式响应
        return Response(
            stream_with_context(generate()),
            mimetype='text/plain',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
        
    except Exception as e:
        error_msg = f"处理请求时出错: {str(e)}"
        print(f"[错误] {error_msg}")
        return jsonify({'error': error_msg}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'ok',
        'message': '应急智能体 API 服务运行正常'
    })


@app.errorhandler(404)
def not_found(error):
    """404 错误处理"""
    return jsonify({'error': '接口不存在'}), 404


@app.errorhandler(500)
def internal_error(error):
    """500 错误处理"""
    return jsonify({'error': '服务器内部错误'}), 500


if __name__ == '__main__':
    print("=" * 70)
    print("应急智能体 Web API 服务启动中...")
    print("=" * 70)
    print("本地访问:")
    print(f"  前端页面: http://localhost:5001")
    print(f"  API 接口: http://localhost:5001/getMessageWeb")
    print(f"  健康检查: http://localhost:5001/health")
    print("-" * 70)
    print("外网访问:")
    print(f"  前端页面: http://218.199.69.58:5001")
    print(f"  API 接口: http://218.199.69.58:5001/getMessageWeb")
    print(f"  健康检查: http://218.199.69.58:5001/health")
    print("=" * 70)
    print("注意: 如果外网无法访问，请检查防火墙是否开放5001端口")
    print("=" * 70)
    
    # 启动 Flask 应用
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True,
        threaded=True
    )

