"""Tests for the main module."""

from __future__ import annotations

import pytest

from detector.main import main


def test_main_output(capsys: pytest.CaptureFixture[str]) -> None:
    """Test main function output."""
    main()
    captured = capsys.readouterr()
    assert captured.out == "Hello from detector!\n"


def test_main_no_errors() -> None:
    """Test main function runs without errors."""
    # Should not raise any exceptions
    main()
