
# mainpipe – Take-Home Data Pipeline Report

This report explains the architecture, design decisions, trade-offs made for **mainpipe** LLM pre-training data pipeline.

---

# 1. Executive Summary

This pipeline implements a realistic, modular, streaming text-preprocessing system capable of:

- Cleaning messy web text  
- Detecting English and filtering noisy samples  
- Applying quality heuristics  
- Annotating PII  
- Optional sampled toxicity scoring  
- Deduplicating  
- Tokenising with GPT-2 BPE  
- Sharding into training-ready files  
- Producing rich metrics and inspection artefacts  

The architecture scales naturally to Spark/Ray for large datasets.

---

# 2. Goals & Problem Framing

Modern LLMs require:

- Clean, high-quality text  
- Low-noise, coherent English  
- PII reduction  
- Safety signals  
- Tokenised output in training-ready format  

The evaluation rubric focuses on:

- Deduplication  
- Noise/Integrity  
- Linguistics (perplexity proxy)  
- Safety (PII + toxicity)  
- Coverage  
- Throughput  

The pipeline is aligned with these criteria.

---

# 3. Data Model

Each record flowing through the pipeline is:

```json
{
  "id": "...",
  "url": "...",
  "raw_text": "...",
  "text": "...",
  "lang": "en",
  "lang_score": 0.99,
  "pii": {...},
  "toxicity": null,
  "drop_reason": null,
  "token_len": 128,
  "tokens": [...]
}
```

---

# 4. Pipeline Architecture

```
Ingest → Clean → Lang → Filter → PII → Toxicity → Dedup → Tokenize → Shard → Metrics
```

All stages are **streaming generators**, enabling memory efficiency.

---

# 5. Ingest & Cleaning

### Ingest
- JSONL reader  
- Normalised schema  
- Deterministic SHA-256 ID generation  

### Cleaning
- Unicode NFKC  
- Remove non-printables  
- Strip HTML  
- Collapse whitespace  

---

# 6. Language Detection

- `langdetect` with deterministic seed  
- Drops:
  - Short text (<100 chars)  
  - Non-English  
  - Low-confidence English (<0.9)  

---

# 7. Quality Filtering

Heuristics include:

- **Minimum characters = 160**  
- Max characters = 20k  
- Markup ratio threshold  
- Character diversity threshold  
- Repeated character detection  

This improves:
- **Noise/Integrity**
- **Linguistics** (lower perplexity)

---

# 8. Minimum Character Length (160)

Rationale:

- Removes tweets and noisy fragments  
- Improves perplexity of small LMs  
- Encourages paragraph-level coherence  
- Matches industrial LLM preprocessing practices  

---

# 9. PII Detection

Regex detection of:

- Emails  
- IP addresses  
- Phone numbers  

Counts stored in `pii` field.  
Optional dropping is supported.

---

# 10. Toxicity (Sampled)

Disabled by default for local execution.

If enabled:

- Scores only *kept* records  
- Samples 1%  
- Uses Detoxify  
- Stores scores in `rec["toxicity"]`  
- Logs aggregated statistics in `metrics.json`

---

# 11. Deduplication

- Normalise text → lowercase + whitespace collapse  
- SHA-256 hashing  
- First occurrence kept  
- Subsequent occurrences marked as `exact_dup`

Satisfies the **deduplication** requirement.

---

# 12. Tokenisation (GPT-2 BPE via TikToken)

Chosen because:

- Very fast (Rust backend)  
- Stable vocabulary  
- Used in real GPT models  
- Ideal for perplexity evaluation  

Outputs:
- `tokens`
- `token_len`

---

# 13. Sharding

- Hash(id) % num_shards  
- Uniform distribution  
- Deterministic ordering  
- Training-ready JSONL shards  

---

# 14. Metrics & Audit

### metrics.json includes:
- Total/kept/dropped  
- Drop reason counts  
- Language distribution  
- PII summary  
- Token distribution  
- (Optional) Toxicity summary  

### token_len_hist.png
Token length histogram.

### audit.jsonl
Full record-level traceability.

---

# 15. Throughput & Performance

Optimisations:

- Streaming pipeline  
- No Detoxify in local mode  
- Fast GPT-2 tokeniser  
- Early filtering reduces work in later stages  
- Deterministic seeding  

---

# 16. Scalability Plan

For large-scale corpora:

- Implement Spark/Ray runners  
- Partition by dedup hash  
- Use Parquet checkpoints  
- Coalesce small files  
- GPU batch tokenisation  
- Offload toxicity scoring to separate worker pool  

---

# 17. Future Extensions

- Near-duplicate detection (MinHash, LSH)  
- ML-based PII models  
- Domain mixture weighting  
- Perplexity-based adaptive filtering  

---

# 18. Conclusion

This pipeline is a clean and production-inspired for LLM pre-training. It balances:

- Practicality  
- Observability  
- Reproducibility  
- Engineering hygiene  
- Scalability  

