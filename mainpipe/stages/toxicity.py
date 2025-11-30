from __future__ import annotations
from typing import Dict, Any, Iterable, Optional
import random

try:
    from detoxify import Detoxify
    _HAS_DETOXIFY = True
except ImportError:
    Detoxify = None  # type: ignore
    _HAS_DETOXIFY = False

_model: Optional[Detoxify] = None


def _get_model() -> Detoxify:
    global _model
    if _model is None:
        _model = Detoxify("original")
    return _model


def annotate_toxicity(records: Iterable[Dict[str, Any]], cfg: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    tox_cfg = cfg.get("toxicity", {})
    enabled = tox_cfg.get("enabled", False)

    if not enabled or not _HAS_DETOXIFY:
        for rec in records:
            yield rec
        return

    max_chars = tox_cfg.get("max_chars", 4096)
    sample_frac = float(tox_cfg.get("sample_frac", 0.01))
    seed = tox_cfg.get("seed", 1234)

    random.seed(seed)
    model = _get_model()

    for rec in records:
        rec["toxicity"] = None
        if rec.get("drop_reason") is None:
            if random.random() < sample_frac:
                try:
                    text = rec["text"][:max_chars]
                    score = model.predict(text)["toxicity"]
                    rec["toxicity"] = float(score)
                except Exception:
                    rec["toxicity"] = None
        yield rec
