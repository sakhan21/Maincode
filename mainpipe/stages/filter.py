from __future__ import annotations
from typing import Iterable, Dict, Any
import re

def _markup_ratio(text: str) -> float:
    if not text:
        return 0.0
    markup_chars = sum(1 for ch in text if ch in "<>{}[]/")
    return markup_chars / max(1, len(text))

def _unique_char_ratio(text: str) -> float:
    if not text:
        return 0.0
    return len(set(text)) / len(text)

def _has_long_repeats(text: str, thresh: int = 8) -> bool:
    if not text:
        return False
    last = None
    run = 0
    for ch in text:
        if ch == last:
            run += 1
            if run >= thresh:
                return True
        else:
            last = ch
            run = 1
    return False

def apply_quality_filters(records: Iterable[Dict[str, Any]], cfg: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    filt_cfg = cfg.get("filter", {})
    min_chars = int(filt_cfg.get("min_chars", 160))
    max_chars = int(filt_cfg.get("max_chars", 20000))
    max_markup_ratio = float(filt_cfg.get("max_markup_ratio", 0.15))
    min_unique_char_ratio = float(filt_cfg.get("min_unique_char_ratio", 0.10))

    for rec in records:
        if rec.get("drop_reason") is not None:
            yield rec
            continue

        text = rec["text"]
        n = len(text)

        if n < min_chars:
            rec["drop_reason"] = "too_short"
        elif n > max_chars:
            rec["drop_reason"] = "too_long"
        elif _markup_ratio(text) > max_markup_ratio:
            rec["drop_reason"] = "markup_heavy"
        elif _unique_char_ratio(text) < min_unique_char_ratio:
            rec["drop_reason"] = "low_char_diversity"
        elif _has_long_repeats(text):
            rec["drop_reason"] = "long_repeats"

        yield rec
