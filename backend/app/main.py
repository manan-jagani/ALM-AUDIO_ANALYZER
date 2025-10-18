import os
import uuid
import asyncio
from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.db.mongo import init_db  # fixed import
from app.core.spectrogram import save_mel_spectrogram
from app.core.yamnet_inference import YAMNetWrapper
from app.core.sentiment import analyze_sentiment
from app.core.speechmatics_api import SpeechmaticsClient
from app.utils.audio_utils import to_mono_wav
from datetime import datetime
from bson import ObjectId   # ✅ Added for ObjectId fix

# =============================
# Directory Setup
# =============================
DATA_DIR = "./data"
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
RESULT_DIR = os.path.join(DATA_DIR, "results")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)

# =============================
# FastAPI Initialization
# =============================
app = FastAPI(title="Audio Analyzer API (Prototype)")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================
# Global Placeholders
# =============================
yamnet: YAMNetWrapper | None = None
speech_client: SpeechmaticsClient | None = None
db = None

# =============================
# Utility Fix for Mongo ObjectId
# =============================
def fix_mongo_ids(doc):
    """Recursively convert MongoDB ObjectIds to strings for JSON serialization."""
    if isinstance(doc, list):
        return [fix_mongo_ids(i) for i in doc]
    elif isinstance(doc, dict):
        return {k: fix_mongo_ids(v) for k, v in doc.items()}
    elif isinstance(doc, ObjectId):
        return str(doc)
    else:
        return doc

# =============================
# Startup Event
# =============================
@app.on_event("startup")
async def startup_event():
    global yamnet, speech_client, db
    db = await init_db()
    yamnet = YAMNetWrapper()
    await yamnet.load_model()
    speech_client = SpeechmaticsClient(api_key=os.getenv("SPEECHMATICS_API_KEY", ""))

# =============================
# Response Models
# =============================
class AnalyzeResponse(BaseModel):
    file_id: str
    status: str

# =============================
# Main Audio Analysis Endpoint
# =============================
@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze(file: UploadFile = File(...)):
    name = file.filename
    ext = name.split(".")[-1].lower()
    if ext not in ("wav", "mp3", "m4a"):
        raise HTTPException(status_code=400, detail="Unsupported audio format")

    file_id = str(uuid.uuid4())
    upload_path = f"{UPLOAD_DIR}/{file_id}.{ext}"
    with open(upload_path, "wb") as f:
        f.write(await file.read())

    wav_path = await to_mono_wav(upload_path, target_path=f"{UPLOAD_DIR}/{file_id}.wav")

    record = {
        "file_id": file_id,
        "filename": name,
        "upload_time": datetime.utcnow().isoformat(),
        "status": "processing",
    }
    await db.insert_one(record)

    asyncio.create_task(process_audio(file_id, wav_path))

    return AnalyzeResponse(file_id=file_id, status="processing")

# =============================
# Background Audio Processing Task
# =============================
async def process_audio(file_id: str, wav_path: str):
    try:
        transcript, stt_conf = await speech_client.transcribe_file(wav_path)
        yamnet_results = await yamnet.infer(wav_path)
        sentiment = analyze_sentiment(transcript)
        mel_path = f"{RESULT_DIR}/{file_id}_mel.png"
        save_mel_spectrogram(wav_path, mel_path)

        summary = {
            "file_id": file_id,
            "transcript": transcript,
            "transcript_confidence": stt_conf,
            "yamnet": yamnet_results,
            "sentiment": sentiment,
            "mel_image": os.path.basename(mel_path),
            "status": "completed",
            "completed_time": datetime.utcnow().isoformat()
        }

        await db.update_one({"file_id": file_id}, {"$set": summary})
    except Exception as e:
        await db.update_one({"file_id": file_id}, {"$set": {"status": "error", "error": str(e)}})

# =============================
# Fetch Recent History
# =============================
@app.get("/api/history")
async def history(limit: int = 50):
    docs = await db.find({}, limit=limit, sort=[("upload_time", -1)])
    return {"items": fix_mongo_ids(docs)}  # ✅ Fixed

# =============================
# Fetch Specific Result
# =============================
@app.get("/api/result/{file_id}")
async def result(file_id: str):
    doc = await db.find_one({"file_id": file_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    if "mel_image" in doc:
        doc["mel_image_url"] = f"/api/result/{file_id}/mel"
    return fix_mongo_ids(doc)  # ✅ Fixed

# =============================
# Fetch Mel Spectrogram Image
# =============================
@app.get("/api/result/{file_id}/mel")
async def result_mel(file_id: str):
    doc = await db.find_one({"file_id": file_id})
    if not doc or "mel_image" not in doc:
        raise HTTPException(status_code=404, detail="Not found")
    path = os.path.join(RESULT_DIR, doc["mel_image"])
    return FileResponse(path, media_type="image/png")
