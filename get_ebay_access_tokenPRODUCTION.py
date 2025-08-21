
import requests
from dotenv import load_dotenv
import os
import base64

load_dotenv()

def token_gen(is_sandbox:bool = False):
    credentials = {"appid":os.getenv("APPID"), "certid":os.getenv("CERTID")}
    	
	# Prepare security authorization url
	url = "https://api.ebay.com/identity/v1/oauth2/token"
	
	# Prepare credentials
	cred_string = f"{credentials['appid']}:{credentials['certid']}"
	EBAY_APP_ID = credentials['appid']		
	credentials_b64 = base64.b64encode(credentials.encode()).decode()
	headers = {
		'Content-Type': 'application/x-www-form-urlencoded',
		'Authorization': f'Basic {credentials_b64}'
	}
	data = {
		'grant_type': 'client_credentials',
		'scope': 'https://api.ebay.com/oauth/api_scope'
	}
	response = requests.post(url, headers=headers, data=data)
	if response.status_code == 200:
		access_token = response.json()['access_token']
		print("niiiice :D")
	else:
		raise Exception(f"Failed to get access token: {response.text}")
	return access_token


