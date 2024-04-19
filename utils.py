from openai import OpenAI
import json
import streamlit as st
from elevenlabs import play, save, voices, Voice, VoiceSettings
from elevenlabs.client import ElevenLabs

openai_api_key = st.secrets["OPENAI_API_KEY"]
eleven_labs_api_key = st.secrets["ELEVEN_LABS_API_KEY"]

open_ai_client = OpenAI(api_key=openai_api_key)
eleven_labs_client = ElevenLabs(api_key=eleven_labs_api_key)

example_json = {
      "answer_status": "correct",
      "response": "Ditt svar är alldeles korrekt! Bra jobbat!"
}
example_json2 = {
      "answer_status": "incorrect",
      "response": "Inte helt rätt, vill du prova igen?"
}
def get_answer(messages):
    system_message = [{"role": "system", "content": "Du är en läxhjälp assistent som ska hjälpa med. Användaren kommer få en förinställd fråga som användaren svara på. Din uppgift är att rätta svaret."},
    {"role": "system", "content": "Du pratar bara svenska och ska absolut inte svara på andra språk och om användaren svarar fel ska du inte inkludera det rätta svaret i ditt svar. Om det är nåt du inte förstår ska du svara att du inte förstår och be användaren förtydliga."},
    {"role": "system", "content": "Du ska alltid svara i JSON format. I JSON objektet skall det finnas två fält, answer_status som kan vara correct eller incorrect, samt fältet response där du lägger in en kommentar om svaret."},
    {"role": "system", "content": "Här är ett exempel på ditt svar: " + json.dumps(example_json)},
    {"role": "system", "content": "Här är ett till exempel på ditt svar: " + json.dumps(example_json2)} ]

    messages = system_message + messages
    response = open_ai_client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        response_format={"type": "json_object"},
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
    audio_file_name = 'temp_response'
    response_audio_path = f'audio/{audio_file_name}.mp3'
    audio = eleven_labs_client.generate(text=input_text, voice=Voice(
        voice_id='kOxuP8FgNUeapEbiIgBZ',
        settings=VoiceSettings(stability=0.8, similarity_boost=0.75, style=0.0, use_speaker_boost=True)),
        model='eleven_multilingual_v2')
    save(audio, response_audio_path)
    return(audio_file_name)


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

def generate_identifier(selected_topic):
    topic_prefix = {
        "Planeten Jupiter": "jupiter",
        "Kejsare Caesar": "caesar",
        "Ronja Rövardotter": "ronja"
    }
    prefix = topic_prefix.get(selected_topic, "unknown_")
    return prefix

def is_json(string):
    try:
        json_object = json.loads(string)
    except ValueError as e:
        return False
    return True