import sys
from pathlib import Path
import requests

DFAT_URL = "https://www.dfat.gov.au/sites/default/files/regulation8_consolidated.xlsx"


def main(out_path="data/raw/dfat_consolidated.xlsx"):
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(DFAT_URL, timeout=60)
    r.raise_for_status()
    p.write_bytes(r.content)
    print(f"Saved {p}")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "data/raw/dfat_consolidated.xlsx"
    main(out)
