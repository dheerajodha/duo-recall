import pytest
from typer.testing import CliRunner
from duo_recall import app, VOCAB_FILE

runner = CliRunner()


def test_vocab_refresh_command_succeeds():
    """Test the vocab-refresh command creates the vocab file."""
    # Check if file exists, if so delete it for a clean test
    if VOCAB_FILE.exists():
        VOCAB_FILE.unlink()

    # Run the command
    result = runner.invoke(app, ["vocab-refresh", "--username", "IamSpaceCowboy"])

    # Assert that the command completed successfully and the file was created
    assert result.exit_code == 0
    assert "Successfully saved vocabulary to 'my-vocab.json'" in result.stdout
    assert VOCAB_FILE.exists()


def test_write_command_fails_without_file():
    """Test that the write command exits gracefully if the vocab file is missing."""
    # Ensure the file does not exist
    if VOCAB_FILE.exists():
        VOCAB_FILE.unlink()

    # Run the command
    result = runner.invoke(app, ["write"])

    # Assert that the command failed and gave the correct message
    assert result.exit_code == 1
    assert "'my-vocab.json' not found" in result.stdout
