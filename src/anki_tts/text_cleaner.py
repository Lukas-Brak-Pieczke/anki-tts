import html
import re

def clean_text(text: str) -> str:
    if not text:
        return ""

    # Remove HTML tags
    cleaned = re.sub(r"<[^>]+>", "", text)

    # Unescape HTML entities (&nbsp;, &amp;, etc.)
    cleaned = html.unescape(cleaned)

    # Remove existing sound tags [sound:...]
    cleaned = re.sub(r"\[sound:[^\]]+\]", "", cleaned)

    # Collapse multiple spaces into one
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned
