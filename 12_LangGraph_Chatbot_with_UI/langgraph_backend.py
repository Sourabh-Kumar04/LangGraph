from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.messages import BaseMessage, HumanMessage
from typing import TypedDict, Annotated
from dotenv import load_dotenv
import operator
import os

load_dotenv()


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



checkpointer = MemorySaver()
graph = StateGraph(ChatState)

# add node
graph.add_node('chat_node', chat_node)
# add edges
graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

chatbot = graph.compile(checkpointer=checkpointer)

