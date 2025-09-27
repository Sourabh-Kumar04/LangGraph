from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.messages import BaseMessage, HumanMessage
from typing import TypedDict, Annotated
from dotenv import load_dotenv
import operator
import os
import sqlite3

load_dotenv()

os.environ['LANGCHAIN_PROJECT'] = 'Raso Chat'

llm = HuggingFaceEndpoint(
    repo_id="openai/gpt-oss-20b",
    task="task-generation",
    huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN")
)
llm = ChatHuggingFace(llm=llm)


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def chat_node(state: ChatState):
    # taske user query from state 
    message = state['messages']
    # send to llm
    response = llm.invoke(message)
    # response store 
    return {'messages': [response]}

# Initialize SQLite checkpointer
conn = sqlite3.connect(database="RasoChat_db.db", check_same_thread=False)
checkpointer = SqliteSaver(conn)

graph = StateGraph(ChatState)

# add node
graph.add_node('chat_node', chat_node)
# add edges
graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

chatbot = graph.compile(checkpointer=checkpointer)

# for message_chunk, metadata in chatbot.stream(
#     {"messages": [HumanMessage(content="HI")]},
#     config={"configurable": {"thread_id": "1"}},
#     stream_mode="messages"
# ):
#     if message_chunk.content:
#         print(message_chunk.content, end=" ", flush=True)

def retrieve_all_threads():

    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])

    return list(all_threads)