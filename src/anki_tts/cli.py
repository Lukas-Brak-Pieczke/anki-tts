import argparse
import json
import sys

from .anki_client import AnkiClient
from .selector import discover_and_select_decks, select_voice_for_deck
from .text_cleaner import clean_text
from .tts_engine import TTSEngine


"""
Command Line Interface (CLI) for Anki TTS.

Orchestrates the application flow: parses CLI arguments, triggers interactive deck/voice
selection or loads a legacy JSON configuration file, and executes batch TTS task processing.
"""


def process_tasks(config: dict, dry_run: bool = False, limit: int | None = None):
    anki_url = config.get("anki_url", "http://127.0.0.1:8765")
    client = AnkiClient(anki_url)
    tts = TTSEngine(edge_tts_binary=config.get("edge_tts_binary", ""))

    mode_label = (
        "DRY-RUN MODE — No changes will be applied."
        if dry_run
        else "WRITE MODE — Generating audio and updating Anki database."
    )
    print("=" * 65)
    print(mode_label)
    print("=" * 65 + "\n")

    for task in config.get("tasks", []):
        task_name = task.get("name", "Unnamed Task")
        deck = task.get("deck")
        model = task.get("model")
        source_field = task.get("source_field", "Front")
        target_field = task.get("target_field", "Front")
        voice = task.get("voice")
        overwrite_mode = task.get("overwrite_mode", "skip_if_exists")

        print(f"--- Running Task: {task_name} (Deck: '{deck}', Voice: '{voice}') ---")

        query = f'deck:"{deck}"'
        if model and model != "Unknown":
            query += f' "note:{model}"'

        note_ids = client.find_notes(query)
        print(f"Found {len(note_ids)} matching notes.")

        if limit and limit > 0:
            note_ids = note_ids[:limit]
            print(f"Limited processing to first {limit} notes.")

        if not note_ids:
            print(f"\nSummary for '{task_name}': Processed: 0, Skipped: 0, Errors: 0\n")
            continue

        notes_info = client.get_notes_info(note_ids)
        processed = 0
        skipped = 0
        errors = 0

        for note in notes_info:
            fields = note.get("fields", {})
            if not fields:
                skipped += 1
                continue

            available_fields = list(fields.keys())
            actual_source = (
                source_field if source_field in fields else available_fields[0]
            )
            actual_target = (
                target_field if target_field in fields else available_fields[0]
            )

            raw_text = fields[actual_source].get("value", "")
            cleaned_text = clean_text(raw_text)

            if not cleaned_text:
                skipped += 1
                continue

            target_val = fields[actual_target].get("value", "")
            if overwrite_mode == "skip_if_exists" and "[sound:" in target_val:
                skipped += 1
                continue

            try:
                audio_filename = tts.generate(cleaned_text, voice=voice)

                if not dry_run:
                    client.store_media_file(audio_filename)
                    sound_tag = f"[sound:{audio_filename}]"

                    if overwrite_mode == "overwrite":
                        new_val = sound_tag
                    elif overwrite_mode == "append":
                        new_val = f"{target_val} {sound_tag}".strip()
                    else:
                        new_val = (
                            sound_tag
                            if not target_val
                            else f"{target_val} {sound_tag}".strip()
                        )

                    client.update_note_fields(note["noteId"], {actual_target: new_val})

                status_tag = "DRY-RUN" if dry_run else "PREPARED"
                print(
                    f"[{status_tag}] Note ID {note['noteId']} | Text: '{cleaned_text}' -> Audio File: {audio_filename}"
                )
                processed += 1
            except Exception as e:
                print(f"Error processing Note ID {note.get('noteId')}: {e}")
                errors += 1

        print(
            f"\nSummary for '{task_name}': Processed: {processed}, Skipped: {skipped}, Errors: {errors}\n"
        )


def main():
    parser = argparse.ArgumentParser(description="Anki Media TTS Generator")
    parser.add_argument(
        "-c",
        "--config",
        default=None,
        help="Path to JSON config file (legacy / batch mode)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate processing without applying changes to Anki",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of notes to process per task",
    )
    args = parser.parse_args()

    if args.config:
        with open(args.config, "r", encoding="utf-8") as f:
            config = json.load(f)
    else:
        client = AnkiClient()
        selected_decks = discover_and_select_decks(client)
        if not selected_decks:
            print("No decks selected. Exiting.")
            sys.exit(0)

        tasks = []
        for item in selected_decks:
            voice = select_voice_for_deck(item["deck"])
            tasks.append(
                {
                    "name": f"Auto Task - {item['deck']}",
                    "deck": item["deck"],
                    "model": item["model"],
                    "source_field": "Front",
                    "target_field": "Front",
                    "voice": voice,
                    "overwrite_mode": "skip_if_exists",
                }
            )

        config = {
            "anki_url": "http://127.0.0.1:8765",
            "edge_tts_binary": "",
            "tasks": tasks,
        }

    process_tasks(config, dry_run=args.dry_run, limit=args.limit)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nUnhandled error: {e}")
    finally:
        input("\nPress Enter to exit...")
