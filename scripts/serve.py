"""Run the Zenos FastAPI app (local dev or container).

Usage:
    python scripts/serve.py [--host 0.0.0.0] [--port 8000] [--reload]
"""

import argparse
import sys
from pathlib import Path

# Add src to sys.path so `api.app` is importable
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def main():
    parser = argparse.ArgumentParser(description="Serve the Zenos API with uvicorn")
    parser.add_argument("--host", default="0.0.0.0", help="Bind host (default 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Bind port (default 8000)")
    parser.add_argument("--reload", action="store_true", help="Auto-reload on code changes")
    args = parser.parse_args()

    import uvicorn

    uvicorn.run("api.app:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
