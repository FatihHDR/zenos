"""FastAPI dependencies for the Zenos API."""

from fastapi import Request

from generation.pipeline import GroundedQAPipeline


def build_default_pipeline() -> GroundedQAPipeline:
    """Build the real pipeline (loads the embedding + reranker models)."""
    return GroundedQAPipeline()


def get_pipeline(request: Request) -> GroundedQAPipeline:
    """Return the app-wide pipeline, building it lazily on first use.

    Loading the models is expensive, so the pipeline is created once and cached
    on ``app.state``. Tests can inject a fake by setting ``app.state.pipeline``
    before the first request.
    """
    pipeline = getattr(request.app.state, "pipeline", None)
    if pipeline is None:
        pipeline = build_default_pipeline()
        request.app.state.pipeline = pipeline
    return pipeline
