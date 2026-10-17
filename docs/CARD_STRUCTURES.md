# Flashcard Structures & Template Guide

`anki-tts` operates directly on Anki **Notes** via AnkiConnect. This guide explains how different note types, reverse cards, and card templates interact with the generator.

---

## Supported Note Layouts

### 1. Basic Cards (`Front` -> `Back`)
- **Source Field**: `Front`
- **Target Field**: `Front` or `Audio`
- **Behavior**: Appends `[sound:...]` to the primary field or inserts it into a dedicated audio field. Audio plays automatically when the card side is revealed.

### 2. Basic with Reversed Cards (`Front` <-> `Back`)
- **Source Field**: `Front`
- **Target Field**: `Front`
- **Behavior**: Anki automatically generates two cards from a single note:
  - **Card 1 (Front -> Back)**: Plays audio when displaying the prompt.
  - **Card 2 (Back -> Front)**: Plays audio when revealing the answer on the back.
  *Note: Because TTS is attached at the Note level, you do not need separate tasks for reverse cards.*

### 3. Dedicated Audio Field (Recommended for Custom Templates)
- **Source Field**: `Front`
- **Target Field**: `Audio`
- **Behavior**: Keeps audio tags isolated from text. In your Anki Card Template, add `{{Audio}}` wherever you want the sound button or auto-play to trigger.

---

## Text Cleaning & Formatting Rules

Before sending text to Edge TTS, `anki-tts` cleans field contents:
- **HTML Removal**: Tags such as `<b>`, `<i>`, `<p>`, and `<br>` are stripped.
- **Whitespace Normalization**: Line breaks and paragraph breaks are converted to single spaces so Edge TTS reads continuous prose naturally.
- **Recursive Tag Protection**: Existing `[sound:...]` tags in the source field are stripped before synthesis to avoid reading audio filenames aloud.

---

## Detailed `overwrite_mode` Behavior

| Mode | Behavior | Best Used For |
| :--- | :--- | :--- |
| **`skip_if_exists`** *(Default)* | Skips synthesis if the target field already contains `[sound:tts_hash.mp3]`. | Default safe operation to avoid duplicating work or tags. |
| **`append`** | Appends `[sound:...]` to existing text in `target_field`. | Target field is the same as source field (`Front` -> `Front`). |
| **`overwrite`** | Replaces the entire content of `target_field` with `[sound:...]`. | Dedicated audio fields (`target_field: "Audio"`). |
