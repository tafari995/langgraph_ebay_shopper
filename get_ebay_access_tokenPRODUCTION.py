
import requests
from dotenv import load_dotenv
import os
import base64

def token_gen(is_sandbox:bool = False):
    load_dotenv()
    appid, certid = (os.getenv('APPID'),os.getenv('CERTID'))
    credentials = f"{appid}:{certid}"
    # Prepare security authorization url
    url = "https://api.ebay.com/identity/v1/oauth2/token"
    # Prepare credentials
    EBAY_APP_ID = appid		
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


