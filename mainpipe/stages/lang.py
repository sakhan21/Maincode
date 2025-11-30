from __future__ import annotations
from typing import Iterable, Dict, Any
from langdetect import detect_langs, DetectorFactory

DetectorFactory.seed = 42

def annotate_language(records: Iterable[Dict[str, Any]], cfg: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    lang_cfg = cfg.get("lang", {})
    min_prob = float(lang_cfg.get("min_prob", 0.9))
    min_chars = int(lang_cfg.get("min_chars", 100))

    for rec in records:
        text = rec["text"]
        if len(text) < min_chars:
            rec["drop_reason"] = rec.get("drop_reason") or "too_short_for_lang"
            yield rec
            continue
        try:
            langs = detect_langs(text)
            if not langs:
                rec["drop_reason"] = rec.get("drop_reason") or "lang_unknown"
            else:
                best = langs[0]
                rec["lang"] = best.lang
                rec["lang_score"] = best.prob
                if best.lang != "en" or best.prob < min_prob:
                    rec["drop_reason"] = rec.get("drop_reason") or "non_english"
        except Exception:
            rec["drop_reason"] = rec.get("drop_reason") or "lang_error"
        yield rec
