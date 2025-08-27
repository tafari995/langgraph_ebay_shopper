
from pydantic import BaseModel
from typing import Dict, Union, Any
from taf_main import config

class WorkflowRequest(BaseModel):
    input_data: Dict[str, Any]
    config: Dict[str, Any] 

def generate_traversal_one():
    global config
    products = input(
        '''
        \n
        Which products are you looking for today?
        \n
        '''
    )   
    state = {"messages":[{"role":"human", "content": products}], "r_counter": 0} 
    wfr = WorkflowRequest(input_data = state, config = config)
    return wfr
    
def generate_traversal_two():
    global config
    sentiments = input(
        '''
        \n 
        ~ what are your top priorities and preferences in 
        the products you are looking for today? ~ 
        \n
        '''
    )
    return sentiments
    
    
