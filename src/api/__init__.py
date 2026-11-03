"""FastAPI app for the Zenos grounded Q&A pipeline.

Import the ASGI app as ``api.app:app`` (used by uvicorn and the Docker image).
This package intentionally does not re-export ``app`` — doing so would shadow
the ``api.app`` submodule with the FastAPI instance.
"""
