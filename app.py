# app.py
import streamlit as st
from services.granite_service import rewrite_text
from services.tts_service import synthesize_speech
from dotenv import load_dotenv
import os

load_dotenv()

st.title("EchoVerse 🎧")
st.sidebar.header("Settings")

# Text Input
text = st.sidebar.text_area("Paste text here") or None
uploaded = st.sidebar.file_uploader("Or upload .txt", type="txt")
if uploaded:
    text = uploaded.read().decode("utf-8")

# Tone Selection
tone = st.sidebar.selectbox("Select Tone", ["Neutral", "Suspenseful", "Inspiring"])

# Voice Selection
voice = st.sidebar.selectbox("Voice", ["Lisa", "Michael", "Allison", "My Voice"])

if st.sidebar.button("Generate Audiobook"):
    if not text:
        st.error("Please provide text input.")
    else:
        with st.spinner("Rewriting text..."):
            adapted = rewrite_text(text, tone)
        col1, col2 = st.columns(2)
        col1.subheader("Original Text")
        col1.write(text)
        col2.subheader(f"{tone} Text")
        col2.write(adapted)

        with st.spinner("Synthesizing speech..."):
            audio_bytes = synthesize_speech(adapted, voice)
        st.audio(audio_bytes, format="audio/mp3")
        st.download_button("Download MP3", data=audio_bytes, file_name="echoverse.mp3")
