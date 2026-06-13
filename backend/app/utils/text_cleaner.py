import re
import unicodedata


def clean_text(text: str) -> str:
    """Normalize raw extracted text into clean, readable text.

    Preserves Unicode (accents, bullets, em-dashes); strips only
    control/format junk. Rejoins end-of-line hyphenated words and
    collapses excess whitespace while keeping paragraph breaks.
    """
    if not text:
        return ""

    # Normalize Unicode form (keeps accents/bullets; folds NBSP, ligatures).
    text = unicodedata.normalize("NFKC", text)

    # Normalize line endings.
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Drop control/format/junk chars, but keep tab and newline.
    text = "".join(
        ch
        for ch in text
        if ch in ("\t", "\n") or not unicodedata.category(ch).startswith("C")
    )

    # Rejoin words broken by end-of-line hyphenation: "experi-\nence" -> "experience".
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)

    # Collapse runs of spaces/tabs into a single space.
    text = re.sub(r"[ \t]+", " ", text)

    # Trim each line.
    text = "\n".join(line.strip() for line in text.split("\n"))

    # Collapse 3+ blank lines into a single paragraph break.
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()