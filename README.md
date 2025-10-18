[README_ALM.md](https://github.com/user-attachments/files/22982728/README_ALM.md)
# 🎧 ALM – Audio Language Model & Real-Time Audio Analyzer

A full-stack AI prototype that performs **real-time audio analysis**, including:
- 🎙️ Speech-to-Text (via Speechmatics API)
- 🔊 Audio Event Detection (via YAMNet)
- 💬 Sentiment Analysis (via NLTK)
- 🎛️ Mel Spectrogram Visualization
- 🧩 MongoDB + FastAPI backend
- 🖥️ Streamlit front-end with dark mode UI

---

## 🚀 Tech Stack

| Layer | Technology |
|:------|:------------|
| **Frontend** | [Streamlit](https://streamlit.io) (Python UI) |
| **Backend** | [FastAPI](https://fastapi.tiangolo.com/) |
| **AI/ML Models** | TensorFlow Hub (YAMNet), NLTK |
| **Speech Recognition** | [Speechmatics API](https://www.speechmatics.com) |
| **Database** | MongoDB |
| **Audio Processing** | FFmpeg, Librosa |
| **Deployment Ready** | Docker + Uvicorn |

---

## 🧩 Features

- Upload `.wav`, `.mp3`, or `.m4a` audio files  
- Real-time processing via FastAPI background tasks  
- Extracts transcript + confidence score  
- Detects sound events using **YAMNet**  
- Performs sentiment analysis on transcript  
- Generates & displays mel spectrogram images  
- Stores analysis history in MongoDB  
- Streamlit frontend auto-updates results in real-time  

---

## 🧠 Architecture

```
📦 audio-analyzer
 ┣ 📂 backend
 ┃ ┣ 📂 app
 ┃ ┃ ┣ 📂 core
 ┃ ┃ ┣ 📂 db
 ┃ ┃ ┣ 📂 utils
 ┃ ┃ ┗ main.py
 ┃ ┣ 📜 requirements.txt
 ┃ ┗ 📜 Dockerfile
 ┣ 📂 frontend
 ┃ ┗ 📜 streamlit_app.py
 ┗ 📜 README.md
```

---

## ⚙️ Setup & Run

### 1️⃣ Clone repo
```bash
git clone https://github.com/manan-jagani/ALM-AUDIO_ANALYZER.git
cd ALM-AUDIO_ANALYZER
```

### 2️⃣ Backend setup
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs at 👉 `http://127.0.0.1:8000`

---

### 3️⃣ Frontend setup
Open a **new terminal**:

```bash
cd frontend
streamlit run streamlit_app.py
```

Frontend runs at 👉 `http://localhost:8501`

---

## 🔑 Environment Variables (.env)
```
MONGO_URI=mongodb://localhost:27017
MONGO_DB=audio_analysis
SPEECHMATICS_API_KEY=your_api_key_here
BACKEND_URL=http://127.0.0.1:8000
MAX_UPLOAD_MB=50
```

---

## 📸 Screenshots
> _Add screenshots of your Streamlit dashboard here (upload later)_  
> - Upload section  
> - Live waveform or mel-spectrogram  
> - Sentiment and event results  

---

## 📜 License
MIT © [Manan Jagani](https://github.com/manan-jagani)

---

## 🌟 Acknowledgments
- TensorFlow Hub – YAMNet model  
- NLTK Sentiment Analyzer  
- Speechmatics Speech-to-Text  
- Streamlit + FastAPI community ❤️  

---

## 💬 Contact
📧 **mananjagani48@gmail.com**  
🌐 [GitHub Profile](https://github.com/manan-jagani)
