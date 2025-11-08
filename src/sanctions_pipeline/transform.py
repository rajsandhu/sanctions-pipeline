from pathlib import Path
import csv
import json
from typing import Dict, Iterable, Any
from followthemoney import model

# Try to import JSONEncoder from the most common location
try:
    from followthemoney.export.json import JSONEncoder
except Exception:
    # Fallback to alternate location for different FTM versions
    try:
        from followthemoney.export.jsonv2 import JSONEncoder
    except Exception:
        # Handle missing import gracefully
        JSONEncoder = None


# Deterministic ID helper (use FollowTheMoney's make_id if available)
try:
    # Attempt to use FollowTheMoney's built-in ID generator
    from followthemoney.helpers import make_id
except Exception:
    # Fallback implementation for deterministic ID generation
    def make_id(*parts):
        return "id-" + "-".join(str(p) for p in parts if p is not None)


try:
    import pandas as pd  # for .xlsx support
except ImportError:
    pd = None

__all__ = ["transform_to_simple_jsonl", "transform_csv_to_ftm"]


def _iter_rows_from_csv(path: Path) -> Iterable[Dict[str, Any]]:
    """
    Iterate over rows in a CSV file, yielding each row as a dictionary.

    Args:
        path: Path to the CSV file

    Yields:
        Dict[str, Any]: Dictionary representing each row in the CSV file
    """
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row


def _iter_rows_from_excel(path: Path) -> Iterable[Dict[str, Any]]:
    """
    Iterate over rows in an Excel file, yielding each row as a dictionary.

    Args:
        path: Path to the Excel file

    Yields:
        Dict[str, Any]: Dictionary representing each row in the Excel file

    Raises:
        RuntimeError: If pandas is not installed
    """
    if pd is None:
        raise RuntimeError(
            "pandas/openpyxl required for Excel. Run: uv add pandas openpyxl"
        )
    df = pd.read_excel(path, dtype=str).fillna("")
    for _, row in df.iterrows():
        yield {k: str(v) for k, v in row.items()}


def _row_iter(input_path: str) -> Iterable[Dict[str, Any]]:
    """
    Determine the appropriate iterator based on file extension.

    Args:
        input_path: Path to the input file

    Returns:
        Iterable[Dict[str, Any]]: Iterator over the file rows

    Raises:
        ValueError: If the file extension is not supported
    """
    inp = Path(input_path)
    ext = inp.suffix.lower()
    if ext in (".xlsx", ".xls"):
        return _iter_rows_from_excel(inp)
    return _iter_rows_from_csv(inp)


def _normalize_row(row: Dict[str, Any]) -> Dict[str, str]:
    """Normalize a row of data by cleaning and standardizing field names."""
    r = {
        str(k).strip().lower(): (str(v).strip() if v is not None else "")
        for k, v in row.items()
    }

    name = (
        r.get("name")
        or r.get("listed_name")
        or r.get("entity_name")
        or r.get("full_name")
        or r.get("individual_name")
        or r.get("name of individual or entity")
        or ""
    )
    sdn_type = (
        r.get("sdntype")
        or r.get("type")
        or r.get("entity_type")
        or r.get("individual")
        or ""
    )
    program = (
        r.get("program")
        or r.get("regime")
        or r.get("listing_program")
        or r.get("sanctions_regime")
        or r.get("committees")
        or ""
    )
    remarks = (
        r.get("remarks")
        or r.get("comments")
        or r.get("reason")
        or r.get("additional_information")
        or r.get("listing information")
        or ""
    )

    return {
        "name": name,
        "sdn_type": sdn_type,
        "program": program,
        "remarks": remarks,
    }


def transform_to_simple_jsonl(input_path: str, output_path: str) -> int:
    """
    Transform input CSV/Excel file to simple JSONL format.

    Args:
        input_path: Path to input CSV/Excel file
        output_path: Path where output JSONL file will be written

    Returns:
        int: Number of entities written

    Raises:
        Exception: If any error occurs during transformation
    """
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    count = 0

    try:
        with out.open("w", encoding="utf-8") as jsonl:
            for idx, row in enumerate(_row_iter(input_path)):
                r = _normalize_row(row)
                name = r["name"]
                if not name:
                    continue

                # Determine schema type
                schema = (
                    "Person"
                    if "individual" in (r["sdn_type"] or "").lower()
                    else "Organization"
                )

                # Create entity
                entity = {
                    "schema": schema,
                    "id": f"row-{idx}",
                    "name": name,
                }

                # Add notes if available
                notes = []
                if r["program"]:
                    notes.append(f"Program: {r['program']}")
                if r["remarks"]:
                    notes.append(r["remarks"])
                if notes:
                    entity["notes"] = "; ".join(notes)

                # Write to JSONL
                jsonl.write(json.dumps(entity) + "\n")
                count += 1
        return count

    except Exception as e:
        raise Exception(f"Error during transformation: {str(e)}")


def transform_csv_to_ftm(input_path: str, output_path: str) -> int:
    """
    Transform input CSV/Excel file to FollowTheMoney JSONL format.

    Args:
        input_path: Path to input CSV/Excel file
        output_path: Path where output JSONL file will be written

    Returns:
        int: Number of entities written

    Raises:
        Exception: If any error occurs during transformation
    """
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    count = 0

    try:
        with out.open("w", encoding="utf-8") as jsonl:
            for idx, row in enumerate(_row_iter(input_path)):
                r = _normalize_row(row)
                name = r["name"]
                if not name:
                    continue

                # Determine schema type
                schema = (
                    "Person"
                    if "individual" in (r["sdn_type"] or "").lower()
                    else "Organization"
                )

                # Create FTM entity
                # Create entity using appropriate method
                try:
                    # Attempt to create entity using modern FTM API
                    ent = model.make_entity(schema)
                except Exception:
                    # Fallback to EntityProxy for older FTM versions
                    from followthemoney.proxy import EntityProxy

                    ent = EntityProxy(model.get(schema))

                # Set a deterministic id (same input -> same id)
                ent.id = make_id("row", idx, name)

                # Add name property
                ent.add("name", name)

                # Prepare notes if available
                notes = []
                if r["program"]:
                    notes.append(f"Program: {r['program']}")
                if r["remarks"]:
                    notes.append(r["remarks"])

                # Add notes if any were found
                if notes:
                    ent.add("notes", "; ".join(notes))

                # Write entity to JSONL
                if JSONEncoder is not None:
                    # Use FollowTheMoney JSON encoder if available
                    jsonl.write(JSONEncoder.to_line(ent))
                else:
                    # Fallback to basic JSON representation
                    import json as _json

                    jsonl.write(_json.dumps(ent.to_dict()) + "\n")

                # Increment counter
                count += 1
        return count

    except Exception as e:
        raise Exception(f"Error during transformation: {str(e)}")
