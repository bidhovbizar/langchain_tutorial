"""
LANGCHAIN_API_KEY="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"
OPENAI_API_KEY="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"
"""
#from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import OllamaLLM

import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

#os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
#os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
# For langsmith tracking
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGSMITH_PROJECT"] = "Tutorial3"
print("=" * 60)
print("LANGCHAIN_TRACING_V2:", os.getenv("LANGCHAIN_TRACING_V2"))
print("LANGCHAIN_PROJECT:", os.getenv("LANGCHAIN_PROJECT"))
print("LANGCHAIN_API_KEY exists:", bool(os.getenv("LANGCHAIN_API_KEY")))
print("=" * 60)
#print(os.getenv("LANGCHAIN_TRACING_V2"), os.getenv("LANGCHAIN_PROJECT"), os.getenv("LANGCHAIN_API_KEY"))


# Prompt Template
prompt=ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistance. Please respond to the queries"),
        ("user", "Question:{question}")
    ]
)


# Streamlit framework
st.title("Langchain demo with Ollama")
input_text=st.text_input("Search the topic you have in mind")

# Ollama LLAma2 LLM
llm = OllamaLLM(model="llama3.2")
output_parser=StrOutputParser()
chain = prompt | llm | output_parser

if input_text:
    print(f"Processing query: {input_text}")
    result = chain.invoke({'question':input_text})
    print(f"Got result, should create trace now")
    st.write(result)
