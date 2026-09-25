"""Pytest configuration and fixtures for the Zenos test suite."""

import sys
from pathlib import Path

# Make `src/` importable during tests without installing the package
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
