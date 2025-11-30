from pathlib import Path
from typing import Dict, Any
import yaml

def load_config(path: str) -> Dict[str, Any]:
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return cfg
