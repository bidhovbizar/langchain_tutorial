"""
This is the client that runs streamlit app to interact with the deployed API server.
To run this in bash run 
streamlit run client.py

Remember that only if the api server is running this client will work.
I have written it using langserve run using uvicorn at port 8000.
"""
import requests
import streamlit as st

def get_openai_response(input_text):
    response = requests.post("http://10.104.117.59:8000/essay/invoke",
                             json={'input': {'topic': input_text}})
    return response.json()['output']['content']

def get_ollama_response(input_text):
    response = requests.post("http://10.104.117.59:8000/poem/invoke",
                             json={'input': {'topic': input_text}})
    return response.json()['output']

st.title("Essay or Peom")
if st.button("Clear All"):
    st.session_state.essay_output = None
    st.session_state.poem_output = None
    st.session_state.essay_input = ""
    st.session_state.poem_input = ""
    st.rerun()

input_essay = st.text_input("Please enter the topic for essay", key="essay_input")
input_poem = st.text_input("Please enter the topic for peom", key="poem_input")

if input_essay: 
    st.session_state.essay_output = get_openai_response(input_essay)
    #st.write(get_openai_response(input_essay))

if input_poem:
    st.session_state.poem_output = get_ollama_response(input_poem)
    #st.write(get_ollama_response(input_poem))

if st.session_state.get('essay_output'):
    st.write(st.session_state.essay_output)

if st.session_state.get('poem_output'):
    st.write(st.session_state.poem_output)
