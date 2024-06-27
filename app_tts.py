import os
import streamlit as st
from streamlit_float import float_css_helper
from dotenv import load_dotenv
from openai import OpenAI
from langchain_core.messages import HumanMessage, AIMessage
from datetime import datetime
from prompts import *
from typing import IO
from io import BytesIO
from elevenlabs import play, stream, save, VoiceSettings
from elevenlabs.client import ElevenLabs
import pygame
from resemble import Resemble


# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
resemble_api_key = os.getenv("RESEMBLE_API_KEY")
if not api_key:
    st.error("API Key not found! Please check your environment variables.")
elevenlabs_voice_id = "Trnt4s21CP7D2iOQdTx2"
elevenlabs_url = "https://api.elevenlabs.io/v1/voices"

client = OpenAI(api_key=api_key)

# Avatar URLs
user_avatar_url = "https://api.dicebear.com/8.x/pixel-art/svg?seed=Jasmine&beardProbability=0&clothing=variant01&clothingColor=ffd969&eyesColor=876658&glassesColor=191919,323232&hair=short04&hairColor=28150a&skinColor=b68655"

specialist_id_caption = {
  "Sunny's Assistant": {
    "assistant_id": "asst_IdOC7jNX9BdemhoOZqd0kmZ7",
    "caption": "role is multifaceted, encompassing elements of an assistant, AI journal, therapist, friend, and counselor.",
    "avatar": "https://www.shareicon.net/data/256x256/2016/01/06/234337_optimus_256x256.png"
  },
  "Mindfulness Teacher": {
    "assistant_id": "asst_bnFm27eqedaYK9Ulekh8Yjd9",
    "caption": "Goes Deep",
    "avatar": "https://cdn.pixabay.com/photo/2013/07/12/19/30/enlightenment-154910_1280.png"
  }
}

def generate_audio(text):
    # Short endpoint: /stream
    # - Up to 1000 characters
    # - Synchronous, instant response (0.3s+)
    # - Streams back raw audio data

    import requests
    import io

    response = requests.post(
    'https://api.v6.unrealspeech.com/stream',
    headers = {
        'Authorization' : 'Bearer oHO1XRGvHNdtEe6IuWzLb3zdOLx0p65a1XNoaCqGEfC0CYrp4TXXu4'
    },
    json = {
        'Text': text, # Up to 1000 characters
        'VoiceId': 'Will', # Dan, Will, Scarlett, Liv, Amy
        'Bitrate': '64k', # 320k, 256k, 192k, ...
        'Speed': '0', # -1.0 to 1.0
        'Pitch': '0.92', # -0.5 to 1.5
        'Codec': 'libmp3lame', # libmp3lame or pcm_mulaw
    }
    )

    # Create a file-like object from the response content
    audio_data = io.BytesIO(response.content)

    # Initialize Pygame mixer
    pygame.mixer.init()

    # Load the audio data into Pygame mixer
    pygame.mixer.music.load(audio_data)

    # Play the audio
    pygame.mixer.music.play()

    # Wait until the audio finishes playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    # Cleanup
    pygame.mixer.quit()
    _ = """client = ElevenLabs(api_key=elevenlabs_api_key)
    def text_to_speech_stream(text: str) -> IO[bytes]:
        # Perform the text-to-speech conversion
        response = client.text_to_speech.convert(
            voice_id=elevenlabs_voice_id, # Adam pre-made voice
            optimize_streaming_latency="0",
            output_format="mp3_22050_32",
            text=text,
            model_id="eleven_multilingual_v2",
            voice_settings=VoiceSettings(
                stability=0.0,
                similarity_boost=1.0,
                style=0.0,
                use_speaker_boost=True,
            ),
        )

        # Create a BytesIO object to hold the audio data in memory
        audio_stream = BytesIO()

        # Write each chunk of audio data to the stream
        for chunk in response:
            if chunk:
                audio_stream.write(chunk)

        # Reset stream position to the beginning
        audio_stream.seek(0)

        # Return the stream for further use
        print(f"Type of text: {type(audio_stream)}")
        return audio_stream
    
    # Get the audio stream
    audio_stream = text_to_speech_stream(text)

    # Play the audio stream using PyAudio
    play(audio_stream)
"""

def initialize_session_state():
    primary_specialist = list(specialist_id_caption.keys())[0]
    primary_specialist_id = specialist_id_caption[primary_specialist]["assistant_id"]
    primary_specialist_avatar = specialist_id_caption[primary_specialist]["avatar"]
    state_keys_defaults = {
        "chat_history": [],
        "user_question": "",
        "json_data": {},
        "critical_actions": {},
        "sidebar_state": 1,
        "assistant_response": "",
        "specialist_input": "",
        "specialist": primary_specialist,
        "assistant_id": primary_specialist_id,
        "specialist_avatar": primary_specialist_avatar,
        "assistant_response": "",
        "should_rerun": False       
    }
    for key, default in state_keys_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default

def display_header():
    st.set_page_config(page_title="OP", page_icon="🤖")
    specialist = st.session_state.specialist
    specialist_avatar = specialist_id_caption[st.session_state.specialist]["avatar"]
    st.markdown(
            f"""
            <div style="text-align: center;">
                <h1>
                    <img src="{specialist_avatar}" alt="Avatar" style="width:60px;height:60px;border-radius:50%;">
                    Optimus Prime
                </h1>
            </div>
            """, 
            unsafe_allow_html=True
        )

def generate_response_stream(stream):
    for response in stream:
        if response.event == 'thread.message.delta':
            for delta in response.data.delta.content:
                if delta.type == 'text':
                    yield delta.text.value


def get_response(user_question):
    client.beta.threads.messages.create(thread_id=st.session_state.thread_id, role="user", content=user_question)

    response_placeholder = st.empty()  # Placeholder for streaming response text
    response_text = ""  # To accumulate response text

    # Stream response from the assistant
    with client.beta.threads.runs.stream(thread_id=st.session_state.thread_id, assistant_id=st.session_state.assistant_id) as stream:
        for chunk in stream:
            if chunk.event == 'thread.message.delta':  # Check if it is the delta message
                for delta in chunk.data.delta.content:
                    if delta.type == 'text':
                        response_text += delta.text.value  # Append new text fragment to response text
                        response_placeholder.markdown(response_text)  # Update the placeholder with new response text as markdown

    return response_text

def display_chat_history():    
    for message in st.session_state.chat_history:
        if isinstance(message, HumanMessage):
            avatar_url = message.avatar
            with st.chat_message("user", avatar=user_avatar_url):                
                st.markdown(message.content, unsafe_allow_html=True)
        else:
            avatar_url = st.session_state.specialist_avatar
            with st.chat_message("AI", avatar=avatar_url):
                st.markdown(message.content, unsafe_allow_html=True)


def user_input():
    input_container = st.container()
    input_container.float(float_css_helper(bottom="50px"))
    with input_container:
        col1, col2 = st.columns([4, 1])  # Adjust column widths for better appearance
        with col1:
            user_question = st.chat_input("How may I help you?")
        with col2:
            submit_button1 = st.button("Upload History")
            submit_button2 = st.button("Voice")
            on = st.toggle("Activate feature")

            if on:
                if st.session_state.assistant_response:
                    text= st.session_state.assistant_response
                    generate_audio(text)
        if submit_button1:
            upload_history()
        if submit_button2:
            text= st.session_state.assistant_response
            #generate_audio(text)
    if user_question is not None and user_question != "":
        st.session_state.chat_history.append(HumanMessage(user_question, avatar=user_avatar_url))

        with st.chat_message("user", avatar=user_avatar_url):
            st.markdown(user_question)
        
        with st.chat_message("AI", avatar=st.session_state.specialist_avatar):
            assistant_response = get_response(user_question)
        st.session_state.assistant_response = assistant_response
        st.session_state.chat_history.append(AIMessage(assistant_response, avatar=st.session_state.specialist_avatar))
        generate_audio(assistant_response)

def upload_history():
    
    # pull thread necessary?
    #thread = client.beta.threads.retrieve(st.session_state.thread_id)
    # extract chat_history from thread
    all_messages = []
    limit = 100  # Maximum allowed limit per request 
    after = None

    while True:
        response = client.beta.threads.messages.list(thread_id=st.session_state.thread_id, limit=limit, after=after)
        messages = response.data
        if not messages:
            break
        all_messages.extend(messages)
        after = messages[-1].id      # Set the 'after' cursor to the ID of the last message
    # Reverse the messages to chronological order
    all_messages.reverse()
    # save to a list of dictionary
    extracted_messages = []
    for message in all_messages:
        # Initialize a dictionary for each message
        message_dict = {
            'role': message.role,
            'text': ''
        }

        message_content = message.content
        if isinstance(message_content, list):
            text_parts = [block.text.value for block in message_content if hasattr(block, 'text')]
            text = ' '.join(text_parts)
            message_dict['text'] = text
        
        extracted_messages.append(message_dict)
        # Now `extracted_messages` is a list of dictionaries containing the role and text of each message.
    # Convert the list of dictionaries to a plain text format
    plain_text = ""
    for msg in extracted_messages:
        plain_text += f"{msg['role']}: {msg['text']}\n"

    # Summarize chat history (plain_text)  
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": summary_prompt + plain_text,
            }
        ],
        model="gpt-3.5-turbo",
        temperature=0.5
    )
    summary = response.choices[0].message.content
    # print chat summary
    print("\nSummary compression:")
    print(summary)
    print(f'Size decrease: {(len(summary))/(len(plain_text))}')
    # update Global instructions of assistant with timestamp
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # extract assistant instructions
    assistant_info=client.beta.assistants.retrieve(assistant_id=st.session_state.assistant_id)
    assistant_instructions = assistant_info.instructions
    # upload new assistant instructions
    new_instructions = assistant_instructions + '\n' + current_time + '\n' + summary
    client.beta.assistants.update(assistant_id=st.session_state.assistant_id,instructions=new_instructions)

def main():
    if "thread_id" not in st.session_state:
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id
        
    initialize_session_state()
    display_header()
    display_chat_history()
    user_input()
    print(st.session_state.thread_id)


if __name__ == '__main__':
    main()