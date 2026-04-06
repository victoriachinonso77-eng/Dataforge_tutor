# agents/voice.py
# Voice Narration Agent — reads lessons, quiz explanations and feedback aloud
# Uses OpenAI Text-to-Speech API (tts-1 model)
# Falls back gracefully if no API key is available

import os
import base64
import re


def clean_for_speech(text: str) -> str:
    """Strips markdown formatting so text sounds natural when spoken."""
    if not text:
        return ""
    text = re.sub(r'#{1,6}\s+', '', text)
    text = re.sub(r'\*{1,3}(.+?)\*{1,3}', r'\1', text)
    text = re.sub(r'`{1,3}[^`]*`{1,3}', '', text)
    text = re.sub(r'^\s*[-•]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'\|[^\n]+\|', '', text)
    text = re.sub(r'\n[-*_]{3,}\n', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'<[^>]+>', '', text)  # strip HTML tags
    return text.strip()


def text_to_speech(text: str, client, voice: str = "nova",
                   speed: float = 1.0) -> bytes | None:
    """
    Converts text to speech using OpenAI TTS API.
    voice options: alloy, echo, fable, onyx, nova, shimmer
    nova = warm and friendly (best for tutoring)
    Returns MP3 bytes or None if failed.
    """
    if not client or not text:
        return None
    try:
        clean_text = clean_for_speech(text)
        if not clean_text or len(clean_text) < 5:
            return None
        if len(clean_text) > 4000:
            clean_text = clean_text[:3900] + "... read the full lesson above."
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=clean_text,
            speed=speed,
        )
        return response.content
    except Exception as e:
        print(f"TTS error: {e}")
        return None


def get_audio_html(audio_bytes: bytes) -> str:
    """Returns an embedded HTML audio player for the given audio bytes."""
    if not audio_bytes:
        return ""
    b64 = base64.b64encode(audio_bytes).decode("utf-8")
    return f"""
    <audio controls style="width:100%;margin:8px 0;border-radius:8px;">
        <source src="data:audio/mpeg;base64,{b64}" type="audio/mpeg">
    </audio>
    """


def narrate_in_streamlit(text: str, client, st,
                          voice: str = "nova",
                          label: str = "Listen to this lesson") -> None:
    """
    Renders a narration button + voice selector + audio player in Streamlit.
    Caches audio in session_state so it only generates once per text.
    """
    if not client:
        return

    key = f"tts_{abs(hash(text[:100]))}"
    col1, col2 = st.columns([2, 3])
    with col1:
        narrate = st.button(f"🔊 {label}", key=key)
    with col2:
        voice_choice = st.selectbox(
            "Voice",
            options=["nova", "alloy", "echo", "fable", "onyx", "shimmer"],
            index=0,
            key=f"voice_{key}",
            label_visibility="collapsed"
        )
    if narrate:
        cache_key = f"audio_{key}_{voice_choice}"
        if cache_key not in st.session_state:
            with st.spinner("Generating audio..."):
                st.session_state[cache_key] = text_to_speech(
                    text, client, voice=voice_choice)
        audio = st.session_state.get(cache_key)
        if audio:
            st.markdown(get_audio_html(audio), unsafe_allow_html=True)
        else:
            st.warning("Audio generation failed. Check your OpenAI API key.")


# ── Predefined narration scripts ───────────────────────────────────────────
NARRATIONS = {
    "welcome": "Welcome to DataForge, your AI-powered Data Science Tutor. In this session you will learn the complete data science pipeline from start to finish. We will clean your data, analyse it, create visualisations, run machine learning models, and write a professional report. At every step I will explain exactly what is happening and why. Let's begin!",
    "cleaning_intro": "Step one is data cleaning. Real world data is almost never perfect. It usually contains missing values, duplicate rows, and unusual numbers called outliers. If we analyse dirty data our results will be wrong. That is why cleaning comes first. DataForge is about to fix every problem it finds in your dataset automatically.",
    "analysis_intro": "Step two is statistical analysis. Now that your data is clean we can start making sense of it. Statistics help us summarise large amounts of data in a few key numbers. We will look at averages, how spread out the data is, and which columns are related to each other. Pay close attention to the correlation findings as they often reveal the most interesting patterns.",
    "visualisation_intro": "Step three is data visualisation. Numbers alone are hard to understand. Charts reveal patterns instantly that would take hours to spot in a spreadsheet. Each chart DataForge creates was chosen specifically for your data type. I will explain what each one is showing you and what to look for.",
    "automl_intro": "Step four is machine learning. This is where we teach a computer to make predictions from your data. You will choose a column you want to predict, and DataForge will automatically test five different algorithms to find the best one. Don't worry if this feels complex. I will explain exactly what each model does and what the results mean.",
    "quiz_intro": "Time for a quick quiz! These questions are based on what DataForge just found in your actual data. Getting them wrong is fine, the explanation will make the concept clearer. Each correct answer earns you ten points.",
    "well_done": "Well done for completing this section! The resources below will help you go deeper into these concepts at your own pace. Videos and articles have been selected specifically for what you just learned.",
    "certificate": "Congratulations! You have completed the full DataForge Data Science Pipeline. You have demonstrated understanding of data cleaning, statistical analysis, data visualisation, and machine learning. Your certificate is ready to download.",
}

def get_narration(key: str) -> str:
    """Returns a predefined narration text by key."""
    return NARRATIONS.get(key, "")