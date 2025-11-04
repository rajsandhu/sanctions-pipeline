import pytest  # Testing framework
from sanctions_pipeline.validate import validate_jsonl  # The function we're testing


def test_validate_jsonl_valid(
    tmp_path,
):  # tmp_path is a pytest fixture (temporary directory)
    f = tmp_path / "valid.jsonl"  # Create a temp file path
    f.write_text('{"name": "Alice"}\n{"name": "Bob"}\n')  # Write 2 valid JSON lines

    result = validate_jsonl(str(f), min_rows=1)  # Call your function

    assert result["total"] == 2  # Check it counted 2 records correctly


def test_validate_jsonl_bad_json(tmp_path):
    f = tmp_path / "bad.jsonl"
    f.write_text('{"name": "Alice"}\n{bad json}\n')  # Second line is broken JSON

    with pytest.raises(AssertionError, match="Bad JSON lines: 1"):  # Expect an error
        validate_jsonl(str(f))  # This should raise AssertionError


def test_validate_jsonl_min_rows(tmp_path):
    f = tmp_path / "few.jsonl"
    f.write_text('{"name": "Alice"}\n')  # Only 1 row

    with pytest.raises(AssertionError, match="Too few records: 1 < 5"):
        validate_jsonl(str(f), min_rows=5)  # Require 5 rows, but only have 1
