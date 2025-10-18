import os
import subprocess

async def to_mono_wav(input_path: str, target_path: str, sample_rate: int = 22050):
    """
    Convert audio file to mono WAV using ffmpeg (Windows-safe synchronous version).
    """
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-ac", "1",
        "-ar", str(sample_rate),
        "-vn",
        target_path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("FFmpeg output:", result.stdout)
    except subprocess.CalledProcessError as e:
        print("FFmpeg error:", e.stderr)
        raise RuntimeError(f"ffmpeg conversion failed: {e.stderr}") from e

    return target_path
