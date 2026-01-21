import json
import os
import requests
from dotenv import load_dotenv
load_dotenv(override=True)

os.environ['BRIDGE_API_APP_KEY']="egai-prd-networking-123120833-summarize-1768589443863"
os.environ['AZURE_OPENAI_API_KEY']="eyJraWQiOiI5NGU4cmxzTzUyUmhoc1RfWDNVMkRvb1lFS2xRTzZlaFRaM3NVajBVUXpnIiwiYWxnIjoiUlMyNTYifQ.eyJ2ZXIiOjEsImp0aSI6IkFULkdHamNoVDBPWUFBWGZVYl9PLUhHdDIweFV0eC1wOWZmTmNtUTlaSWR3V28iLCJpc3MiOiJodHRwczovL2lkLmNpc2NvLmNvbS9vYXV0aDIvZGVmYXVsdCIsImF1ZCI6ImFwaTovL2RlZmF1bHQiLCJpYXQiOjE3Njg5OTI2NTMsImV4cCI6MTc2ODk5NjI1MywiY2lkIjoiMG9hc2lqdGh0MEtKdzk5ZFc1ZDciLCJzY3AiOlsiY3VzdG9tc2NvcGUiXSwic3ViIjoiMG9hc2lqdGh0MEtKdzk5ZFc1ZDciLCJhenAiOiIwb2FzaWp0aHQwS0p3OTlkVzVkNyJ9.ihG-fYi1ec5g-DVNge8zeNThvB2IIGExaKl2NEMuMAbfTAwkXSeQF8_oFoyJ21aTQR4awEu_08iSEQ8hjDrL4H4GdKcinM3lHBNW4C2eNGYRXVl2rccVl9SaG1F_CDcLcGnp-2nnF-Or3CMNhBmHDDtpWW1vPE9w8JLHwyzVNLJcgmiJrbETKtvrveeqYZGWfZWJ6tJmAuYgTjK7O2FghZPO2jTXPoQE4sdZ9AMrrbaUS6NWn72zLZCz297cJ3-RMIiH9IBqdiLTyJlS-q3re4IIJuIqPwmTpODGVjzlhtNHnupogJ5ETA2OAoAlpKTbRzyyVEIieYuWMVcIn_fA3g"
APPKEY = os.getenv("BRIDGE_API_APP_KEY") # This is the app-key from CircuIT which is passed as user in the payload
api_key = os.getenv("AZURE_OPENAI_API_KEY") # This is the access_token

MODEL_NAME = "gpt-4.1"
API_URL = f"https://chat-ai.cisco.com/openai/deployments/{MODEL_NAME}/chat/completions"   # api-version is optional

def chat_with_circuit():
    print("Cisco CircuIT GPT Chatbot (type 'exit' to quit)")
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    headers = {
       'Content-Type': 'application/json',
       'api-key': api_key
    }

    while True:
        user_input = input("You: ")
        if user_input.lower() in {"exit", "quit"}:
            break

        messages.append({"role": "user", "content": user_input})

        payload = {
            "user": json.dumps({"appkey": APPKEY}),
            # "user": f'{{"appkey": "{APPKEY}"}}',  # this works also
            "messages": messages
        }

        try:
            response = requests.post(API_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            reply = data["choices"][0]["message"]["content"]
            messages.append({"role": "assistant", "content": reply})
            print("AI:", reply.strip())

        except requests.exceptions.HTTPError as e:
            print("API request error:", e)
            print("Status code:", e.response.status_code)
            print("Response content:", e.response.text)

        except requests.exceptions.RequestException as e:
            print("API request error:", e)
            break
        except (KeyError, IndexError) as e:
            print("Unexpected response format:", e)
            break

if __name__ == "__main__":
    chat_with_circuit()

