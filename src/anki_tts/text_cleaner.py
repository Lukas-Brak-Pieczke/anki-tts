import html
import re

"""
Text Normalization Utility.

Cleans HTML markup, unescapes HTML entities, removes existing Anki `[sound:...]` tags,
and normalizes whitespace to prepare card field text for speech synthesis.
"""


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
