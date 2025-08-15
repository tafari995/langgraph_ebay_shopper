# the main langgraph script to run the agent
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.types import interrupt, Command

from taf_main import State, has_reasoned
from tools import tools
from compact_agent import agent, checkpointer

# for debugging
from langchain.globals import set_debug
set_debug(True)

def should_continue(state: State):
    if state["r_counter"]>1:
        return END
    else:
        return "tools"

def check_after_tools(state):
    messages = state["messages"]
    last_message = messages[-1]    
    # If the last message is a tool response from ending_tool
    if (hasattr(last_message, 'name') and 
        last_message.name == 'save_text_to_file'):
        return "end"    
    return "continue"


def agent_reasoner(state: State): 
    ai_msg =f'''
        0) Extract a list of products to shop for from the user's query
        1) Search for each product the user is looking for using the ebay_product_finder tool 
        2.1) If there are results, remember the results the ebay_product_finder tool returns 
        for future processing and skip step 2.2). 
        2.2) If there are no results, use the bad_results_tool
        3) Using the item summaries list, make a list of tuples containing a) the products'
        title, b) a url for the product, and c) the products' price'''
    state["messages"].append({"role":"ai", "content":ai_msg})
    state["messages"] = (agent.invoke(state))["messages"]
    has_reasoned(state)	
    return state
    
def agent_reasoner_two(state: State):
    assert state["r_counter"] > 0
    interruptor_sentis = interrupt(
        {
        "query": "collecting desired product vibes from user"
        }
    )
    state["messages"].append({"role":"human", "content": interruptor_sentis["sentiments"]})
    additional_ai_msg = f''' \n
        4) Using the item summaries list and user sentiments together, reason about which 
        products might best suit the user
        5) Return the top {config["configurable"].get("n_final")} items from your 
        reasoning in step 4. You may return between 1 and {config["configurable"].get("n_final")}
        items if step 4 returned fewer than {config["configurable"].get("n_final")} items
        6) Save the items in step 5 to results_output.txt using save_text_to_file
        7) Please check over your work, and be sure that you carefully followed the 
        directions in the system prompt. This is the final step.'''
    state["messages"].append({"role":"ai", "content": additional_ai_msg})
    state["messages"] = (agent.invoke(state))["messages"]
    has_reasoned(state)	
    return state

tool_node = ToolNode(tools=tools)

graph_builder = StateGraph(State)

# The first argument is the unique node name
# The second argument is the function or object that will be called whenever
# the node is used.
graph_builder.add_node("tools", tool_node)
graph_builder.add_node("reasoner", agent_reasoner)
graph_builder.add_node("second_reasoner", agent_reasoner_two)

graph_builder.add_edge(START, "reasoner")
graph_builder.add_edge("reasoner", "tools")
graph_builder.add_edge("tools","second_reasoner")

graph_builder.add_conditional_edges(
    "second_reasoner",
    should_continue,
)

graph_builder.add_conditional_edges(
    "tools",
    check_after_tools,
    {
        "continue": "second_reasoner",
        "end": END
    }
)

graph = graph_builder.compile(checkpointer=checkpointer)

config = {"configurable" : {"thread_id": "1", "n_final": 5}}

products = input(
	"""
	Which products are you looking for today?
	"""
)
state = {"messages":[{"role":"human", "content": products}], "r_counter": 0}

result_state = graph.invoke(
    state,    
	config    
)

sentiments = input(
    """
    \n 
    ~ what are your top priorities and preferences in 
    the products you are looking for today? ~ 
    \n
    """
)

result_state_dos = graph.invoke(
    Command(resume = {"sentiments": sentiments } ),
    config
)





"""
additonal_ai_msg = f'''
	4) Using the item summaries list, reason about which product might best suit the user
	and return the top {config["configurable"].get("n_final")} 
	5) Please check over your work, and be sure that you carefully followed the 
	directions in the system prompt.
'''
"""
"""
sentiments = input(
	'''
	Which qualities do you value most in each product
	you listed (in response to the first query)?
	'''
)

end_state = graph.invoke(
	{"messages":[
	{"role":"human", "content": sentiments},
	{"role":"ai", "content": additonal_ai_msg}
	],
    "reasoned": state["reasoned"]
	},
	config
)



config = {"configurable": {"thread_id": "1", "n_final": 5}}
"""

"""
if state["r_counter"] == 1:
        interruptor_sentis = interrupt(
            {
            "query": "collecting desired product vibes from user"
            }
        )
        state["messages"].append({"role":"human", "content": interruptor_sentis["sentiments"]})
        
        additional_ai_msg = f'''
            4) Using the item summaries list, reason about which product might best suit the user
            and return the top {config["configurable"].get("n_final")} 
            5) Please check over your work, and be sure that you carefully followed the 
            directions in the system prompt.'''
        state["messages"].append({"role":"ai", "content": additional_ai_msg})
"""
