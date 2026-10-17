import html
import re

def clean_text_for_tts(raw_html: str) -> str:
    """
    Strips HTML tags, line breaks (<br>, <p>), existing Anki sound tags [sound:...],
    unescapes HTML entities, and normalizes whitespace for clean TTS output.
    """
    if not raw_html:
        return ""

    # Remove existing Anki audio tags
    text = re.sub(r'\[sound:[^\]]+\]', '', raw_html)

    # Convert block/line break tags to spaces for multiline texts
    text = re.sub(r'<(br|p|div|header|li)[^>]*>', ' ', text, flags=re.IGNORECASE)

    # Strip remaining HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)

    # Unescape HTML entities (&nbsp;, &amp;, etc.)
    text = html.unescape(text)

    # Normalize whitespace
    return ' '.join(text.split()).strip()
