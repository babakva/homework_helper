from openai import OpenAI
import os
from dotenv import load_dotenv
import base64
import streamlit as st
from elevenlabs import generate, play, save, voices, Voice, VoiceSettings
from elevenlabs.api.error import UnauthenticatedRateLimitError, RateLimitError

load_dotenv()
openai_api_key = st.secrets["OPENAI_API_KEY"]
eleven_labs_api_key = st.secrets["ELEVEN_LABS_API_KEY"]

client = OpenAI(api_key=openai_api_key)

def get_answer(messages):
    system_message = [{"role": "system", "content": "Du är en läxhjälp assistent som ska hjälpa mitt barn med läxor. Din uppgift är att ställa frågor om ett specifikt ämne och sen hjälpa mitt barn att svara rätt genom att ge ledtrådar, frågorna får vara på nivån för en person som är 12 år."},
    {"role": "system", "content": "Du pratar bara svenska och ska absolut inte svara på andra språk. Om det är nåt du inte förstår ska du svara att du inte förstår och be användaren förtydliga."},
    {"role": "system", "content": "Kom ihåg att det är du som hittar på frågor om ämnet och användaren svarar."}]

    messages = system_message + messages
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages
    )
    return response.choices[0].message.content

def speech_to_text(audio_data):
    with open(audio_data, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            response_format="text",
            file=audio_file,
            language="sv"
        )
    return transcript

def text_to_speech(input_text):
    webm_file_path = "temp_audio_play.mp3"
    try:
        audio = generate(text=input_text, voice=Voice(
        voice_id='kOxuP8FgNUeapEbiIgBZ',
        settings=VoiceSettings(stability=0.8, similarity_boost=0.75, style=0.0, use_speaker_boost=True)),
        model='eleven_multilingual_v2', api_key=eleven_labs_api_key)
        play(audio)
    except UnauthenticatedRateLimitError:
        e = UnauthenticatedRateLimitError("Unauthenticated Rate Limit Error")
        print(e)
        st.exception(e)
    except RateLimitError:
        e = RateLimitError('Rate Limit')
        print(e)
        st.exception(e)

def handle_errors(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        # Log the error for debugging
        print(f"Error occurred: {e}")
        # Display a user-friendly error message
        st.error("Ett fel uppstod. Försök igen senare.")
        # Return a default value (optional)
        return None

def prepare_response(get_answer_func, user_input):
    with st.spinner("Låt mig tryänka..."):
        response = handle_errors(get_answer_func, st.session_state.messages, user_input)
    audio_file = None
    if response:
        with st.spinner("..."):
            audio_file = handle_errors(text_to_speech, response)
    return response, audio_file


def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode("utf-8")
    md = f"""
    <audio autoplay>
    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    st.markdown(md, unsafe_allow_html=True)