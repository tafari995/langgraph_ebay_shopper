# a list of functions with wrappers to tool-ify them for langgraph agent use 
from langchain_community.tools import DuckDuckGoSearchRun   #, WikipediaQueryRun
#from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools import Tool
from datetime import datetime
from get_ebay_access_token import token_gen
from taf_main import State
import requests

def save_to_txt(data: str, filename: str = "results_output.txt"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_text = f"--- Results Output ---\nTimestamp: {timestamp}\n\n{data}\n\n"

    with open(filename, "a", encoding="utf-8") as f:
        f.write(formatted_text)
    
    return f"Data successfully saved to {filename}"
    
def ebay_search(keyword:str, num_results:int = 20, is_sandbox:bool = False):
    access_token = token_gen(is_sandbox)
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
    headers = {
        "Authorization": f"Bearer {access_token}", 
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_US", 
        "Content-Type": "application/json"
    }

    # Define the query parameters for your search
    params = {
        "q": keyword, # Search keyword
        "limit": num_results,             # Number of results to return
        "sort": "price",         # Sort by price (ascending)
        "filter": "buyingOptions:{FIXED_PRICE}" # Filter for "Buy It Now" listings
    }

    # data is a dictionary containing the itemSummaries list
    # each item in the itemSummaries list is a dictionary 
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        if "itemSummaries" in data:
            return data['itemSummaries']
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
    return data
    
def bad_result_aligner(state:State):
    state["r_counter"] = 2

#-----------------------------------------------Tools Below-----------------------------------------------------------

bad_results_tool = Tool(
    name="bad_product_results",
    func=bad_result_aligner,
    description="""
                Changes the counter variable in the state 
                to 2, in the case where the find_product_tool 
                returns no results
                """
)

save_tool = Tool(
    name="save_text_to_file",
    func=save_to_txt,
    description="Saves structured research data to a text file",
)

find_product_tool = Tool(
    name="ebay_product_finder",
    func=ebay_search,
    description="Searches the ebay site for products they sell"
)

search = DuckDuckGoSearchRun()
web_search_tool = Tool(
    name="search",
    func=search.run,
    description="Search the web for information",
)

tools = [save_tool, find_product_tool, web_search_tool, bad_results_tool]

#api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=100)
#wiki_tool = WikipediaQueryRun(api_wrapper=api_wrapper)

# Print the search results the request returned, if results exist
'''
if "itemSummaries" in data:
    print(f'\n {type(data)} \n ')
    print(f"\n {type(data['itemSummaries']) } \n ")
    for item in data["itemSummaries"]:
        print(f"Title: {item.get('title')}")
        print(f"Price: {item.get('price', {}).get('value')} {item.get('price', {}).get('currency')}")
        print(f"URL: {item.get('itemWebUrl')}")
        print("-" * 20)
else:
    print("No items found.")
'''
