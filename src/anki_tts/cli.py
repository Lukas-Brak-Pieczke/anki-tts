import argparse
import json
import os
import sys

from .generator import run_tasks
from .selector import discover_and_select_decks


def main():
    parser = argparse.ArgumentParser(description="Anki Media TTS Generator")
    parser.add_argument(
        "-c",
        "--config",
        default="config.json",
        help="Path to configuration file (default: config.json)",
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Force interactive deck selection mode",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply audio generation changes to Anki (default is dry-run)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of notes to process per task",
    )
    args = parser.parse_args()

    if args.interactive or not os.path.exists(args.config):
        if not os.path.exists(args.config) and not args.interactive:
            print("Configuration file not found. Falling back to interactive mode.\n")

        selected_decks = discover_and_select_decks()
        if not selected_decks:
            print("No decks selected. Exiting.")
            sys.exit(0)

        tasks = []
        for item in selected_decks:
            tasks.append(
                {
                    "name": f"Auto Task - {item['deck']}",
                    "deck": item["deck"],
                    "model": item["model"],
                    "source_field": "Front",
                    "target_field": "Front",
                    "voice": "fi-FI-HarriNeural",
                    "overwrite_mode": "skip_if_exists",
                }
            )

        config = {
            "anki_url": "http://127.0.0.1:8765",
            "edge_tts_binary": "",
            "tasks": tasks,
        }
    else:
        with open(args.config, "r", encoding="utf-8") as f:
            config = json.load(f)

    dry_run = not args.apply
    run_tasks(config, dry_run=dry_run, limit=args.limit)


if __name__ == "__main__":
    main()
