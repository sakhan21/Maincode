from __future__ import annotations
from typing import Iterable, Dict, Any
from pathlib import Path
import json
import hashlib

def _make_id(text: str, url: str | None) -> str:
    h = hashlib.sha256()
    h.update((url or "").encode("utf-8"))
    h.update(b"\n")
    h.update(text.encode("utf-8"))
    return h.hexdigest()

def load_raw(path: Path) -> Iterable[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            text = obj.get("text") or ""
            url = obj.get("url")
            rec_id = _make_id(text, url)
            rec = {
                "id": rec_id,
                "url": url,
                "raw_text": text,
                "text": text,
                "lang": None,
                "lang_score": None,
                "char_len": len(text),
                "token_len": None,
                "hash": None,
                "pii": {"email_count": 0, "ip_count": 0, "phone_count": 0},
                "toxicity": None,
                "drop_reason": None,
            }
            yield rec
