from __future__ import annotations
from typing import Iterable, Dict, Any
import unicodedata
import re
from bs4 import BeautifulSoup

_whitespace_re = re.compile(r"\s+")

def _strip_html(text: str) -> str:
    if "<" in text and ">" in text:
        soup = BeautifulSoup(text, "lxml")
        return soup.get_text(" ", strip=True)
    return text

def _clean(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = "".join(ch for ch in text if ch.isprintable())
    text = _strip_html(text)
    text = _whitespace_re.sub(" ", text).strip()
    return text

def clean_text(records: Iterable[Dict[str, Any]]) -> Iterable[Dict[str, Any]]:
    for rec in records:
        text = rec.get("raw_text", "")
        cleaned = _clean(text)
        rec["text"] = cleaned
        rec["char_len"] = len(cleaned)
        yield rec
