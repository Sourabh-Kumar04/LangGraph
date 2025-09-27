import streamlit as st
from langgraph_tools_backend import chatbot, retrieve_all_threads
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
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
    raw_chats = retrieve_all_threads()
    st.session_state["chats"] = {
        str(chat_id): {"title": "New Chat", "messages": []}
        for chat_id in raw_chats
    } if isinstance(raw_chats, list) else raw_chats

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

for chat_id, chat_data in st.session_state["chats"].items():
    if st.sidebar.button(chat_data["title"], key=chat_id, use_container_width=True):
        st.session_state["current_chat"] = chat_id

# --- Current Chat ---
chat_data = st.session_state["chats"][st.session_state["current_chat"]]
st.title("🤖 Raso LangGraph Chatbot")

for message in chat_data["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- User Input ---
user_input = st.chat_input("Message LangGraph...")

if user_input:
    # Save user message
    chat_data["messages"].append({"role": "user", "content": user_input})

    if chat_data["title"] == "New Chat":
        chat_data["title"] = user_input[:30] + ("..." if len(user_input) > 30 else "")

    CONFIG = {
        "configurable": {"thread_id": st.session_state["current_chat"]},
        "metadata": {"thread_id": st.session_state["current_chat"]},
        "run_name": "chat_turn_with_threads"
    }

    # Stream assistant response with tool feedback
    with st.chat_message("assistant"):
        tool_status = {"box": None}  # holder for status

        def stream_response():
            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages",
            ):
                # 🔧 If tool is running, update status box
                if isinstance(message_chunk, ToolMessage):
                    tool_name = getattr(message_chunk, "name", "tool")
                    if tool_status["box"] is None:
                        tool_status["box"] = st.status(f"🔧 Using `{tool_name}` …", expanded=True)
                    else:
                        tool_status["box"].update(
                            label=f"🔧 Using `{tool_name}` …",
                            state="running",
                            expanded=True
                        )

                # ✅ AI output streaming
                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content

        ai_message = st.write_stream(stream_response())

        # ✅ finalize tool status if used
        if tool_status["box"] is not None:
            tool_status["box"].update(
                label="✅ Tool finished",
                state="complete",
                expanded=False
            )

    chat_data["messages"].append({"role": "assistant", "content": ai_message})

    st.rerun() if hasattr(st, "rerun") else st.experimental_rerun()