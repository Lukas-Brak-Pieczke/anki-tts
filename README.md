# Anki TTS Generator (`anki-tts`)

An interactive, high-performance CLI tool for automatically generating Text-to-Speech (TTS) audio for Anki flashcards using Microsoft Edge's neural voices (`edge-tts`) and `AnkiConnect`.

---

## ✨ Features

- **Interactive First Workflow**: Launch `anki-tts` directly—no manual JSON configuration required.
- **Automatic Deck Discovery**: Connects to running Anki instance, listing decks, card types, and note counts.
- **Smart Voice Presets**: Choose from curated neural voices across multiple languages or specify custom Edge TTS voice IDs. Selections are stored locally in `~/.config/anki-tts/presets.json`.
- **Hardened Input Processing**: Safely handles complex text, HTML tags, HTML entities, sound tag collisions, and prefix hyphens (e.g., `-o`, `-a` in Esperanto or language suffixes).
- **Safety Options**:
  - `--dry-run`: Simulate audio generation and view exact note field targets without touching your Anki database.
  - `--limit`: Restrict batch operations to a test subset of cards.
- **Legacy Batch Support**: Pass a custom JSON configuration file via `-c` / `--config` for automated workflows.

---

## 📋 Requirements

1. **Anki Desktop** running locally with the **AnkiConnect** add-on installed (`code: 2055492159`).
2. **Python 3.10+** and [uv](https://github.com/astral-sh/uv) installed.
3. `edge-tts` available in your environment (installed automatically via `uv`).

---


## 🚀 Quick Start

### 📦 Option 1: Standalone Executable (Recommended for Non-Developers)

No Python, `uv`, or command-line installation is required.

1. **Ensure Anki Desktop is running** with the **AnkiConnect** add-on enabled (`code: 2055492159`).
2. Go to the [**Latest Releases Page**](https://github.com/Lukas-Brak-Pieczke/anki-tts/releases/latest) (located in the right sidebar of this repository).
3. Download the executable built for your operating system:
   - 💻 **Windows**: Download `anki-tts-windows.exe` and double-click to run.
   - 🍏 **macOS**: Download `anki-tts-macos` and run it via Terminal or right-click to open.
   - 🐧 **Linux**: Download `anki-tts-linux`, grant execution rights (`chmod +x anki-tts-linux`), and run.

---

### 🛠️ Option 2: Run from Source (For Developers)

If you have Python 3.10+ and [`uv`](https://github.com/astral-sh/uv) installed:

```bash
# Launch interactive mode directly
uv run anki-tts

# Optional safety flags
uv run anki-tts --dry-run
uv run anki-tts --limit 5
```

---

## Useful Flags

```bash
  # Test generation without modifying Anki
  uv run anki-tts --dry-run

  # Limit processing to the first 5 notes per task (useful for testing)
  uv run anki-tts --limit 5

  # Combine flags
  uv run anki-tts --dry-run --limit 2
 ```

---

## Finding Available Voices & Languages

Anki-tts supports dozens of languages via Microsoft Edge Neural TTS. To list available voices for your target language, run edge-tts in your terminal:
```bash
# List all available neural voices
uv run edge-tts --list-voices

# Filter voices by language code (e.g., Finnish, Polish, German, English, Japanese):
uv run edge-tts --list-voices | grep fi-FI
uv run edge-tts --list-voices | grep pl-PL
uv run edge-tts --list-voices | grep de-DE
uv run edge-tts --list-voices | grep en-US
uv run edge-tts --list-voices | grep ja-JP
``` 

### Popular Voice Examples
- **Finnish**: `"fi-FI-HarriNeural"`, `"fi-FI-SelmaNeural"`
- **Polish**: `"pl-PL-MarekNeural"`, `"pl-PL-ZofiaNeural"`
- **English (US)**: `"en-US-AvaNeural"`, `"en-US-AndrewNeural"`
- **German**: `"de-DE-KillianNeural"`, `"de-DE-KatjaNeural"`

Enter any voice identifier directly when selecting the Custom voice ID option in anki-tts interactive prompt, or use it inside your batch config.json.

---

## Advanced / Batch Mode

If you still prefer file-based batch configurations, pass a JSON file using -c:
```bash
uv run anki-tts -c path/to/config.json
```

Sample JSON structure:
```json
{
  "anki_url": "(http://127.0.0.1:8765)",
  "tasks": [
    {
      "name": "Finnish Vocabulary",
      "deck": "Finnish 1",
      "model": "Basic",
      "source_field": "Front",
      "target_field": "Front",
      "voice": "fi-FI-HarriNeural",
      "overwrite_mode": "skip_if_exists"
    }
  ]
}
```

---

## Privacy & Network Disclosure
Microsoft Edge TTS is a cloud service. Text extracted from configured source fields is transmitted via TLS-encrypted connections directly to Microsoft Edge TTS endpoints solely to generate audio files. No personal Anki note metadata, deck statistics, or personal identifiers are stored or transmitted.

---

## Acknowledgments & Inspiration

This project was inspired by [krmanik/anki-tts](https://github.com/krmanik/anki-tts).
