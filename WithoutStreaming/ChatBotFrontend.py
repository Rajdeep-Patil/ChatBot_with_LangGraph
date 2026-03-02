import streamlit as st
from WithoutStreaming.ChatBotBackend import workflow

if 'messages' not in st.session_state:
    st.session_state['messages'] = []

for memory in st.session_state['messages']:
    with st.chat_message(memory['role']):
        st.text(memory['content'])
        
user_input = st.chat_input('Type here ')

if user_input:
    st.session_state['messages'].append({'role':'user','content':user_input})
    with st.chat_message('user'):
        st.text(user_input)
    
    config1 = {'configurable':{'thread_id':'thread_1'}}
    input_dict = {'messages':user_input}
    answer = workflow.invoke(input_dict,config1)['messages'][-1].content
    with st.chat_message('assistant'):
        st.text(answer)
    st.session_state['messages'].append({'role':'assistant','content':answer})        