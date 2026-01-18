from fastapi import FastAPI
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langserve import add_routes
import uvicorn
import os
from langchain_ollama import OllamaLLM

from dotenv import load_dotenv
load_dotenv()

if os.getenv("OPENAI_API_KEY") is None:
    print("OPENAI_API_KEY is not set")
if os.getenv("LANGCHAIN_API_KEY") is None:
    print("LANGCHAIN_API_KEY is not set")
os.environ["LANGCHAIN_TRACING_V2"] = "true"

app = FastAPI(
    title="Langchain Server",
    version="1.0",
    description="A simple API server"
)

add_routes(
    app,
    ChatOpenAI(model="gpt-3.5-turbo"),
    path="/openai")

model = ChatOpenAI(model="gpt-3.5-turbo")
llm = OllamaLLM(model="llama3.2")

prompt1 = ChatPromptTemplate.from_template("Please write me an 20 word essay on {topic}")
prompt2 = ChatPromptTemplate.from_template("Please write me a 4 line poem on {topic}")

add_routes(
        app,
        prompt1|model,
        path="/essay")

add_routes(
        app,
        prompt2|llm,
        path="/poem")

if __name__=="__main__":
    uvicorn.run(app,
                host="localhost",
                port=8000)
