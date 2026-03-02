import sys 
from WithStreaming.logger import logging

class ChatBotWithLangGraphException(Exception):
    def __init__(self,exception_error,error_detail:sys):
        self.exception_error = exception_error
        _,_,exc_info = error_detail.exc_info()
        
        self.lineno=exc_info.tb_lineno
        self.file_name=exc_info.tb_frame.f_code.co_filename
        
    def __str__(self):
        return f"Error occured in python script name [{self.file_name}] line number [{self.lineno}] error message [{self.exception_error}]"