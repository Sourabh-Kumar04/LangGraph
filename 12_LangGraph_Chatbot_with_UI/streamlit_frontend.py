import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import  HumanMessage

# st.session_state -> dict 
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

# message_history = []

# load the conversation hiostory
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

# {'role': 'user', 'content': "hi"}
# {'role': 'assistant','content': "test"}

user_input = st.chat_input("Type here")

if user_input:
    # first append the message to message_history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    # first append the message to message_history
    thread_id = '1'
    config = {'configurable': {'thread_id': thread_id}}
    response = chatbot.invoke({'messages': [HumanMessage(content=user_input)]}, config=config)
    ai_message = response['messages'][-1].content
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
    with st.chat_message('assistant'):
        st.text(ai_message)