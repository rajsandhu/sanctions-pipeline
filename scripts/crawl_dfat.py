import sys
from pathlib import Path
import requests

DFAT_URL = "https://www.dfat.gov.au/sites/default/files/Australian_Sanctions_Consolidated_List.xlsx"


def main(out_path="data/raw/dfat_consolidated.xlsx"):
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    headers = {"User-Agent": "sanctions-pipeline/0.1 (+github)"}
    r = requests.get(DFAT_URL, timeout=60, headers=headers)
    if r.status_code != 200 or len(r.content) < 5000:
        raise SystemExit(f"Download failed: status={r.status_code}")
    p.write_bytes(r.content)
    print(f"Saved {p}")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "data/raw/dfat_consolidated.xlsx"
    main(out)
