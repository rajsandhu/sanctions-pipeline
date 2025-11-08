from pathlib import Path  # File path handling
from unittest.mock import (
    patch,
    MagicMock,
)  # For mocking requests.get (no real network calls in tests)
import sys  # To manipulate sys.path for importing the crawler script

# Import the crawler module
# Since crawl_dfat.py is in scripts/, we need to add it to the import path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import crawl_dfat  # The crawler script we're testing


def test_crawl_dfat_downloads_file(tmp_path, monkeypatch):
    """Test that crawl_dfat downloads and saves the XLSX file."""
    fake_xlsx_content = b"x" * 6000  # Make it > 5000 bytes to pass validation

    mock_response = MagicMock()
    mock_response.content = fake_xlsx_content
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()

    with patch("crawl_dfat.requests.get", return_value=mock_response) as mock_get:
        output_path = tmp_path / "test_dfat.xlsx"
        crawl_dfat.main(str(output_path))

        assert output_path.exists()
        assert output_path.read_bytes() == fake_xlsx_content
        mock_get.assert_called_once()
