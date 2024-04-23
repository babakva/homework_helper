import streamlit as st
import time
import numpy as np
import pandas as pd
import random

st.set_page_config(page_title="Förälderadmin")

with st.sidebar:
  st.page_link('streamlit_app.py', label='Läxor')
  st.page_link('pages/parent.py', label='Förälderadmin')
  st.divider()
st.write(
    """Här kan du se hur det går för ditt barn."""
)
st.header('Den här veckans läxor', divider='rainbow')
df = pd.DataFrame(
    {
        "homework": ["Planeten Jupiter", "Ronja Rövardotter", "Kejsare Caesar"],
        "progress": [random.randint(0, 100) for _ in range(3)],
        "time_per_question": [random.randint(0, 10) for _ in range(3)],
        "activity": [[random.randint(0, 500) for _ in range(30)] for _ in range(3)],
    }
)
st.dataframe(
    df,
    column_config={
        "homework": "App name",
        "progress": st.column_config.ProgressColumn(
            "Läxstatus",
            help="Ant    al rätta svar",
            format="%f%%",
            min_value=0,
            max_value=100,
        ),
        "time_per_question": st.column_config.NumberColumn(
            "Genomsnitt svarstid (m)",
            help="Tid det tar att svara på en fråga i snitt",
            min_value=0,
            max_value=10,
            step=1,
            format="%d",
        ),
        "activity": st.column_config.LineChartColumn(
            "Aktivitet (senaste 30 dagar)", y_min=0, y_max=500
        ),
    },
    hide_index=True,
)
st.header('Ditt barns kursplaner', divider='rainbow')
df2 = pd.DataFrame(
    {
        "name": ["Svenska", "Matematik", "Biologi"],
        "url": ["https://www.skolverket.se/undervisning/grundskolan/laroplan-och-kursplaner-for-grundskolan/laroplan-lgr22-for-grundskolan-samt-for-forskoleklassen-och-fritidshemmet?url=907561864%2Fcompulsorycw%2Fjsp%2Fsubject.htm%3FsubjectCode%3DGRGRSVE01%26tos%3Dgr&sv.url=12.5dfee44715d35a5cdfa219f",
         "https://www.skolverket.se/undervisning/grundskolan/laroplan-och-kursplaner-for-grundskolan/laroplan-lgr22-for-grundskolan-samt-for-forskoleklassen-och-fritidshemmet?url=907561864%2Fcompulsorycw%2Fjsp%2Fsubject.htm%3FsubjectCode%3DGRGRMAT01%26tos%3Dgr&sv.url=12.5dfee44715d35a5cdfa219f",
          "https://www.skolverket.se/undervisning/grundskolan/laroplan-och-kursplaner-for-grundskolan/laroplan-lgr22-for-grundskolan-samt-for-forskoleklassen-och-fritidshemmet?url=907561864%2Fcompulsorycw%2Fjsp%2Fsubject.htm%3FsubjectCode%3DGRGRBIO01%26tos%3Dgr&sv.url=12.5dfee44715d35a5cdfa219f"],
        "grade": [random.choice(['A', 'B', 'C', 'D', 'E']) for _ in range(3)],
        "next_exam": [random.randint(0, 30) for _ in range(3)],
    }
)
st.dataframe(
    df2,
    column_config={
        "name": "Kurs",
        "grade": st.column_config.TextColumn(
            "Betyg",
            help="Nuvarande betyg",
        ),
        "url": st.column_config.LinkColumn("Länk", display_text="Gå till kursplanen"),
        "next_exam": st.column_config.NumberColumn(
            "Nästa prov",
            help="Nästa prov",
            format="Om %d dagar",
        ),

    },
    hide_index=True,
)


options = ["Lägg till läxor", "Se vad barnet har svarat", "Rekommendationer för ditt barn"]
option = st.selectbox(
   "Vad skulle du vilja göra",
   (options),
   index=None,
   placeholder="Välj ett...",
)
if option:
	option_index = options.index(option)
	if option_index == 0:
	    st.write('När denna funktion är utvecklat kommer du komma ladda upp din läxor till ditt barn.')
	if option_index == 1:
	    st.write('När denna funktion är utvecklat kommer du komma kunna se vad ditt barn har svarat.')
	if option_index == 2:
	    st.write('När denna funktion är utvecklat kommer du komma kunna få rekommendationer för att öka eller sänka läxhastigheten.')