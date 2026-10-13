"""Pytest configuration and fixtures for the Zenos test suite."""

import sys
from pathlib import Path

SRC_DIR = Path(__file__).parent.parent / "src"
EVAL_DIR = Path(__file__).parent.parent / "data" / "eval"

# Make `src/` importable during tests without installing the package
sys.path.insert(0, str(SRC_DIR))
# Make the evaluation dataset builder importable too
sys.path.insert(0, str(EVAL_DIR))