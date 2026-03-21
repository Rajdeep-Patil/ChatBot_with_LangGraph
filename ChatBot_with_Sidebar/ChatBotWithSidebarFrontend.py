import streamlit as st
from ChatBotWithSidebarBackend import ChatBot
from langchain_core.messages import HumanMessage
import uuid

#------------------------------------------- * -----------------------------------------

def new_conversations():
    return str(uuid.uuid4())

def reset_chat():
    thread_id = new_conversations()
    st.session_state['thread_id'] = thread_id
    st.session_state['thread_dict'][thread_id] = ''
    st.session_state['message_history'] = []
    st.session_state['thread_id_list'].append(thread_id)

def load_conversation(thread_id):
    return workflow.get_state(config = {'configurable':{'thread_id':str(thread_id)}}).values['messages']

#------------------------------------------- * -----------------------------------------

if 'workflow' not in st.session_state:
    object = ChatBot('llama-3.3-70b-versatile')
    st.session_state.workflow, st.session_state.retrieve_all_threads = object.WorkflowFunction()
workflow = st.session_state.workflow
retrieve_all_threads = st.session_state.retrieve_all_threads

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []
    
if 'thread_id_list' not in st.session_state:
    st.session_state['thread_id_list'] = []
    
if 'thread_dict' not in st.session_state:
    st.session_state['thread_dict'] = {}
    for tid in list(retrieve_all_threads()):
        state = workflow.get_state(config={'configurable': {'thread_id': tid}})
        messages = state.values.get('messages', [])
        name = messages[0].content[:30] if messages else 'New Chat'
        st.session_state['thread_dict'][tid] = name
        if tid not in st.session_state['thread_id_list']:
            st.session_state['thread_id_list'].append(tid)
    
if 'thread_id' not in st.session_state:
    thread = new_conversations()
    st.session_state['thread_id'] = thread
    st.session_state['thread_id_list'].append(thread)
    st.session_state['thread_dict'][thread] = ''
    
#------------------------------------------- * -----------------------------------------

st.sidebar.title('Chat With Rajdeep')

if st.sidebar.button('New Chat'):
    reset_chat()
    
st.sidebar.header('My Conversations')
    
#------------------------------------------- * -----------------------------------------

for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

for thread_id, thread_name in list(st.session_state['thread_dict'].items())[::-1]:
    thread_name = st.session_state['thread_dict'].get(thread_id, '')
    if not thread_name:          
        continue
    if st.sidebar.button(thread_name, use_container_width=True):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)
        temp_messages = []
        st.session_state['message_history'] = [
            {'role':'user' if isinstance(msg, HumanMessage) else 'ai', 'content':msg.content} for msg in messages
        ]
        st.rerun()
        
#------------------------------------------- * -----------------------------------------

user_input = st.chat_input("Ask here :")

if user_input:
    current_thread = st.session_state['thread_id']
    if st.session_state['thread_dict'][current_thread] == '':
        st.session_state['thread_dict'][current_thread] = user_input[:30]
    
    
    st.session_state['message_history'].append({'role':'user', 'content':user_input})
    with st.chat_message('user'):
        st.text(user_input)
    
    input_dict = {'messages':[HumanMessage(content = user_input)]}
    config = {'configurable':{'thread_id':st.session_state['thread_id']}}
    with st.chat_message('ai'):
        ai_message = st.write_stream(
        message_chunk.content for message_chunk, metadata in workflow.stream(
            input_dict,config=config,stream_mode='messages'))
        
    st.session_state['message_history'].append({'role':'ai', 'content':ai_message})