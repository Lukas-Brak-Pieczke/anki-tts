import json
import os
import urllib.error
import urllib.request


class AnkiClient:
    def __init__(self, url: str = "http://127.0.0.1:8765"):
        self.url = url

    def invoke(self, action: str, **params):
        payload = json.dumps({"action": action, "version": 6, "params": params}).encode(
            "utf-8"
        )
        req = urllib.request.Request(
            self.url,
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req) as response:
                res = json.loads(response.read().decode("utf-8"))
                if res.get("error"):
                    raise Exception(res["error"])
                return res["result"]
        except urllib.error.URLError as e:
            raise RuntimeError(
                f"Cannot connect to AnkiConnect at {self.url}. Ensure Anki is running."
            ) from e

    def find_notes(self, query: str) -> list[int]:
        return self.invoke("findNotes", query=query)

    def get_notes_info(self, note_ids: list[int]) -> list[dict]:
        return self.invoke("notesInfo", notes=note_ids)

    def store_media_file(self, filename: str, path: str | None = None):
        file_path = path if path else os.path.abspath(filename)
        base_name = os.path.basename(filename)
        return self.invoke("storeMediaFile", filename=base_name, path=file_path)

    def update_note_fields(self, note_id: int, fields: dict):
        return self.invoke("updateNoteFields", note={"id": note_id, "fields": fields})
