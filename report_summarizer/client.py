"""
This is the client that runs streamlit app to interact with the deployed API server.
To run this in bash run 
streamlit run client.py

Remember that only if the api server is running this client will work.
I have written it using langserve run using uvicorn at port 8000.
"""
import requests
import streamlit as st

#def get_openai_response(input_text):
#    response = requests.post("http://10.104.117.59:8000/essay/invoke",
#                             json={'input': {'topic': input_text}})
#    return response.json()['output']['content']

def get_ollama_response(input_text):
    response = requests.post("http://10.104.117.59:8000/summarize/invoke",
                             json={'input': {'paragraph': input_text}})
    return response.json()['output']

st.title("Summarize the run report")
if st.button("Clear All"):
    st.session_state.summarize_output = None
    st.session_state.sumamrize_input = ""
    st.rerun()

input_summarize = st.text_input("Enter the URL for the run report", key="poem_input")

if input_summarize:
    st.session_state.summarize_output= get_ollama_response(input_summarize)
    #st.write(get_ollama_response(input_poem))

if st.session_state.get('summarize_output'):
    st.write(st.session_state.summarize_output)
