from __future__ import annotations
from typing import Iterable, Dict, Any
import re

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
PHONE_RE = re.compile(r"\b\+?\d[\d\s\-]{7,}\b")

def annotate_pii(records: Iterable[Dict[str, Any]], cfg: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    pii_cfg = cfg.get("pii", {})
    drop_on_high = bool(pii_cfg.get("drop_on_high_pii", False))
    max_email = int(pii_cfg.get("max_email", 10))
    max_ip = int(pii_cfg.get("max_ip", 10))
    max_phone = int(pii_cfg.get("max_phone", 10))

    for rec in records:
        text = rec["text"]
        emails = EMAIL_RE.findall(text)
        ips = IP_RE.findall(text)
        phones = PHONE_RE.findall(text)

        rec["pii"] = {
            "email_count": len(emails),
            "ip_count": len(ips),
            "phone_count": len(phones),
        }

        if rec.get("drop_reason") is None and drop_on_high:
            if len(emails) > max_email or len(ips) > max_ip or len(phones) > max_phone:
                rec["drop_reason"] = "high_pii"

        yield rec
