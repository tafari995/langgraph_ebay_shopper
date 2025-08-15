import requests
import json
import base64

def token_gen(is_sandbox:bool = False):
	# Load json config with security details 
	config_file = 'ebay-config-sample.json'
	with open(config_file,'r') as f:
		credentials = json.load(f)

	production_creds = credentials["api.ebay.com"]	
	sandbox_creds = credentials["api.sandbox.ebay.com"]
	# Prepare security authorization url
	url = "https://api.ebay.com/identity/v1/oauth2/token"
	if is_sandbox:
		url = "https://api.sandbox.ebay.com/identity/v1/oauth2/token"

	# Prepare credentials
	if is_sandbox:
		credentials = f"{sandbox_creds['appid']}:{sandbox_creds['certid']}"
		EBAY_APP_ID = sandbox_creds['appid']
	else:
		credentials = f"{production_creds['appid']}:{production_creds['certid']}"
		EBAY_APP_ID = production_creds['appid']
		
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

#token_gen(is_sandbox = False)
