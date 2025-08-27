from fastapi import FastAPI, HTTPException
from langgraph.types import Command
import asyncio
from uuid import uuid4
from graph_deQwen import graph
from bg_app_manager import *

app = FastAPI()
active_threads = {}

@app.get("/")
def home():
    return {"content":"welcome to the home page!"}


# Interactive workflow with human-in-the-loop
@app.get("/start-agent/")
async def start_interactive_workflow():
    """
    Start an interactive workflow that may require human input.
    Returns immediately with a thread_id for subsequent interactions.
    """
    request = generate_traversal_one()
    thread_id = request.config['configurable']['thread_id'] or str(uuid4())
    
    # Store the initial request
    active_threads[thread_id] = {
        "status": "running",
        "input_data": request.input_data,
        "config": request.config or {},
        "awaiting_input": False,
        "current_step": None
    }
    
    # Start the workflow in the background
    asyncio.create_task(run_interactive_workflow(thread_id, request))
    
    return {"thread_id": thread_id, "status": "started"}

async def run_interactive_workflow(thread_id: str, request: WorkflowRequest):
    """Background task to run the interactive workflow."""
    try:
        config = request.config or {}
        config["configurable"] = config.get("configurable", {})
        config["configurable"]["thread_id"] = thread_id
        
        active_threads[thread_id]["current_step"] = "processing"
        async for event in graph.astream(
            request.input_data, 
            config,
            stream_mode="updates"
            ):
                print(event)
        
        # Simulate needing human input
        active_threads[thread_id]["awaiting_input"] = True
        active_threads[thread_id]["current_step"] = "awaiting_user_decision"
        
        
    except Exception as e:
        active_threads[thread_id]["status"] = "error"
        active_threads[thread_id]["error"] = str(e)

@app.get("/status/{thread_id}")
async def get_workflow_status(thread_id: str):
    """Get the current status of a workflow thread."""
    if thread_id not in active_threads:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    return active_threads[thread_id]

@app.get("/continue/{thread_id}")
async def continue_workflow(thread_id: str):
    """Continue an interactive workflow with user input."""
    user_input = {"sentiments":generate_traversal_two()}
    if thread_id not in active_threads:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    thread_data = active_threads[thread_id]
    
    if not thread_data.get("awaiting_input"):
        raise HTTPException(status_code=400, detail="Workflow not awaiting input")
    
    # Update the thread with user input and continue
    thread_data["awaiting_input"] = False
    thread_data["user_input"] = user_input
    
    async for event in graph.astream(
            Command(resume=user_input), 
            config,
            stream_mode="updates"
            ):
                print(event)
    
    # Continue the workflow (this would involve updating the graph state)
    # For demonstration:
    thread_data["status"] = "completed"
    thread_data["result"] = f"Workflow completed with user input: {user_input}"
    
    return {"status": "completed", "thread_id": thread_id}

"""
@app.put("/agent", response_model=ChatOutput)
def processor():
	products = ChatInput(
        message = input(
        '''
        Which products are you looking for today?
        '''
        )
	)
	state = {
		"messages":[{"role":"human", "content": products}], 
		"r_counter": 0
	}

	result_state = graph.invoke(
		state,    
		config    
	)

	sentiments = input(
		'''
		\n 
		~ what are your top priorities and preferences in 
		the products you are looking for today? ~ 
		\n
		'''
	)

	result_state_dos = graph.invoke(
		Command(resume = {"sentiments": sentiments } ),
		config
	)


	return ChatOutput(response="success :D")
"""
