# Anki Media TTS Generator

A lightweight, standalone CLI tool to generate high-quality Text-to-Speech (TTS) audio for Anki cards using Microsoft Edge TTS and AnkiConnect.

---

## Requirements & Quick Start

### Requirements
1. **Python 3.10+**
2. **Anki Desktop** running with the **AnkiConnect** add-on installed (Code: `2055492153`).
3. [`uv`](https://github.com/astral-sh/uv) package manager.

### Quick Start

A default `config.json` is already provided at the root of the project. You can edit it directly or optionally copy a template from `examples/`:

```bash
# Optional: Use a specific template from examples/
# cp examples/basic_and_reversed.json config.json
# cp examples/dedicated_audio.json config.json
# cp examples/multilingual.json config.json

# 1. Run unit tests
uv run python -m unittest discover tests

# 2. Preview changes (Dry-Run by default)
uv run anki-tts
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

C### Popular Voice Examples
- **Finnish**: `"fi-FI-HarriNeural"`, `"fi-FI-SelmaNeural"`
- **Polish**: `"pl-PL-MarekNeural"`, `"pl-PL-ZofiaNeural"`
- **English (US)**: `"en-US-AvaNeural"`, `"en-US-AndrewNeural"`
- **German**: `"de-DE-KillianNeural"`, `"de-DE-KatjaNeural"`

copy the desired voice identifier into the "voice" field in your config.json.

## Configuration Reference (config.json)

```json
{
  "anki_url": "http://127.0.0.1:8765",
  "edge_tts_binary": "",
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

| Parameter | Options / Default | Description |
| :--- | :--- | :--- |
| `anki_url` | `"http://127.0.0.1:8765"` | AnkiConnect HTTP API URL. |
| `deck` | Exact deck name | Name of target Anki deck. |
| `model` | Exact note type name | Anki Note Type (e.g., `"Basic"`). |
| `source_field` | Field name | Field containing text to read aloud. |
| `target_field` | Field name | Field to store `[sound:...]` tag. |
| `voice` | Edge TTS voice string | Voice identifier (e.g., `"fi-FI-HarriNeural"`). |
| `overwrite_mode` | `"skip_if_exists"` / `"append"` / `"overwrite"` | Behavior when audio tag exists. |

*For in-depth documentation on note layouts, reverse cards, and card templates, see [docs/CARD_STRUCTURES.md](docs/CARD_STRUCTURES.md).*

---

## CLI Usage
```bash
# Preview mode (Dry-run, safe default)
uv run anki-tts

# Test run on 1 single note (Requires card editor in Anki to be closed)
uv run anki-tts --limit 1 --apply

# Process full deck
uv run anki-tts --apply

# Global installation as a CLI tool
uv tool install .
```

---

## Privacy & Network Disclosure
Microsoft Edge TTS is a cloud service. Text extracted from configured source fields is transmitted via TLS-encrypted connections directly to Microsoft Edge TTS endpoints solely to generate audio files. No personal Anki note metadata, deck statistics, or personal identifiers are stored or transmitted.
