from langgraph.graph import StateGraph, START, END 
from langchain_groq import ChatGroq
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from logger import logging
from exception import ChatBotWithSidebarBackend
import sqlite3
import sys
from dotenv import load_dotenv
load_dotenv()

class ChatBot:
    def __init__(self, model_name):
        self.model_name = model_name 
    
    def WorkflowFunction(self):
        logging.info("Workflow Function Started")
        logging.info("Taking DeepSeek LLM Model")
        try:
            model = ChatGroq(model=self.model_name)
            logging.info("Taking Groq LLM Model Done")
        except Exception as e:
            logging.error("Error inside loading LLM model",exc_info=True)
            raise ChatBotWithSidebarBackend(e,sys)
        
        logging.info("Making ChatBot State")
        
        class ChatState(TypedDict):
            messages : Annotated[list[BaseMessage],add_messages]
            
        logging.info("ChatBot State Completed Successfully")
            
        def chat(state:ChatState) -> dict:
            logging.info("Chat Function Started")
            try:
                message = state['messages']
                result = model.invoke(message)
    
                logging.info("Chat Function Completed Successfully")
                
                return {'messages':[result]}
            except Exception as e:
                logging.error("Error inside Chat Function",exc_info=True)
                raise ChatBotWithSidebarBackend(e,sys)
            
        logging.info("Making Workflow for ChatBot")            
        try:
            logging.info("Building StateGraph...")
            graph = StateGraph(ChatState)
            
            graph.add_node('chat', chat)
            logging.info("Node 'chat' added successfully")
            
            graph.add_edge(START, 'chat')
            graph.add_edge('chat', END)
            logging.info("Edges added: START → chat → END")
            
            conn = sqlite3.connect('workflow.db', check_same_thread=False)
            logging.info("SQLite connection established: workflow.db")
            
            checkpointer = SqliteSaver(conn=conn)
            logging.info("SqliteSaver checkpointer initialized")
            
            workflow = graph.compile(checkpointer=checkpointer)
            logging.info("Workflow compiled successfully")

        except Exception as e:
            logging.error(f"Failed to build workflow: {e}")
            raise ChatBotWithSidebarBackend(e,sys)

        def retrieve_all_threads():
            logging.info("Retrieving all threads...")
            all_threads = []
            for checkpoint in checkpointer.list(None):
                thread_id = checkpoint.config['configurable']['thread_id']
                if thread_id not in all_threads:
                    all_threads.append(thread_id)
            logging.info(f"Total {len(all_threads)} threads found")
            return all_threads[::-1]

        return workflow, retrieve_all_threads