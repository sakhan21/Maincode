from __future__ import annotations
from typing import Iterable, Dict, Any
import tiktoken

def tokenize_records(records: Iterable[Dict[str, Any]], cfg: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    tok_cfg = cfg.get("tokenizer", {})
    name = tok_cfg.get("name", "gpt2")
    enc = tiktoken.get_encoding(name)

    for rec in records:
        if rec.get("drop_reason") is None:
            tokens = enc.encode(rec["text"])
            rec["tokens"] = tokens
            rec["token_len"] = len(tokens)
        yield rec
