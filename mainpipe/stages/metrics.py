from __future__ import annotations
from typing import Dict, Any, List
from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt

class MetricsAggregator:
    def __init__(self, out_dir: Path):
        self.out_dir = out_dir
        self.total = 0
        self.kept = 0
        self.dropped = 0
        self.drop_reasons: Dict[str, int] = {}
        self.lang_counts: Dict[str, int] = {}
        self.pii_counts = {"email": 0, "ip": 0, "phone": 0}
        self.token_lens: List[int] = []
        self.toxicity_scores: List[float] = []

    def update(self, rec: Dict[str, Any]):
        self.total += 1

        lang = rec.get("lang")
        if lang:
            self.lang_counts[lang] = self.lang_counts.get(lang, 0) + 1

        pii = rec.get("pii", {})
        self.pii_counts["email"] += pii.get("email_count", 0)
        self.pii_counts["ip"] += pii.get("ip_count", 0)
        self.pii_counts["phone"] += pii.get("phone_count", 0)

        if rec.get("drop_reason") is None:
            self.kept += 1
            tok_len = rec.get("token_len")
            if tok_len:
                self.token_lens.append(tok_len)

            tox = rec.get("toxicity")
            if tox is not None:
                self.toxicity_scores.append(float(tox))
        else:
            self.dropped += 1
            reason = rec["drop_reason"]
            self.drop_reasons[reason] = self.drop_reasons.get(reason, 0) + 1

    def finalize(self):
        self.out_dir.mkdir(parents=True, exist_ok=True)
        out_json = self.out_dir / "metrics.json"
        data: Dict[str, Any] = {
            "total_records": self.total,
            "kept_records": self.kept,
            "dropped_records": self.dropped,
            "drop_reason_counts": self.drop_reasons,
            "language_counts": self.lang_counts,
            "pii_summary": self.pii_counts,
        }

        if self.token_lens:
            arr = np.array(self.token_lens)
            data["token_len_summary"] = {
                "mean": float(arr.mean()),
                "p50": float(np.percentile(arr, 50)),
                "p90": float(np.percentile(arr, 90)),
                "p99": float(np.percentile(arr, 99)),
                "max": int(arr.max()),
            }

        if self.toxicity_scores:
            arr_t = np.array(self.toxicity_scores)
            data["toxicity_summary"] = {
                "count": int(len(arr_t)),
                "mean": float(arr_t.mean()),
                "p50": float(np.percentile(arr_t, 50)),
                "p90": float(np.percentile(arr_t, 90)),
                "p99": float(np.percentile(arr_t, 99)),
                "max": float(arr_t.max()),
            }

        with out_json.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        if self.token_lens:
            import matplotlib
            matplotlib.use("Agg")
            plt.figure(figsize=(8, 5))
            plt.hist(self.token_lens, bins=50)
            plt.title("Token Length Distribution")
            plt.xlabel("token_len")
            plt.ylabel("count")
            plt.tight_layout()
            plt.savefig(self.out_dir / "token_len_hist.png")
            plt.close()
