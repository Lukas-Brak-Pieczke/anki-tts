import hashlib
import os
import subprocess

class TTSEngine:

    def __init__(self, edge_tts_binary: str = ""):
        self.binary = edge_tts_binary if edge_tts_binary else "edge-tts"

    def generate(self, text: str, voice: str = "fi-FI-HarriNeural") -> str:
        if not text:
            raise ValueError("Text for TTS generation cannot be empty.")

        hash_id = hashlib.md5(f"{voice}:{text}".encode("utf-8")).hexdigest()[:12]
        filename = f"tts_{hash_id}.mp3"

        if os.path.exists(filename):
            return filename

        cmd = [
            self.binary,
            "--voice",
            voice,
            "--text",
            text,
            "--write-media",
            filename,
        ]

        try:
            subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        except FileNotFoundError:
            raise RuntimeError(
                f"Executable '{self.binary}' not found in PATH. "
                "Ensure edge-tts is installed in your environment."
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"edge-tts failed with exit code {e.returncode}: {e.stderr}"
            )

        return filename
