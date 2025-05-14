import os
import json
from flask import Flask, request, abort

app = Flask(__name__)

# 指向你的 data/processed 目录
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), '../data/processed')
os.makedirs(PROCESSED_DIR, exist_ok=True)

def receive(query: dict):
    """
    接收 query 对象并写入 JSON 文件，
    然后触发后续 Agent 流程（可改为 subprocess、线程或消息队列）
    """
    target = os.path.join(PROCESSED_DIR, f"{query['id']}.json")
    with open(target, 'w', encoding='utf-8') as f:
        json.dump(query, f, ensure_ascii=False, indent=2)
    # TODO: 在这里真正唤醒 agent 主流程，比如：
    # from my_image_agent.src.agent import main
    # main(query_id=query['id'])
    print(f"[agent.py] 已保存 query → {target}")

@app.route('/api/trigger-agent', methods=['POST'])
def trigger_agent():
    # 前端已做了必填校验，这里再二次检查
    query_id = request.form.get('id')
    text     = request.form.get('text')
    image    = request.files.get('image')

    if not query_id or not text:
        abort(400, '缺少 id 或 text')
    if image is None:
        abort(400, '缺少 image 文件')

    # 先把图片保存到 processed 目录
    img_path = os.path.join(PROCESSED_DIR, f"{query_id}{os.path.splitext(image.filename)[1]}")
    image.save(img_path)

    # 构造 query 对象
    query = {
        'id': query_id,
        'text': text,
        'image_path': img_path
    }

    # 写入并触发后端 Agent
    receive(query)
    return 'OK', 200

if __name__ == '__main__':
    # 代理运行在 5000 端口，React 默认是 3000，记得 CORS 或 proxy 配置
    app.run(host='0.0.0.0', port=5000, debug=True)
