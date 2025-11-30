from __future__ import annotations
from pathlib import Path
from typing import Dict, Any
import json

from .config import load_config
from .utils_logging import setup_logging
from .stages import (
    ingest,
    clean,
    lang,
    filter as quality_filter,
    pii,
    toxicity,
    dedup,
    tokenize,
    shard,
    metrics,
)

def run(config_path: str) -> None:
    logger = setup_logging()
    cfg = load_config(config_path)

    raw_path = Path(cfg["data"]["raw_path"])
    base_out = Path(cfg["output"]["base_dir"])
    train_dir = base_out / cfg["output"].get("train_dir", "train")
    metrics_dir = base_out / cfg["output"].get("metrics_dir", "metrics")
    audit_path = base_out / cfg["output"].get("audit_path", "audit.jsonl")
    num_shards = int(cfg["output"].get("num_shards", 8))

    base_out.mkdir(parents=True, exist_ok=True)
    train_dir.mkdir(parents=True, exist_ok=True)
    metrics_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Reading raw data from %s", raw_path)
    logger.info("Writing outputs to %s", base_out)

    records = ingest.load_raw(raw_path)
    records = clean.clean_text(records)
    records = lang.annotate_language(records, cfg)
    records = quality_filter.apply_quality_filters(records, cfg)
    records = pii.annotate_pii(records, cfg)
    records = toxicity.annotate_toxicity(records, cfg)
    records = dedup.deduplicate(records)
    records = tokenize.tokenize_records(records, cfg)

    sharder = shard.Sharder(train_dir, num_shards)
    metrics_agg = metrics.MetricsAggregator(metrics_dir)

    kept = 0
    dropped = 0

    with audit_path.open("w", encoding="utf-8") as audit_f:
        for rec in records:
            metrics_agg.update(rec)
            audit_f.write(json.dumps(rec, ensure_ascii=False) + "\n")

            if rec.get("drop_reason") is None:
                sharder.write(rec)
                kept += 1
            else:
                dropped += 1

    sharder.close()
    metrics_agg.finalize()

    logger.info("Pipeline complete. Kept=%d, Dropped=%d", kept, dropped)
