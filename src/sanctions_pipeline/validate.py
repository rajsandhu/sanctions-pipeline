from pathlib import Path
import json

__all__ = ["validate_jsonl"]


def validate_jsonl(path: str, min_rows: int = 1) -> dict:
    """Validates a JSONL file containing one JSON object per line."""

    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")

    total = 0
    bad_json = 0

    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            try:
                json.loads(line)
                total += 1
            except Exception:
                bad_json += 1

    if bad_json > 0:
        raise AssertionError(f"Bad JSON lines: {bad_json}")

    if total < min_rows:
        raise AssertionError(f"Too few records: {total} < {min_rows}")

    return {"total": total}
