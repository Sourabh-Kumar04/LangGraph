import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage
import uuid

# --- Page Config ---
st.set_page_config(page_title="Raso Chatbot", page_icon="🤖", layout="wide")

# --- CSS Styling for Better UI ---
st.markdown("""
    <style>
        /* Sidebar Styling */
        .css-1d391kg, .css-1v3fvcr {  
            background-color: #f8f9fa !important;
        }
        .chat-title {
            font-size: 16px;
            font-weight: 600;
            padding: 6px 10px;
            margin-bottom: 4px;
            border-radius: 8px;
            cursor: pointer;
        }
        .chat-title:hover {
            background-color: #e9ecef;
        }
        /* Chat Bubbles */
        .stChatMessage.user {
            background-color: #e8f0fe !important;
            border-radius: 12px;
            padding: 10px;
        }
        .stChatMessage.assistant {
            background-color: #f1f3f4 !important;
            border-radius: 12px;
            padding: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if "chats" not in st.session_state:
    st.session_state["chats"] = {}  # {chat_id: {"title": str, "messages": []}}

if "current_chat" not in st.session_state:
    chat_id = str(uuid.uuid4())
    st.session_state["current_chat"] = chat_id
    st.session_state["chats"][chat_id] = {"title": "New Chat", "messages": []}

# --- Functions ---
def new_chat():
    chat_id = str(uuid.uuid4())
    st.session_state["current_chat"] = chat_id
    st.session_state["chats"][chat_id] = {"title": "New Chat", "messages": []}

# --- Sidebar ---
st.sidebar.title("💬 Your Chats")

if st.sidebar.button("🆕 Start New Chat", use_container_width=True):
    new_chat()

# List chats in sidebar
for chat_id, chat_data in st.session_state["chats"].items():
    if st.sidebar.button(chat_data["title"], key=chat_id, use_container_width=True):
        st.session_state["current_chat"] = chat_id

# --- Current Chat ---
chat_data = st.session_state["chats"][st.session_state["current_chat"]]
st.title("🤖 LangGraph Chatbot")

# Display messages with bubbles
for message in chat_data["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- User Input ---
user_input = st.chat_input("Message LangGraph...")

if user_input:
    # Save user message
    chat_data["messages"].append({"role": "user", "content": user_input})

    # Update chat title if first message
    if chat_data["title"] == "New Chat":
        chat_data["title"] = user_input[:30] + ("..." if len(user_input) > 30 else "")

    # Generate AI response
    config = {"configurable": {"thread_id": st.session_state["current_chat"]}}
    response = chatbot.invoke({"messages": [HumanMessage(content=user_input)]}, config=config)
    ai_message = response["messages"][-1].content

    # Save AI response
    chat_data["messages"].append({"role": "assistant", "content": ai_message})

    st.rerun() if hasattr(st, "rerun") else st.experimental_rerun()
