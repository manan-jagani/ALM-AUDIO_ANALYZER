import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import csv
import librosa
import soundfile as sf
from typing import List, Dict

MODEL_URL = "https://tfhub.dev/google/yamnet/1"
LABELS_CSV = "app/core/yamnet_class_map.csv"  # path inside container

class YAMNetWrapper:
    def __init__(self):
        self.model = None
        self.class_names = []

    async def load_model(self):
        # Load YAMNet model from TF Hub
        print("🔊 Loading YAMNet model...")
        self.model = hub.load(MODEL_URL)
        # Load class labels
        with open(LABELS_CSV) as f:
            reader = csv.reader(f)
            self.class_names = [row[2] for row in reader]
        print(f"✅ Loaded YAMNet with {len(self.class_names)} labels.")

    async def infer(self, wav_path: str) -> List[Dict]:
        # Load audio at 16kHz mono (YAMNet expects this)
        waveform, sr = librosa.load(wav_path, sr=16000, mono=True)
        waveform = waveform.astype(np.float32)

        # Run inference
        scores, embeddings, spectrogram = self.model(waveform)

        # Average scores over time windows
        mean_scores = tf.reduce_mean(scores, axis=0)
        top5_idx = tf.argsort(mean_scores, direction='DESCENDING')[:5].numpy()

        results = []
        for i in top5_idx:
            results.append({
                "event": self.class_names[i],
                "score": float(mean_scores[i].numpy())
            })
        return results
