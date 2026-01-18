"""
LANGCHAIN_API_KEY="-------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"
OPENAI_API_KEY="========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"
"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import streamlit as st
import os
from dotenv import load_dotenv
# By default load_dotenv loads the .env file by searching through its parent directories.
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
# For langsmith tracking
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = "Tutorial3"

# Prompt Template
prompt=ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistance. Please respond to the queries"),
        ("user", "Question:{question}")
    ]
)


# Streamlit framework

st.title("Langchain demo with OPEN_AI")
input_text=st.text_input("Search the topic you have in mind")

# OpenAI LLM
llm = ChatOpenAI(model="gpt-3.5-turbo")
output_parser=StrOutputParser()
chain = prompt | llm | output_parser

if input_text:
    st.write(chain.invoke({'question':input_text}))
