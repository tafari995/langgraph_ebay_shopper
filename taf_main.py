# a script containing the langgraph llm, defining the agent state, 
# and state updating functions which are not tools
import operator
from dotenv import load_dotenv
from typing import Annotated
from typing_extensions import TypedDict
#from langchain_ollama import ChatOllama
from langchain_anthropic import ChatAnthropic
from langchain_community.cache import SQLiteCache
from langchain.globals import set_llm_cache

load_dotenv()

class State(TypedDict):
    messages: Annotated[list, operator.add]
    r_counter:int = 0
    
def has_reasoned(state:State) -> State:
	state["r_counter"] +=1
	return state
	
set_llm_cache(SQLiteCache(database_path=".langchain.db"))
    
llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
#llm = ChatOllama(model="qwen3:8b", temperature=0.05)

