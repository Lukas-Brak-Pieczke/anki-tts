import json
import urllib.request
import urllib.error
from typing import Any, Dict, List

class AnkiConnectError(Exception):
    pass

class AnkiConnectClient:
    def __init__(self, url: str = "http://127.0.0.1:8765", timeout: int = 10):
        self.url = url
        self.timeout = timeout

    def invoke(self, action: str, **params) -> Any:
        payload = json.dumps({"action": action, "version": 6, "params": params}).encode("utf-8")
        req = urllib.request.Request(
            self.url,
            data=payload,
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                res = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as e:
            raise AnkiConnectError(
                f"Could not connect to AnkiConnect at {self.url}. "
                f"Ensure Anki is running and the AnkiConnect add-on is enabled. Details: {e}"
            )

        if res.get("error") is not None:
            err_msg = str(res["error"])
            if "editor" in err_msg.lower():
                raise AnkiConnectError(
                    "ERROR: An open note editor in Anki is blocking database operations! "
                    "Please close the card editor window in Anki and try again."
                )
            raise AnkiConnectError(f"AnkiConnect API error: {err_msg}")

        return res.get("result")

    def find_notes(self, query: str) -> List[int]:
        return self.invoke("findNotes", query=query)

    def get_notes_info(self, note_ids: List[int]) -> List[Dict[str, Any]]:
        return self.invoke("notesInfo", notes=note_ids)

    def store_media_file(self, filename: str, base64_data: str) -> str:
        return self.invoke("storeMediaFile", filename=filename, data=base64_data)

    def update_note_fields(self, note_id: int, fields: Dict[str, str]) -> None:
        self.invoke("updateNoteFields", note={"id": note_id, "fields": fields})
