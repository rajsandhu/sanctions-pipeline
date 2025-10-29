from pathlib import Path
import csv
import json


def screen_names(input_csv: str, entities_jsonl: str, output_csv: str) -> int:
    """
    Process CSV rows against JSONL entities file to match names.

    Args:
        input_csv: Path to input CSV file containing names to match
        entities_jsonl: Path to JSONL file containing entity definitions
        output_csv: Path to output CSV file with matched results

    Returns:
        int: Number of successful matches found
    """
    # Load entities from JSONL file
    ents = []
    p = Path(entities_jsonl)
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            ents.append(json.loads(line))

    # Precompute lowercase names for matching efficiency
    names = [((e.get("name") or "").strip().lower(), e) for e in ents]

    matched = 0

    # Set up input and output paths
    pin = Path(input_csv)
    pout = Path(output_csv)
    pout.parent.mkdir(parents=True, exist_ok=True)

    # Process CSV files
    with (
        pin.open("r", encoding="utf-8", newline="") as fin,
        pout.open("w", encoding="utf-8", newline="") as fout,
    ):
        reader = csv.DictReader(fin)
        fieldnames = list(reader.fieldnames or []) + ["match_name", "match_schema"]
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()

        # Process each row and match names
        for row in reader:
            q = (row.get("name") or "").strip().lower()
            hit = None

            if q:
                for n, ent in names:
                    if q and n and q in n:  # case-insensitive substring match
                        hit = ent
                        break

            row["match_name"] = hit.get("name", "") if hit else ""
            row["match_schema"] = hit.get("schema", "") if hit else ""

            writer.writerow(row)
            if hit:
                matched += 1

    return matched
