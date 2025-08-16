import streamlit as st
import yt_dlp as youtube_dl
from moviepy.editor import VideoFileClip
import whisper
import os
import glob
from langdetect import detect, DetectorFactory
from deep_translator import GoogleTranslator

DetectorFactory.seed = 0  # for consistent language detection

# Function to clear previous files
def clear_previous_files():
    file_types = ['*.mp3', '*.txt', '*.mp4']
    for file_type in file_types:
        files = glob.glob(file_type)
        for f in files:
            os.remove(f)

# Function to download the YouTube video
def download_video(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.mp4',
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return "video.mp4"

# Function to extract audio
def extract_audio(video_path, audio_path):
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)
    return audio_path

# Transcribe using Whisper
def transcribe_audio(audio_path, model_name="base"):
    try:
        model = whisper.load_model(model_name)
    except Exception as e:
        st.error(f"Error loading Whisper model: {e}")
        return None
    result = model.transcribe(audio_path)
    transcription_path = "transcription.txt"
    with open(transcription_path, "w") as f:
        f.write(result["text"])
    return transcription_path, result["text"]

# Remove audio
def remove_audio_from_video(video_path):
    video = VideoFileClip(video_path)
    video_no_audio = video.without_audio()
    video_no_audio_path = "video_without_audio.mp4"
    video_no_audio.write_videofile(video_no_audio_path)
    return video_no_audio_path

# Detect language of text
def detect_language(text):
    try:
        lang = detect(text)
        return lang
    except:
        return "unknown"

# Translate text
def translate_text(text, target_lang):
    try:
        translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
        return translated
    except Exception as e:
        st.error(f"Translation failed: {e}")
        return None

# Streamlit UI
st.title("🎬 YouTube Video Processing App + 🌐 Translation")
st.markdown("**Please comply with YouTube's terms and conditions. Do not misuse this tool.**")

video_url = st.text_input("📥 Enter YouTube video URL:")
target_language = st.selectbox("🌍 Choose language to translate transcription (optional):", 
                               ["None", "en", "es", "fr", "de", "zh", "hi", "ar", "ru", "ja", "pt"])

if st.button("🚀 Process Video"):
    clear_previous_files()

    with st.spinner("📦 Downloading video..."):
        video_path = download_video(video_url)
    st.success("✅ Video downloaded!")

    with st.spinner("🎧 Extracting audio..."):
        audio_path = extract_audio(video_path, "original_audio.mp3")
    st.success("✅ Audio extracted!")

    with st.spinner("📝 Transcribing audio..."):
        transcription_path, transcription_text = transcribe_audio(audio_path)
        if transcription_path:
            st.success("✅ Transcription completed!")

            # Detect language
            detected_lang = detect_language(transcription_text)
            st.markdown(f"🧭 Detected transcription language: **{detected_lang}**")

            st.subheader("📄 Transcription")
            st.text_area("Original Transcription", transcription_text, height=200)

            # Translate if requested
            if target_language != "None":
                with st.spinner("🔄 Translating transcription..."):
                    translated = translate_text(transcription_text, target_language)
                    if translated:
                        st.subheader(f"🌐 Translated Transcription ({target_language})")
                        st.text_area("Translated Text", translated, height=200)

        else:
            st.error("❌ Failed to transcribe audio.")

    with st.spinner("🔇 Removing audio from video..."):
        video_no_audio_path = remove_audio_from_video(video_path)
    st.success("✅ Audio removed!")

    st.subheader("🎥 Original Video:")
    st.video(video_path)

    st.subheader("🔊 Original Audio:")
    st.audio(audio_path, format='audio/mp3')

    st.subheader("🎞️ Video without Audio:")
    st.video(video_no_audio_path)

    st.download_button("⬇️ Download Original Video", open(video_path, "rb"), "video.mp4", "video/mp4")
    st.download_button("⬇️ Download Original Audio", open(audio_path, "rb"), "original_audio.mp3", "audio/mp3")

    if transcription_path:
        st.download_button("⬇️ Download Transcription", open(transcription_path, "rb"), "transcription.txt", "text/plain")
    st.download_button("⬇️ Download Video without Audio", open(video_no_audio_path, "rb"), "video_without_audio.mp4", "video/mp4")
