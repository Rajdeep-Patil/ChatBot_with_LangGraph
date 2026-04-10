from flask import Flask, request, jsonify, render_template, Response, stream_with_context
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ChatBot_with_Sidebar'))
from ChatBot_with_Sidebar.ChatBotWithSidebarBackend import ChatBot
from langchain_core.messages import HumanMessage
import uuid
import json

app = Flask(__name__)

_chatbot_instance = None
workflow = None
retrieve_all_threads = None

def get_workflow():
    global _chatbot_instance, workflow, retrieve_all_threads
    if workflow is None:
        _chatbot_instance = ChatBot('llama-3.3-70b-versatile')
        workflow, retrieve_all_threads = _chatbot_instance.WorkflowFunction()
    return workflow, retrieve_all_threads

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/threads', methods=['GET'])
def get_threads():
    wf, retrieve = get_workflow()
    thread_ids = retrieve()
    thread_dict = {}
    for tid in thread_ids:
        state = wf.get_state(config={'configurable': {'thread_id': tid}})
        messages = state.values.get('messages', [])
        name = messages[0].content[:30] if messages else ''
        if name:
            thread_dict[tid] = name
    return jsonify({'threads': thread_dict})

@app.route('/api/thread/<thread_id>', methods=['GET'])
def get_thread_messages(thread_id):
    wf, _ = get_workflow()
    state = wf.get_state(config={'configurable': {'thread_id': thread_id}})
    messages = state.values.get('messages', [])
    result = []
    for msg in messages:
        role = 'user' if isinstance(msg, HumanMessage) else 'ai'
        result.append({'role': role, 'content': msg.content})
    return jsonify({'messages': result})

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message', '')
    thread_id = data.get('thread_id', str(uuid.uuid4()))

    if not user_input:
        return jsonify({'error': 'Message is required'}), 400

    wf, _ = get_workflow()

    def generate():
        input_dict = {'messages': [HumanMessage(content=user_input)]}
        config = {'configurable': {'thread_id': thread_id}}
        full_response = ''
        try:
            for message_chunk, metadata in wf.stream(input_dict, config=config, stream_mode='messages'):
                chunk = message_chunk.content
                if chunk:
                    full_response += chunk
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            yield f"data: {json.dumps({'done': True, 'full': full_response})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    response = Response(stream_with_context(generate()), mimetype='text/event-stream')
    response.headers['X-Accel-Buffering'] = 'no'
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Connection'] = 'keep-alive'
    return response

@app.route('/api/new_thread', methods=['POST'])
def new_thread():
    thread_id = str(uuid.uuid4())
    return jsonify({'thread_id': thread_id})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, threaded=True)