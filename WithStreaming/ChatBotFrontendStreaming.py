import streamlit as st 
from langchain_core.messages import HumanMessage
from WithStreaming.ChatBotBackendStreaming import ChatBotWithStreaming

backend_object = ChatBotWithStreaming('deepseek-ai/DeepSeek-R1','text-generation')
workflow = backend_object.WorkflowFunction()

if 'messages' not in st.session_state:
    st.session_state['messages'] = []
    
for message in st.session_state['messages']:
    with st.chat_message(message['role']):
        st.text(message['content'])
        
user_input = st.chat_input('Ask me anything ')

if user_input:
    st.session_state['messages'].append({'role':'user','content':user_input})
    with st.chat_message('user'):
        st.text(user_input)
    
    config2 = {'configurable':{'thread_id':'thread_2'}}
    input_dict = {'messages':[HumanMessage(content=user_input)]}
    
    with st.chat_message('assistant'):
        ai_message = st.write_stream(message_chunk.content for message_chunk, metadata in workflow.stream(input_dict,config=config2,stream_mode='messages')
                                    if message_chunk.content is not None)
    st.session_state['messages'].append({'role':'assistant','content':ai_message})