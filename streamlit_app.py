import os
import streamlit as st
import json
from streamlit_float import *
import base64
from audio_recorder_streamlit import audio_recorder
from utils import get_answer, text_to_speech, speech_to_text, generate_identifier, is_json
from streamlit.components.v1 import html

st.set_page_config(page_title="🧑‍💻 Läxhälparen 💬", page_icon="", layout="centered", initial_sidebar_state="auto", menu_items=None)

float_init()

homework = {
  "Planeten Jupiter": [
      "Vad är Jupiter känd för att vara inom solsystemet? (Stor, ljus, med mera.)",
      "Kan du nämna någon av jupiters månar?",
      "Vad är den röda fläcken på Jupiter?"
  ],
  "Kejsare Caesar": [
      "Vad var Julius Caesars kända uttryck när han korsade floden Rubicon?",
      "Vad hette Julius Caesars adoptivson, som också blev kejsare?",
      "Vilket är den berömda romerska byggnaden som kallas för Julius Caesars sista viloplats?"
  ],
  "Ronja Rövardotter": [
      "Vad heter Ronjas rövarpappa?",
      "Var bor Ronja Rövardotter?",
      "Vilken sorts varelse är Birk i boken?"
  ]
}

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hej! Nu ska vi göra läxor ihop. Är du redo?"}
        ]
    if "ready_to_start" not in st.session_state:
        st.session_state["ready_to_start"] = False
    if "selected_topic" not in st.session_state:
        st.session_state["selected_topic"] = None
    if "question_index" not in st.session_state:
        st.session_state["question_index"] = 0
    if "correct_answer" not in st.session_state:
        st.session_state["correct_answer"] = False
    if "audio_base" not in st.session_state:
        st.session_state["audio_base"] = "welcome"

initialize_session_state() 

placeholder = st.empty()

def autoplay_audio(audio_file_name: str):
    file_path = f'audio/{audio_file_name}.mp3'
    st.session_state.audio_base = audio_file_name
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio id="{audio_file_name}" autoplay=true style="display: none;" >
              <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(
            md,
            unsafe_allow_html=True,)
    
autoplay_audio('welcome')

def next_question():
  if st.session_state.question_index <= 2:
    question = current_questions[st.session_state.question_index]
    audio_file_name = f'{generate_identifier(st.session_state.selected_topic)}_{st.session_state.question_index+1}'
    with st.chat_message("assistant"):
      st.write(question)
      st.session_state.messages.append({"role": "assistant", "content": question})
      autoplay_audio(audio_file_name)
  else:
    with st.chat_message("assistant"):
      st.write(question)
      st.session_state.messages.append({"role": "assistant", "content": "Bra jobbat, du har svarat på alla frågor."})
      autoplay_audio('finished_homework')


st.title("🧑‍💻 Läxhälparen 💬")

# Create footer container for the microphone
footer_container = st.container()
with footer_container:
    audio_bytes = audio_recorder(
        text="",
        recording_color="#e8b62c",
        neutral_color="#6aa36f",
        icon_name="microphone",
        icon_size="6x",
    )

# Float the footer container and provide CSS to target it with
footer_container.float("bottom: 0rem;")


with st.sidebar:
    if st.button(':page_facing_up: Ladda upp egen läxa',  use_container_width=True):
        st.write('När denna funktion är utvecklat kommer du komma ladda upp din egen läxa och AIn kommer skapa frågor till dig baserat på din årskurs.')
    if st.button(':camera: Fota matteläxa',  use_container_width=True):
        st.write('När denna funktion är utvecklat kommer du kunna ta bild på din matteläxa och få hjälp att lösa den.')

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Initialization
if not st.session_state["ready_to_start"]:
    placeholder = st.empty()
    button = placeholder.button('Jag är redo!')
    if button:
        placeholder.empty()
        st.session_state["ready_to_start"] = True
        st.session_state["audio_base"] = "ready_to_start"
        st.rerun()

if st.session_state["ready_to_start"] and not st.session_state.selected_topic:
    with st.chat_message("assistant"):
        st.write("Då kör vi! Tryck på mikrofonen när du vill svara.")
        st.write("Din förälder har angett följande läxa. Vad vill du börja med?")
        autoplay_audio('ready_to_start')
        option = st.selectbox(
        "   ",
        (homework.keys()),
        index=None,
        placeholder="Välj...",)
        if option:
          st.session_state.selected_topic = option
          st.session_state.question_index = 0  # Starta från första frågan

if st.session_state.selected_topic:
    current_questions = homework[st.session_state.selected_topic]
    if st.session_state.question_index < len(current_questions):
      next_question()

if audio_bytes:
    with st.spinner("...."):
        webm_file_path = "temp_audio.mp3"
        with open(webm_file_path, "wb") as f:
            f.write(audio_bytes)

        transcript = speech_to_text(webm_file_path)
        if transcript:
            st.session_state.messages.append({"role": "user", "content": transcript})
            with st.chat_message("user"):
                st.write(transcript)
            os.remove(webm_file_path)


if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Låt mig tänka🤔..."):
            chat_response = get_answer(st.session_state.messages)
            if is_json(chat_response):
              json_object = json.loads(chat_response)
              if "response" in json_object:
                  response = json_object["response"]
                  if "answer_status" in json_object and json_object["answer_status"] == "correct":
                      st.session_state.question_index= st.session_state.question_index + 1
                      st.session_state.correct_answer = True
              else:
                  response = "något verkar ha gått fel, prova igen."
            else:
              response = chat_response
        with st.spinner("..."):    
            audio_file_name = text_to_speech(response)
            if audio_file_name:
              autoplay_audio(audio_file_name)
        st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
    if st.session_state.correct_answer:
        st.session_state.correct_answer = False
        next_question()

