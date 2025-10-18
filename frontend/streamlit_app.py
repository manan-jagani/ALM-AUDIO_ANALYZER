import streamlit as st
import requests
import os
import time
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# Load .env
load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Audio Analyzer", layout="wide")

# Sidebar
st.sidebar.title("Audio Analyzer Controls")
dark_mode = st.sidebar.checkbox("🌙 Dark Mode", value=True)
if dark_mode:
    st.markdown(
        """<style>
        .stApp { background-color: #0e1117; color: #fafafa; }
        div[data-testid="stSidebar"] { background-color: #111; }
        </style>""",
        unsafe_allow_html=True
    )

st.title("🎧 Audio Language Model — Real-time Audio Analysis")

# Columns layout
col1, col2 = st.columns([1.2, 2])

with col1:
    st.header("1️⃣ Upload Audio File")
    uploaded = st.file_uploader("Upload WAV / MP3 / M4A", type=["wav", "mp3", "m4a"])
    
    if uploaded:
        st.markdown(f"**Filename:** {uploaded.name}")
        max_mb = int(os.getenv("MAX_UPLOAD_MB", "50"))
        if uploaded.size > max_mb * 1024 * 1024:
            st.error(f"File too large (> {max_mb} MB).")
        else:
            # Show waveform preview
            st.subheader("🎵 Waveform Preview")
            try:
                y, sr = librosa.load(uploaded, sr=None)
                fig, ax = plt.subplots(figsize=(6, 2))
                librosa.display.waveshow(y, sr=sr, color="cyan")
                plt.xlabel("Time (s)")
                plt.ylabel("Amplitude")
                plt.tight_layout()
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Could not load waveform: {e}")

            if st.button("🚀 Upload & Analyze"):
                with st.spinner("Uploading to backend..."):
                    files = {"file": (uploaded.name, uploaded.getvalue())}
                    r = requests.post(f"{BACKEND_URL}/api/analyze", files=files, timeout=120)
                if r.status_code == 200:
                    data = r.json()
                    st.session_state["file_id"] = data["file_id"]
                    st.success(f"Uploaded successfully — File ID: {data['file_id']}")
                else:
                    st.error(f"Upload failed: {r.text}")

    st.markdown("---")
    st.header("🕘 History")
    if st.button("Refresh history"):
        r = requests.get(f"{BACKEND_URL}/api/history")
        if r.ok:
            items = r.json().get("items", [])
            for it in items:
                st.write(f"- {it.get('file_id')} — {it.get('filename')} — {it.get('status')}")
        else:
            st.error("Failed to fetch history.")

with col2:
    st.header("2️⃣ Analysis Progress")
    file_id = st.session_state.get("file_id")
    status_placeholder = st.empty()
    result_placeholder = st.empty()

    if file_id:
        status_placeholder.info(f"Processing file `{file_id}`...")

        for _ in range(60):  # 2 min timeout
            r = requests.get(f"{BACKEND_URL}/api/result/{file_id}")
            if r.status_code == 200:
                doc = r.json()
                status = doc.get("status")
                if status == "completed":
                    status_placeholder.success("✅ Analysis Complete!")

                    result_placeholder.subheader("🧠 Analysis Results")
                    st.markdown(f"**Transcript:** {doc.get('transcript')}")
                    st.markdown(f"**Confidence:** {doc.get('transcript_confidence')}")
                    
                    st.markdown("### 🎵 YAMNet Top Events:")
                    for ev in doc.get("yamnet", [])[:5]:
                        st.write(f"- {ev['event']} ({ev['score']})")
                    
                    s = doc.get("sentiment", {})
                    st.markdown(f"### 💬 Sentiment: `{s.get('tone')}` (compound={s.get('compound')})")

                    if doc.get("mel_image_url"):
                        img_r = requests.get(f"{BACKEND_URL}{doc.get('mel_image_url')}")
                        if img_r.status_code == 200:
                            st.image(img_r.content, caption="Mel Spectrogram", use_container_width=True)
                    break
                elif status == "error":
                    status_placeholder.error("❌ Error: " + str(doc.get("error")))
                    break
                else:
                    status_placeholder.info("⏳ Processing...")
            else:
                status_placeholder.warning("Waiting for backend response...")
            time.sleep(2)
    else:
        st.info("Upload an audio file to begin.")
