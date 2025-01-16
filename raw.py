#

"""#####################--------------3 -----------------------"""


import streamlit as st
import pyaudio
import wave
import speech_recognition as sr
from gtts import gTTS
import requests
from bs4 import BeautifulSoup
import json
import time

# Function to get the Bearer Token
def get_key():
    url = "Your_url_Endpoint"
    USERNAME = "your_username"
    PASSWORD = "password"
    
    if not USERNAME or not PASSWORD:
        raise ValueError("Username or password environment variables not set.")
    
    auth = (USERNAME, PASSWORD)
    
    try:
        response = requests.get(url, verify=False, auth=auth)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            page_text = soup.get_text()
        else:
            st.error(f"Request failed with status code: {response.status_code}")
    except Exception as e:
        st.error(f"An error occurred: {e}")
    
    return "Bearer " + response.text

# Function to interact with the LLM endpoint
def chat_completion(prompt):
    try:
        api_endpoint_url = "your_endpoint_url"
        payload = {
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 1,
            "max_tokens": 4096,
            "n": 1,
            "model": "llama3-70b",
            "stream": False
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": get_key()
        }
        response = requests.post(api_endpoint_url, json=payload, headers=headers, verify=False)
        if response.status_code == 200:
            return response.json(), 200
        else:
            st.error(f"Error response from API: {response.text}")
            return None, response.status_code
    except Exception as e:
        st.error(f"Exception in /chat endpoint: {str(e)}")
        return None, 500

# Function to record audio
def record_audio():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Say something...")
        audio_data = recognizer.listen(source)
    
    try:
        spoken_text = recognizer.recognize_google(audio_data)
        return spoken_text
    except sr.UnknownValueError:
        st.error("Google Speech Recognition could not understand audio")
        return None
    except sr.RequestError:
        st.error("Could not request results from Google Speech Recognition")
        return None

# Function to create audio response
def create_audio_response(text):
    tts = gTTS(text=text, lang='en')
    audio_file_path = "response_audio.mp3"
    tts.save(audio_file_path)
    return audio_file_path

# Streamlit interface
st.title("Speech to Text and Text to Speech with GPT")

if 'recording' not in st.session_state:
    st.session_state.recording = False

if st.button("Start/Stop Recording"):
    st.session_state.recording = not st.session_state.recording
    if st.session_state.recording:
        spoken_text = record_audio()
        if spoken_text:
            st.write(f"Recorded Text: {spoken_text}")
            prompt = "Keep the response short and crisp. User Query: " + spoken_text
            response, status_code = chat_completion(prompt)
            if response:
                response_text = response['choices'][0]['message']['content']
                st.subheader("Model Response")
                st.text_area("", response_text, height=200)
                audio_file_path = create_audio_response(response_text)
                audio_file = open(audio_file_path, 'rb')
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format='audio/mp3')
                st.audio(audio_file_path, format='audio/mp3', start_time=0)
    else:
        st.write("Recording stopped.")

# Text input for prompt
prompt_input = st.text_input("Enter a prompt:")
if st.button("Get Response"):
    if prompt_input:
        prompt = "Keep the response short and crisp. User Query: " + prompt_input
        response, status_code = chat_completion(prompt)
        if response:
            response_text = response['choices'][0]['message']['content']
            st.subheader("Model Response")
            st.text_area("", response_text, height=200)
            audio_file_path = create_audio_response(response_text)
            audio_file = open(audio_file_path, 'rb')
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format='audio/mp3')
            