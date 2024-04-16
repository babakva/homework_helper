import os
import streamlit as st
from streamlit_float import *
import base64
from audio_recorder_streamlit import audio_recorder
from utils import get_answer, text_to_speech, autoplay_audio, speech_to_text

st.set_page_config(page_title="🧑‍💻 Läxhjälpsbotten 💬", page_icon="", layout="centered", initial_sidebar_state="auto", menu_items=None)

float_init()

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hej! Nu ska vi göra läxor ihop. Är du redo?"}
        ]
    if "ready_to_start" not in st.session_state:
        st.session_state["ready_to_start"] = False
    if "selected_topic" not in st.session_state:
        st.session_state["selected_topic"] = None

initialize_session_state()

st.title("🧑‍💻 Läxhjälpsbotten 💬")

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
        st.write('Denna funktion är under utveckling.')
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
        st.session_state.messages.append({"role": "assistant", "content": "Då kör vi igång! Tryck på mikrofonen för att prata."})
        st.session_state["ready_to_start"] = True
        st.rerun()

if st.session_state["ready_to_start"] and not st.session_state.selected_topic:
    with st.chat_message("assistant"):
        st.write("Din förälder har angett följande läxa. Vad vill du börja med?")
        option = st.selectbox(
        "",
        ("Planeten Jupiter", "Kejsare Cesar", "Ronja Rövardotter"),
        index=None,
        placeholder="Välj...",)
        if option:
            st.session_state.messages.append({"role": "user", "content": f"Jag vill lära mig mer om '{option}'."})
            st.session_state.selected_topic = option



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
            final_response = get_answer(st.session_state.messages)
        with st.spinner("..."):    
            audio_file = text_to_speech(final_response)
        st.write(final_response)
        st.session_state.messages.append({"role": "assistant", "content": final_response})
