from WithoutStreaming.ChatBotBackend import ChatBotWithoutStreaming
from WithStreaming.ChatBotBackendStreaming import ChatBotWithStreaming
from WithStreaming.logger import logging
from WithStreaming.exception import ChatBotWithLangGraphException
import sys


logging.info("Calling Workflow of ChatBotWithStreaming")
try:
    backend_object = ChatBotWithoutStreaming('deepseek-ai/DeepSeek-R1','text-generation')
    workflow = backend_object.WorkflowFunction()
    print(workflow)
except Exception as e:
    logging.error("Error inside Calling Workflow of ChatBotWithStreaming",exc_info=True)
    raise ChatBotWithLangGraphException(e,sys)
logging.info("Calling Workflow of ChatBotWithStreaming Completed Successfully")


logging.info("Calling Workflow of ChatBotWithStreaming")
try:
    backend_object = ChatBotWithStreaming('deepseek-ai/DeepSeek-R1','text-generation')
    workflow = backend_object.WorkflowFunction()
    print(workflow)
except Exception as e:
    logging.error("Error inside Calling Workflow of ChatBotWithStreaming",exc_info=True)
    raise ChatBotWithLangGraphException(e,sys)
logging.info("Calling Workflow of ChatBotWithStreaming Completed Successfully")
