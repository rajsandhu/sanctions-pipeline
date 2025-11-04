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
    # monkeypatch is a pytest fixture that lets us temporarily replace functions

    # Create fake XLSX content (just some bytes to simulate a file)
    fake_xlsx_content = b"fake xlsx data"

    # Create a mock response object (simulates what requests.get returns)
    mock_response = MagicMock()  # MagicMock is a test double that records calls
    mock_response.content = fake_xlsx_content  # Set the fake content
    mock_response.raise_for_status = MagicMock()  # Mock the status check method

    # Replace requests.get with our mock (no real network call)
    with patch("crawl_dfat.requests.get", return_value=mock_response) as mock_get:
        # Define where the output should be saved (in our temp directory)
        output_path = tmp_path / "test_dfat.xlsx"

        # Run the crawler's main function
        crawl_dfat.main(str(output_path))

        # Verify requests.get was called with the correct URL
        mock_get.assert_called_once_with(
            "https://www.dfat.gov.au/sites/default/files/regulation8_consolidated.xlsx",
            timeout=60,
        )

        # Verify raise_for_status was called (checks for HTTP errors)
        mock_response.raise_for_status.assert_called_once()

        # Verify the file was created
        assert output_path.exists()  # File should exist

        # Verify the file contains the fake content we mocked
        assert output_path.read_bytes() == fake_xlsx_content
