from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from exception import ChatBotWithLangGraphException
import sys
from logger import logging
from dotenv import load_dotenv
load_dotenv()


class ChatBotWithStreaming:
    def __init__(self,repo_id,task):
        self.repo_id = repo_id
        self.task = task 

    def WorkflowFunction(self):
        logging.info("Workflow Function Started")
        logging.info("Taking DeepSeek LLM Model")
        llm = HuggingFaceEndpoint(
        repo_id= self.repo_id,
        task = self.task
        )
        model = ChatHuggingFace(llm=llm)
        logging.info("Taking DeepSeek LLM Model Done")
    
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
        
# backend_object = ChatBotWithStreaming('deepseek-ai/DeepSeek-R1','text-generation')
# workflow = backend_object.WorkflowFunction()

# config2 = {'configurable':{'thread_id':'thread_2'}}
# while True:
#     input_ = input('you : ')
#     user_input = {'messages':[HumanMessage(content=input_)]}
#     if input_.strip().lower() in ['exit','bye']:
#         break
#     for messages_chunk, metadata in  workflow.stream(user_input,config=config2,stream_mode='messages'):
#         if messages_chunk.content is not None:
#             print(messages_chunk.content, end="", flush=True)
#     print('\n')