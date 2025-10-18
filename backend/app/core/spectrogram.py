import librosa
import matplotlib.pyplot as plt
import numpy as np

def save_mel_spectrogram(wav_path: str, out_path: str, sr=22050, n_mels=128):
    y, sr = librosa.load(wav_path, sr=sr, mono=True)
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=n_mels)
    S_dB = librosa.power_to_db(S, ref=np.max)
    plt.figure(figsize=(8, 3))
    librosa.display.specshow(S_dB, sr=sr, x_axis="time", y_axis="mel")
    plt.axis('off')
    plt.tight_layout(pad=0)
    plt.savefig(out_path, bbox_inches='tight', pad_inches=0)
    plt.close()
