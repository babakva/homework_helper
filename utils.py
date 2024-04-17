from openai import OpenAI
import os
import base64
import streamlit as st
from elevenlabs import play, save, voices, Voice, VoiceSettings
from elevenlabs.client import ElevenLabs

openai_api_key = st.secrets["OPENAI_API_KEY"]
eleven_labs_api_key = st.secrets["ELEVEN_LABS_API_KEY"]

open_ai_client = OpenAI(api_key=openai_api_key)
eleven_labs_client = ElevenLabs(api_key=eleven_labs_api_key)

def get_answer(messages):
    system_message = [{"role": "system", "content": "Du är en läxhjälp assistent som ska hjälpa mitt barn med läxor. Din uppgift är att ställa frågor om ett specifikt ämne och sen hjälpa mitt barn att svara rätt genom att ge ledtrådar, frågorna får vara på nivån för en person som är 12 år."},
    {"role": "system", "content": "Du pratar bara svenska och ska absolut inte svara på andra språk. Om det är nåt du inte förstår ska du svara att du inte förstår och be användaren förtydliga."},
    {"role": "system", "content": "Kom ihåg att det är du som hittar på frågor om ämnet och användaren svarar."}]

    messages = system_message + messages
    response = open_ai_client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages
    )
    return response.choices[0].message.content

def speech_to_text(audio_data):
    with open(audio_data, "rb") as audio_file:
        transcript = open_ai_client.audio.transcriptions.create(
            model="whisper-1",
            response_format="text",
            file=audio_file,
            language="sv"
        )
    return transcript

def text_to_speech(input_text):
    response_audio_path = 'temp_response.mp3'
    audio = eleven_labs_client.generate(text=input_text, voice=Voice(
        voice_id='kOxuP8FgNUeapEbiIgBZ',
        settings=VoiceSettings(stability=0.8, similarity_boost=0.75, style=0.0, use_speaker_boost=True)),
        model='eleven_multilingual_v2')
    save(audio, response_audio_path)
    return(response_audio_path)


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