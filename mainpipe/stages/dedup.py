from __future__ import annotations
from typing import Iterable, Dict, Any, Set
import hashlib

def _normalise(text: str) -> str:
    text = " ".join(text.split())
    return text.lower().strip()

def _hash(text: str) -> str:
    h = hashlib.sha256()
    h.update(text.encode("utf-8"))
    return h.hexdigest()

def deduplicate(records: Iterable[Dict[str, Any]]) -> Iterable[Dict[str, Any]]:
    seen: Set[str] = set()
    for rec in records:
        norm = _normalise(rec["text"])
        h = _hash(norm)
        rec["hash"] = h
        if rec.get("drop_reason") is None:
            if h in seen:
                rec["drop_reason"] = "exact_dup"
            else:
                seen.add(h)
        yield rec
