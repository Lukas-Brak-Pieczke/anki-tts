import json
import sys
import urllib.error
import urllib.request

ANKI_URL = "http://127.0.0.1:8765"


def anki_request(action: str, **params):
    """Helper function to communicate with AnkiConnect API using standard library."""
    payload = json.dumps({"action": action, "version": 6, "params": params}).encode(
        "utf-8"
    )
    req = urllib.request.Request(
        ANKI_URL, data=payload, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode("utf-8"))
            if res.get("error"):
                raise Exception(res["error"])
            return res["result"]
    except urllib.error.URLError:
        print(
            "\n❌ Error: Cannot connect to Anki Desktop. "
            "Make sure Anki is running and the AnkiConnect add-on is installed."
        )
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ AnkiConnect API error: {e}")
        sys.exit(1)


def discover_and_select_decks() -> list[dict]:
    """Interactively scans Anki for decks, displays them, and prompts the user for selection."""
    print("🔍 Discovering available decks in Anki...\n")

    decks = anki_request("deckNames")
    # Filter out empty default decks
    decks = [d for d in decks if d != "Default"]

    if not decks:
        print("No decks found in Anki.")
        return []

    discovered = []

    # Retrieve deck information
    for index, deck_name in enumerate(sorted(decks), start=1):
        note_ids = anki_request("findNotes", query=f'deck:"{deck_name}"')
        count = len(note_ids)

        model_name = "Unknown"
        if note_ids:
            info = anki_request("notesInfo", notes=[note_ids[0]])
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

    # Print interactive table
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

    # User input selection
    user_input = (
        input("\nEnter the deck IDs to process (e.g., 1, 3 or 'all') [default: all]: ")
        .strip()
        .lower()
    )

    if not user_input or user_input == "all":
        return discovered

    selected_items = []
    try:
        indices = [int(x.strip()) for x in user_input.split(",") if x.strip().isdigit()]
        selected_items = [item for item in discovered if item["id"] in indices]
    except ValueError:
        print("❌ Invalid input format.")
        return []

    return selected_items


if __name__ == "__main__":
    selected = discover_and_select_decks()
    if selected:
        print(f"\nSelected {len(selected)} deck(s): {[s['deck'] for s in selected]}")
