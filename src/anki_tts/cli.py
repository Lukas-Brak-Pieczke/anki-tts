import argparse
import base64
import json
import sys
from pathlib import Path

from .anki_client import AnkiConnectClient, AnkiConnectError
from .text_cleaner import clean_text_for_tts
from .tts_engine import ensure_audio_file, get_audio_filename

def main():
    parser = argparse.ArgumentParser(description="Standalone TTS Audio Generator for Anki cards.")
    parser.add_argument("--config", "-c", default="config.json", help="Path to JSON configuration file")
    parser.add_argument("--apply", action="store_true", help="Apply changes to the Anki database (dry-run by default)")
    parser.add_argument("--limit", type=int, default=0, help="Limit processing to N notes (e.g., --limit 1)")
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        # Fallback check inside config/ folder
        if Path("config/example.json").exists() and not Path("config.json").exists():
            print(f"ERROR: Configuration file '{config_path}' not found.")
            print("Please copy 'config/example.json' to 'config.json' and fill in your settings.")
            sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    client = AnkiConnectClient(url=config.get("anki_url", "http://127.0.0.1:8765"))
    custom_bin = config.get("edge_tts_binary", "")
    is_apply_mode = args.apply

    if not is_apply_mode:
        print("\n" + "="*65)
        print("PREVIEW MODE (DRY-RUN) — No changes will be saved to Anki.")
        print("To apply changes to your Anki collection, add the flag: --apply")
        print("="*65 + "\n")
    else:
        print("\n" + "="*65)
        print("WRITE MODE (--apply) — Generating audio and updating Anki database.")
        print("="*65 + "\n")

    for task in config.get("tasks", []):
        task_name = task.get("name", "Unnamed Task")
        deck = task["deck"]
        model = task["model"]
        src_field = task["source_field"]
        tgt_field = task["target_field"]
        voice = task["voice"]
        overwrite_mode = task.get("overwrite_mode", "skip_if_exists")

        print(f"--- Running Task: {task_name} (Deck: '{deck}', Note Type: '{model}') ---")
        query = f'deck:"{deck}" "note:{model}"'

        try:
            note_ids = client.find_notes(query)
        except AnkiConnectError as e:
            print(f"[ERROR] Could not fetch notes for task '{task_name}': {e}\n")
            continue

        print(f"Found {len(note_ids)} matching notes.")
        if args.limit > 0:
            note_ids = note_ids[:args.limit]
            print(f"Limited processing to first {args.limit} notes.")

        try:
            notes_info = client.get_notes_info(note_ids)
        except AnkiConnectError as e:
            print(f"[ERROR] Failed to read note details: {e}\n")
            continue

        processed, skipped, errors = 0, 0, 0

        for note in notes_info:
            note_id = note["noteId"]
            fields = note["fields"]

            if src_field not in fields or tgt_field not in fields:
                print(f"[SKIP] Note ID {note_id}: Missing field '{src_field}' or '{tgt_field}'.")
                skipped += 1
                continue

            raw_src = fields[src_field]["value"]
            clean_text = clean_text_for_tts(raw_src)

            if not clean_text:
                print(f"[SKIP] Note ID {note_id}: Source field empty after HTML cleaning.")
                skipped += 1
                continue

            tgt_val = fields[tgt_field]["value"]
            filename = get_audio_filename(clean_text, voice)
            sound_tag = f"[sound:{filename}]"

            if sound_tag in tgt_val and overwrite_mode == "skip_if_exists":
                print(f"[SKIP] Note ID {note_id} ('{clean_text[:25]}...'): Audio [sound:{filename}] already present.")
                skipped += 1
                continue

            print(f"[PREPARED] Note ID {note_id} | Text: '{clean_text}' -> Audio File: {filename}")

            if not is_apply_mode:
                processed += 1
                continue

            # Write Mode Execution
            try:
                audio_path = ensure_audio_file(clean_text, voice, custom_binary=custom_bin)

                with open(audio_path, "rb") as audio_file:
                    b64_data = base64.b64encode(audio_file.read()).decode("utf-8")

                client.store_media_file(filename, b64_data)

                if tgt_field == src_field:
                    new_val = f"{tgt_val} {sound_tag}".strip() if sound_tag not in tgt_val else tgt_val
                else:
                    new_val = sound_tag if overwrite_mode != "append" else f"{tgt_val} {sound_tag}".strip()

                client.update_note_fields(note_id, {tgt_field: new_val})
                processed += 1

            except AnkiConnectError as e:
                print(f"[ANKI WRITE ERROR] Note ID {note_id}: {e}")
                errors += 1
                break
            except Exception as e:
                print(f"[TTS/FILE ERROR] Note ID {note_id}: {e}")
                errors += 1

        print(f"\nSummary for '{task_name}': Processed: {processed}, Skipped: {skipped}, Errors: {errors}\n")

if __name__ == "__main__":
    main()
