
# mainpipe – LLM Pre-Training Data Pipeline (Take-Home Submission)

`mainpipe` is a modular, streaming, containerizable data preprocessing pipeline designed to transform raw web text into a high-quality, filtered, English-only, deduplicated, tokenised, and sharded dataset suitable for **LLM pre-training**.

This project is inspired by large-scale industrial pipelines used by OpenAI, Meta, and MosaicML, but intentionally simplified and self-contained so it can run on a **Windows 11 laptop**.

The pipeline demonstrates:

- System architecture and modular pipeline design  
- Data cleaning, noise filtering, and quality heuristics  
- Language detection and coverage tracking  
- Optional toxicity scoring (sample-mode)  
- Basic PII detection (email, IP, phone)  
- Tokenisation using GPT-2 BPE (TikToken)  
- Sharding and training-ready output generation  
- Observability: audit log, metrics, histograms  
- Scalability planning for Spark / Ray  
- Reproducibility via YAML configuration and deterministic seeds  

---

# 1. Project Structure

```
mainpipe/
  mainpipe/
    cli.py
    pipeline.py
    config.py
    utils_logging.py
    stages/
      ingest.py
      clean.py
      lang.py
      filter.py
      pii.py
      toxicity.py
      dedup.py
      tokenize.py
      shard.py
      metrics.py

  configs/
    local.yaml

  scripts/
    install_env.ps1

  run_pipeline.bat
  requirements.txt
  Dockerfile
  README.md
  REPORT.md
```

Raw data is expected here:

```
data/raw/sample.jsonl
```

Outputs are written to:

```
data/processed/
```

---

# 2. Installation (Windows 11)

## 2.1 Install Python 3.10+

Download from:

https://www.python.org/downloads/windows/

**Important:** Check the box  
 *“Add Python to PATH”*

Verify:

```powershell
python --version
```

---

## 2.2 Create the required data folder

```powershell
mkdir data
mkdir data/raw
```

Place your dataset at:

```
data/raw/sample.jsonl
```

---

## 2.3 Install dependencies (automatic method)

```powershell
.\scripts\install_env.ps1
```

This will:

- Create `venv/`
- Activate it
- Install dependencies
- Upgrade pip

---

## 2.4 Manual installation (alternative)

```powershell
python -m venv venv
.\env\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

# 3. Running the Pipeline (Windows One-Click)

Simply run:

```cmd
run_pipeline.bat
```

Or via Python:

```powershell
.\env\Scripts\Activate.ps1
python -m mainpipe.cli --config configs/local.yaml
```

---

# 4. Running with Docker (Optional)

## 4.1 Build the image

```powershell
docker build -t mainpipe .
```

## 4.2 Run the pipeline in a container

```powershell
docker run --rm -v "%cd%\data:/app/data" mainpipe --config configs/local.yaml
```

This mounts your Windows folder into the container.

---

# 5. Configuration (local.yaml)

```yaml
data:
  raw_path: data/raw/sample.jsonl

output:
  base_dir: data/processed
  train_dir: train
  audit_path: audit.jsonl
  metrics_dir: metrics
  num_shards: 8

lang:
  min_prob: 0.90
  min_chars: 100

filter:
  min_chars: 160
  max_chars: 20000
  max_markup_ratio: 0.15
  min_unique_char_ratio: 0.10

pii:
  drop_on_high_pii: false

toxicity:
  enabled: false
  max_chars: 4096
  sample_frac: 0.01
  seed: 1234

tokenizer:
  name: gpt2
```

---

# 6. Pipeline Stages

## 6.1 Ingest  
- Load raw JSONL  
- Normalise schema (id, text, url, metadata)

## 6.2 Cleaning  
- Unicode NFKC  
- Remove junk characters  
- Strip HTML  
- Collapse whitespace

## 6.3 Language Detection  
- Drops non-English / low-confidence samples

## 6.4 Quality Filters  
Includes:
- `min_chars = 160`
- Max markup ratio  
- Character diversity  
- Repeated character detection  

## 6.5 PII Detection  
Counts:
- Emails  
- IP addresses  
- Phone numbers  

## 6.6 Toxicity (Optional Sampling Mode)  
Disabled by default.  
If enabled:
- Scores only *kept* records  
- Samples 1%  
- Uses Detoxify  

## 6.7 Deduplication  
SHA-256 hashing of normalised text.

## 6.8 Tokenisation  
GPT-2 BPE via TikToken. Produces `tokens` and `token_len`.

## 6.9 Sharding  
Hash-based deterministic shard assignment.

## 6.10 Metrics & Audit  
- `metrics.json`  
- `token_len_hist.png`  
- `audit.jsonl`  

---

# 7. Output Structure

```
data/processed/
  train/
    train_shard_00000.jsonl
    ...
    shard_counts.json
  audit.jsonl
  metrics/
    metrics.json
    token_len_hist.png
```

---

# 8. Scaling Considerations

- Spark/Ray distributed version  
- Parquet checkpoints  
- Small-file mitigation  
- MinHash near-dup  
- Domain mixtures  
- GPU-based tokenisation  

---

