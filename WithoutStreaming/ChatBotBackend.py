from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from WithStreaming.exception import ChatBotWithLangGraphException
import sys
from WithStreaming.logger import logging
from dotenv import load_dotenv
load_dotenv()


class ChatBotWithoutStreaming:
    def __init__(self,repo_id,task):
        self.repo_id = repo_id
        self.task = task 

    def WorkflowFunction(self):
        logging.info("Workflow Function Started")
        logging.info("Taking DeepSeek LLM Model")
        try:
            llm = HuggingFaceEndpoint(
            repo_id= self.repo_id,
            task = self.task
            )
            model = ChatHuggingFace(llm=llm)
            logging.info("Taking DeepSeek LLM Model Done")
        except Exception as e:
            logging.error("Error inside loading LLM model",exc_info=True)
            raise ChatBotWithLangGraphException(e,sys)
        
        logging.info("Making ChatBot State")

        class ChatBotState(TypedDict):
            messages: Annotated[list[BaseMessage], add_messages]

        logging.info("ChatBot State Completed Successfully")

        def ChatFunction(state:ChatBotState) -> dict:
            logging.info("Chat Function Started")
            try:
                messages = state['messages']
                answer = model.invoke(messages)
                
                logging.info("Chat Function Completed Successfully")
                
                return {'messages':[answer]}
            except Exception as e:
                logging.error("Error inside Chat Function",exc_info=True)
                raise ChatBotWithLangGraphException(e,sys)
        
        logging.info("Making Workflow for ChatBot")            
        try:
            #graph 
            graph = StateGraph(ChatBotState)

            # nodes 
            graph.add_node('ChatFunction',ChatFunction)

            # edges 
            graph.add_edge(START,'ChatFunction')
            graph.add_edge('ChatFunction',END)

            # compile 
            checkpointer = InMemorySaver()
            workflow = graph.compile(checkpointer=checkpointer)
            logging.info("Making Workflow for ChatBot Done")
            return workflow
        except Exception as e:
            logging.error("Error inside Workflow for ChatBot",exc_info=True)
            raise ChatBotWithLangGraphException(e,sys)