import json  # For parsing JSON output from transform functions
from sanctions_pipeline.transform import (
    transform_to_simple_jsonl,
    transform_csv_to_ftm,
)  # Functions we're testing


def test_transform_to_simple_jsonl_dfat_like(tmp_path):
    """Test transform with DFAT-like columns (Name of Individual or Entity, etc.)."""
    # tmp_path is a pytest fixture - gives us a temporary directory that's cleaned up after the test

    # Create a minimal CSV with DFAT column names (same as the real DFAT file)
    input_csv = tmp_path / "dfat_sample.csv"
    input_csv.write_text(
        "Reference,Name of Individual or Entity,Type,Committees,Listing Information\n"  # Header row
        "1,John Doe,Individual,1988 (Taliban),Listed by UN on 2020-01-01\n"  # Person entity
        "2,ACME Corp,Entity,ISIL,Listed by UN on 2019-05-15\n"  # Organization entity
    )

    # Define where the output JSONL will be written
    output_jsonl = tmp_path / "entities.jsonl"

    # Run the transform function (this is what we're testing)
    count = transform_to_simple_jsonl(str(input_csv), str(output_jsonl))

    # Verify it processed both rows
    assert count == 2

    # Read the output file and split into individual JSON lines
    lines = output_jsonl.read_text().strip().split("\n")
    assert len(lines) == 2  # Should have exactly 2 entities

    # Parse the first entity (John Doe)
    entity1 = json.loads(lines[0])  # Convert JSON string to Python dict
    assert entity1["name"] == "John Doe"  # Check name was extracted correctly
    assert entity1["schema"] == "Person"  # Should be Person because Type=Individual
    assert "1988 (Taliban)" in entity1["notes"]  # Check program/committee was captured
    assert (
        "Listed by UN on 2020-01-01" in entity1["notes"]
    )  # Check listing info was captured

    # Parse the second entity (ACME Corp)
    entity2 = json.loads(lines[1])
    assert entity2["name"] == "ACME Corp"  # Check name
    assert (
        entity2["schema"] == "Organization"
    )  # Should be Organization (not Individual)


def test_transform_csv_to_ftm_dfat_like(tmp_path):
    """Test FTM transform with DFAT-like columns."""
    # This tests the FollowTheMoney (FTM) output format instead of simple JSONL

    # Create a minimal DFAT-like CSV (just one row to keep test simple)
    input_csv = tmp_path / "dfat_sample.csv"
    input_csv.write_text(
        "Reference,Name of Individual or Entity,Type,Committees,Listing Information\n"
        "1,Jane Smith,Individual,1988 (Taliban),Listed by UN on 2021-03-10\n"
    )

    # Define output path for FTM JSONL
    output_jsonl = tmp_path / "ftm_entities.jsonl"

    # Run the FTM transform function
    count = transform_csv_to_ftm(str(input_csv), str(output_jsonl))

    # Verify it processed 1 row
    assert count == 1

    # Read and parse the FTM output
    lines = output_jsonl.read_text().strip().split("\n")
    entity = json.loads(lines[0])

    # FTM entities have a specific structure: id, schema, properties
    # This is different from simple JSONL which has: id, schema, name, notes
    assert "id" in entity  # FTM entities have deterministic IDs
    assert entity["schema"] == "Person"  # Schema type
    assert "name" in entity["properties"]  # FTM stores data in 'properties' dict
    assert "Jane Smith" in entity["properties"]["name"]  # Name should be in a list
