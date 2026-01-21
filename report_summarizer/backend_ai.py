"""
This is the API server that exposes endpoints to interact with different LLMs and prompts.
To run this in bash run
python app.py

Remember that this is only the api server. 
You need to start the client written in streamlit separately to interact with this server at port 8501
"""
from fastapi import FastAPI
from langchain_core.prompts import ChatPromptTemplate
#from langchain_openai import ChatOpenAI
from langserve import add_routes
import uvicorn
import os
from langchain_ollama import OllamaLLM

from dotenv import load_dotenv
load_dotenv()

#if os.getenv("OPENAI_API_KEY") is None:
#    print("OPENAI_API_KEY is not set")
if os.getenv("LANGCHAIN_API_KEY") is None:
    print("LANGCHAIN_API_KEY is not set")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGSMITH_PROJECT"] = "Tutorial3"

app = FastAPI(
    title="Langchain Server",
    version="1.0",
    description="A simple API server")

#openai_model = ChatOpenAI(model="gpt-3.5-turbo")
llm = OllamaLLM(model="llama3.2")

#prompt_essay = ChatPromptTemplate.from_template("Please write me an 20 word essay on {topic}")
prompt_summarize = ChatPromptTemplate.from_template("Can you please summarize the following paragraph: {paragraph}")

#add_routes(
#    app,
#    ChatOpenAI(model="gpt-3.5-turbo"),
#    path="/openai")

#add_routes(
#    app,
#    prompt_essay|openai_model,
#    path="/essay")

add_routes(
    app,
    prompt_summarize|llm,
    path="/summarize")

if __name__=="__main__":
    uvicorn.run(app,
                # To make the api only be visible from within the system at localhost or 127.0.0.1 use the following host
                #host="localhost",
                # 0.0.0.0 means open all ipv4 ips, LAN, localhost, VPN, docker and not just localhost
                host="0.0.0.0",
                # API listens only on the lan interfaces
                #host = "10.104.117.59",
                # To open to ipv6 use the following host
                # host = "::"
                port=8000)
