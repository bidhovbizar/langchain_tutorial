'''
OPENAI_API_VERSION=??
AZURE_OPENAI_API_VERSION="access token"
AZURE_OPENAI_ENDPOINT="https://chat-ai.cisco.com/"
'''

import os
import requests
import json
from langchain_openai import AzureChatOpenAI
import traceback

# Please reach out for clientid,clientsecret
import base64

import dotenv
dotenv.load_dotenv()
#os.environ['LANGSMITH_API_KEY'] = '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'
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGSMITH_PROJECT"] = "Tutorial3"

client_id = ''
client_secret = ''
# print(base64.b64encode(f'{client_id}:{client_secret}'.encode('utf-8')).decode('utf-8'))

url = "https://id.cisco.com/oauth2/default/v1/token"

payload = "grant_type=client_credentials"
value = base64.b64encode(f'{client_id}:{client_secret}'.encode('utf-8')).decode('utf-8')
headers = {
    "Accept": "*/*",
    "Content-Type": "application/x-www-form-urlencoded",
    "Authorization": f"Basic {value}"
}

#token_response = requests.request("POST", url, headers=headers, data=payload)
token_response = "eyJraWQiOiI5NGU4cmxzTzUyUmhoc1RfWDNVMkRvb1lFS2xRTzZlaFRaM3NVajBVUXpnIiwiYWxnIjoiUlMyNTYifQ.eyJ2ZXIiOjEsImp0aSI6IkFULmdaeThCLWY1bkJ5VEVXLV9LbXY1ajdYUmk0SUFMbXFzVWR4Z0ZvdnFKU1UiLCJpc3MiOiJodHRwczovL2lkLmNpc2NvLmNvbS9vYXV0aDIvZGVmYXVsdCIsImF1ZCI6ImFwaTovL2RlZmF1bHQiLCJpYXQiOjE3Njg5OTY1MDUsImV4cCI6MTc2OTAwMDEwNSwiY2lkIjoiMG9hc2lqdGh0MEtKdzk5ZFc1ZDciLCJzY3AiOlsiY3VzdG9tc2NvcGUiXSwic3ViIjoiMG9hc2lqdGh0MEtKdzk5ZFc1ZDciLCJhenAiOiIwb2FzaWp0aHQwS0p3OTlkVzVkNyJ9.JxUg1NmNpj6RbWuNSjbLciL2Wp_WiaGhxHk8D7cwiu73LrN7Qpjv2eMbxsegUK-0T-Fm_ON75bR8fSRzPMHuFvFw0APnyDo8uQCxzdcLQaFIZP7XQwY-J5AfXK1sJViV-NZRO_cMlwRje4YOsKUQXS6z-ww19hDuikgX4CdpKko4NG3ocmyB5xThmFxvJ99xTTbLm_O22h2E7Xe-n3-4lTlxDK6ZJlm7vT1CFGfdVmiZzN4YjW8n0XA2XhuPoOWPekZKhR94aKBG7-gWdOvjhNDRo2W9Vo6rYPNoWjAXRSJuDushGYB9wZRNwRzcPgcHgmzq8r-71G65q7MILaQGLA"

# print(token_response.text)

CISCO_OPENAI_APP_KEY = 'egai-prd-networking-123120833-summarize-1768589443863'
# your used id
CISCO_BRAIN_USER_ID = 'bbizar'

llm = AzureChatOpenAI(deployment_name="gpt-4.1",
                      azure_endpoint='https://chat-ai.cisco.com',
                      #api_key=token_response.json()["access_token"],
                      api_key=token_response,
                      api_version="2023-08-01-preview",
                      model_kwargs=dict(user=f'{{"appkey": "{CISCO_OPENAI_APP_KEY}", "user": "{CISCO_BRAIN_USER_ID}"}}'))

from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

messages = [
    SystemMessage(content="You are a helpful assistant"),
    HumanMessage(content="I love information.")
]

response = llm.invoke([HumanMessage(content='What is volcano?')])
print(response.content)
#print(json.dumps(response.response_metadata, indent=2, sort_keys=True))
print(json.dumps(response.response_metadata))
print(response.id)
print(response.usage_metadata)

