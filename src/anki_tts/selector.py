import json
import os
import sys

from .anki_client import AnkiClient

"""
Interactive Deck and Voice Selector.

Discovers available decks in Anki, manages persistent user voice presets in
`~/.config/anki-tts/presets.json`, and guides the user through deck and voice selection.
"""

CONFIG_DIR = os.path.expanduser("~/.config/anki-tts")
PRESETS_FILE = os.path.join(CONFIG_DIR, "presets.json")

DEFAULT_VOICES = [
    "en-US-AvaNeural",
    "de-DE-KillianNeural",
    "fr-FR-HenriNeural",
    "es-ES-AlvaroNeural",
    "it-IT-DiegoNeural",
    "sv-SE-MattiasNeural",
    "fi-FI-HarriNeural",
    "pl-PL-MarekNeural",
]


def is_valid_voice_name(voice: str) -> bool:
    if not isinstance(voice, str):
        return False
    v = voice.strip().lower()
    if v in ["none", "null", "all", "default", "custom", ""]:
        return False
    return len(v) >= 3 and "-" in v


def load_voice_presets() -> list[str]:
    if not os.path.exists(PRESETS_FILE):
        return DEFAULT_VOICES

    try:
        with open(PRESETS_FILE, "r", encoding="utf-8") as f:
            saved = json.load(f)
            if isinstance(saved, list):
                valid_saved = [v for v in saved if is_valid_voice_name(v)]
                return valid_saved + [v for v in DEFAULT_VOICES if v not in valid_saved]
    except Exception:
        pass
    return DEFAULT_VOICES


def save_voice_preset(voice: str):
    if not is_valid_voice_name(voice):
        return

    os.makedirs(CONFIG_DIR, exist_ok=True)
    presets = load_voice_presets()

    if voice in presets:
        presets.remove(voice)
    presets.insert(0, voice)

    try:
        with open(PRESETS_FILE, "w", encoding="utf-8") as f:
            json.dump(presets[:15], f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save preset to {PRESETS_FILE}: {e}")


def select_voice_for_deck(deck_name: str) -> str:
    presets = load_voice_presets()
    display_options = presets[:8]

    print(f"\n--- Select Voice for Deck: '{deck_name}' ---")
    for idx, voice in enumerate(display_options, start=1):
        print(f"[{idx}] {voice}")

    custom_option_num = len(display_options) + 1
    print(
        f"[{custom_option_num}] Custom voice ID (run 'uv run edge-tts --list-voices' to list all)"
    )

    default_idx = 1
    user_choice = input(
        f"\nChoose voice option [default: {default_idx} ({display_options[0]})]: "
    ).strip()

    if not user_choice:
        chosen_voice = display_options[0]
    elif user_choice.isdigit():
        num = int(user_choice)
        if 1 <= num <= len(display_options):
            chosen_voice = display_options[num - 1]
        elif num == custom_option_num:
            chosen_voice = input(
                "Enter Edge-TTS voice ID (e.g., eo-EO-TitusNeural): "
            ).strip()
            if not is_valid_voice_name(chosen_voice):
                print(
                    f"Error: '{chosen_voice}' is not a valid voice ID format. Exiting."
                )
                sys.exit(1)
        else:
            print(f"Error: Invalid option number '{num}'. Exiting.")
            sys.exit(1)
    else:
        print(
            f"Error: Invalid input '{user_choice}'. Expected an option number. Exiting."
        )
        sys.exit(1)

    save_voice_preset(chosen_voice)
    return chosen_voice


def discover_and_select_decks(client: AnkiClient | None = None) -> list[dict]:
    if client is None:
        client = AnkiClient()

    print("Discovering available decks in Anki...\n")

    try:
        decks = client.invoke("deckNames")
    except Exception as e:
        print(f"Error communicating with Anki: {e}")
        sys.exit(1)

    decks = [d for d in decks if d != "Default"]

    if not decks:
        print("No decks found in Anki.")
        return []

    discovered = []
    for index, deck_name in enumerate(sorted(decks), start=1):
        note_ids = client.find_notes(f'deck:"{deck_name}"')
        count = len(note_ids)

        model_name = "Unknown"
        if note_ids:
            info = client.get_notes_info([note_ids[0]])
            if info and len(info) > 0:
                model_name = info[0].get("modelName", "Unknown")

        discovered.append(
            {
                "id": index,
                "deck": deck_name,
                "model": model_name,
                "count": count,
            }
        )

    print(f"{'ID':<4} | {'Deck Name':<32} | {'Note Type (Model)':<28} | {'Cards':<8}")
    print("-" * 80)
    for item in discovered:
        deck_disp = (
            item["deck"][:29] + "..." if len(item["deck"]) > 32 else item["deck"]
        )
        model_disp = (
            item["model"][:25] + "..." if len(item["model"]) > 28 else item["model"]
        )
        print(
            f"[{item['id']:>2}] | {deck_disp:<32} | {model_disp:<28} | {item['count']:<8}"
        )
    print("-" * 80)

    user_input = (
        input("\nEnter the deck IDs to process (e.g., 1, 3 or 'all') [default: all]: ")
        .strip()
        .lower()
    )

    if not user_input or user_input == "all":
        return discovered

    selected_items = []
    parts = [x.strip() for x in user_input.split(",") if x.strip()]

    for p in parts:
        if not p.isdigit():
            print(f"Error: Invalid deck selection input '{p}'. Exiting.")
            sys.exit(1)

        idx = int(p)
        found = [item for item in discovered if item["id"] == idx]
        if not found:
            print(f"Error: Deck ID [{idx}] does not exist. Exiting.")
            sys.exit(1)

        selected_items.extend(found)

    return selected_items
