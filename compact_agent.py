# compact agent for langgraph deployment
from pydantic import BaseModel

from langchain_core.messages import AnyMessage
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import create_react_agent
from langchain_core.output_parsers import PydanticOutputParser
from langgraph.checkpoint.memory import InMemorySaver

from taf_main import llm, State
from tools import tools

checkpointer = InMemorySaver()

class AgResponse(BaseModel):    
    product_price_pairs: list[(str,str,float)]
    summary: str

parser = PydanticOutputParser(pydantic_object=AgResponse)

def prompt(state: State, config: RunnableConfig) -> list[AnyMessage]:
    system_msg = f"""
				 You are a business assistant that will help fill the user's 
				 needs by helping them shop on ebay. After deciding which products 
				 the user would like based on the human messages, save the 
                 {config["configurable"].get("n_final")} best 
				 products to results_output.txt using the 
				 save_text_to_file tool."""
    toadds = [{"role": "system", "content": system_msg}]
    return toadds + state["messages"]  

llm = llm.bind_tools(tools)
	
agent = create_react_agent(
	model = llm,
	tools = tools, 
	prompt = prompt, 
	output_parser = parser,
	checkpointer = checkpointer
)

"""
system_msg = f'''
				 You are a business assistant that will help fill the user's 
				 needs by helping them shop on ebay. After deciding which products 
				 would, save the top {config["configurable"].get("n_final")} best 
				 products to a text file using the 
				 save_text_to_file tool.
				 '''
    
    ai_msg =f'''
			0) Extract a list of products to shop for from the user's query
			1) Search for each product the user is looking for using the ebay_product_finder tool 
			2.1) If there are results, remember the results the ebay_product_finder tool returns 
			for future processing and skip step 2.2). 
			2.2) If there are no results, use the bad_results_tool
			3) Using the item summaries list, make a list of tuples containing a) the products'
			title, b) a url for the product, and c) the products' price
			
			'''
    
    toadds = []
    toadds.append({"role": "system", "content": system_msg})
    
    toadds.append({"role":"ai", "content":ai_msg})
    return toadds + state["messages"]
"""


