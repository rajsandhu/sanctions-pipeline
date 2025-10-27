from sanctions_pipeline.transform import transform_csv_to_ftm
import json


def test_transform_creates_entities(tmp_path):
    raw = tmp_path / "sdn.csv"
    raw.write_text(
        "sdnType,name,program,remarks\nIndividual,Jane Doe,SDGT,Test remark\n"
    )
    out = tmp_path / "entities.jsonl"
    n = transform_csv_to_ftm(str(raw), str(out))
    assert n == 1
    lines = out.read_text().strip().splitlines()
    assert len(lines) == 1
    entity = json.loads(lines[0])
    assert entity["name"] == "Jane Doe"
    assert entity["schema"] == "Person"
