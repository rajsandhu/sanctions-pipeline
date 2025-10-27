from pathlib import Path
import csv
import json
from followthemoney import model

__all__ = ["transform_csv_to_ftm"]

def transform_csv_to_ftm(input_path: str, output_path: str) -> int:
    """
    Transform a CSV file to FollowTheMoney JSONL format.
    Expects columns like: name, sdnType (Individual/Entity/etc.), program, remarks.
    
    Args:
        input_path: Path to the input CSV file
        output_path: Path where the JSONL output will be written
        
    Returns:
        int: Number of entities transformed
    """
    count = 0
    
    try:
        # Convert string paths to Path objects
        inp = Path(input_path)
        out = Path(output_path)
        
        # Create parent directory if it doesn't exist
        out.parent.mkdir(parents=True, exist_ok=True)
        
        # Open input CSV and output JSONL files
        with inp.open("r", newline="", encoding="utf-8") as csv_file, \
             out.open("w", encoding="utf-8") as jsonl_file:
            reader = csv.DictReader(csv_file)
            
            for idx, row in enumerate(reader):
                # Get and clean the name
                name = (row.get("name") or "").strip()
                if not name:
                    continue
                
                # Get and clean the type
                sdn_type = (row.get("sdnType") or row.get("type") or "").strip().lower()
                schema = "Person" if sdn_type == "individual" else "Organization"
                
                # Create a basic FTM entity
                entity = {
                    "schema": schema,
                    "id": f"row-{idx}",
                    "name": name
                }
                
                # Add optional context fields into notes
                program = (row.get("program") or "").strip()
                remarks = (row.get("remarks") or "").strip()
                notes = []
                if program:
                    notes.append(f"Program: {program}")
                if remarks:
                    notes.append(remarks)
                if notes:
                    entity["notes"] = "; ".join(notes)
                
                # Write one JSON line per entity
                jsonl_file.write(json.dumps(entity) + "\n")
                count += 1
                
    except Exception as e:
        print(f"Error during transformation: {str(e)}")
        raise
    
    return count