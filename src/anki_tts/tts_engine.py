import hashlib
import os
import subprocess
from pathlib import Path

CACHE_DIR = Path(".cache/audio")

def get_audio_filename(text: str, voice: str) -> str:
    """Generates a stable, unique filename based on the voice and text content."""
    digest = hashlib.sha256(f"{voice}:{text}".encode("utf-8")).hexdigest()[:12]
    return f"tts_{digest}.mp3"

def ensure_audio_file(text: str, voice: str, custom_binary: str = "") -> Path:
    """
    Returns the path to the MP3 audio file.
    If the file exists in .cache/audio/, it reuses it. Otherwise, synthesizes via edge-tts.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    filename = get_audio_filename(text, voice)
    mp3_path = CACHE_DIR / filename

    # 1. Check local cache
    if mp3_path.exists() and mp3_path.stat().st_size > 0:
        return mp3_path

    # 2. Determine binary to execute
    binary = custom_binary if custom_binary and os.path.exists(custom_binary) else "edge-tts"

    cmd = [binary, "--voice", voice, "--text", text, "--write-media", str(mp3_path)]

    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        raise RuntimeError(
            f"Command '{binary}' not found. Ensure edge-tts is installed in the active environment "
            f"or specify the binary path in config.json under 'edge_tts_binary'."
        )

    if res.returncode != 0:
        if mp3_path.exists():
            mp3_path.unlink()  # Remove partial or corrupt file
        raise RuntimeError(f"Edge TTS error ({voice}): {res.stderr.strip()}")

    return mp3_path
