from __future__ import annotations
from typing import Dict, Any, List
from pathlib import Path
import json

class Sharder:
    def __init__(self, out_dir: Path, num_shards: int):
        self.out_dir = out_dir
        self.num_shards = num_shards
        self.files: List[Any] = []
        self.counts = [0 for _ in range(num_shards)]
        self._open_files()

    def _open_files(self):
        for i in range(self.num_shards):
            shard_path = self.out_dir / f"train_shard_{i:05d}.jsonl"
            f = shard_path.open("w", encoding="utf-8")
            self.files.append(f)

    def write(self, rec: Dict[str, Any]):
        sid = hash(rec["id"]) % self.num_shards
        line = json.dumps(
            {
                "id": rec["id"],
                "url": rec.get("url"),
                "tokens": rec.get("tokens", []),
            },
            ensure_ascii=False,
        )
        self.files[sid].write(line + "\n")
        self.counts[sid] += 1

    def close(self):
        for f in self.files:
            f.close()
        counts_path = self.out_dir / "shard_counts.json"
        with counts_path.open("w", encoding="utf-8") as f:
            json.dump(self.counts, f, indent=2)
