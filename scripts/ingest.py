"""CLI script to ingest documents, generate BGE-M3 dual embeddings, and load into Qdrant."""

import argparse
import sys
import time
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

from config import settings
from db.qdrant import QdrantManager
from embeddings.bge_m3 import BGEM3EmbeddingExtractor
from ingestion.chunker import TokenChunker
from ingestion.parser import DocumentParser
from ingestion.pipeline import IngestionPipeline

console = Console()


def run_ingestion(
    input_path: str,
    collection_name: str = None,
    recreate_db: bool = False,
    use_memory: bool = False,
):
    target_collection = collection_name or settings.qdrant_collection_name
    path = Path(input_path)

    if not path.exists():
        console.print(f"[bold red]Error: Path '{input_path}' does not exist.[/bold red]")
        sys.exit(1)

    console.print(
        Panel.fit(
            f"[bold cyan]Zenos Ingestion Pipeline (Phase 1)[/bold cyan]\n"
            f"Source Path: [yellow]{path.resolve()}[/yellow]\n"
            f"Collection: [magenta]{target_collection}[/magenta]\n"
            f"Chunk Size: [green]{settings.chunk_size} tokens[/green] (overlap: [green]{settings.chunk_overlap}[/green])\n"
            f"Embedding Model: [cyan]{settings.dense_model_name}[/cyan] (Dense + Sparse)\n"
            f"Qdrant Target: {'In-Memory' if use_memory else f'{settings.qdrant_host}:{settings.qdrant_port}'}",
            title="Ingestion Configuration",
        )
    )

    db_manager = QdrantManager(use_memory=use_memory)
    db_manager.init_collection(collection_name=target_collection, recreate=recreate_db)

    extractor = BGEM3EmbeddingExtractor()
    chunker = TokenChunker()
    parser = DocumentParser()
    pipeline = IngestionPipeline(
        db_manager=db_manager,
        embedding_extractor=extractor,
        chunker=chunker,
        parser=parser,
    )

    start_time = time.perf_counter()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Ingesting documents...", total=None)

        if path.is_file():
            results = [pipeline.ingest_file(path, collection_name=target_collection)]
        else:
            results = pipeline.ingest_directory(path, collection_name=target_collection)

        progress.update(task, completed=True)

    elapsed = time.perf_counter() - start_time

    table = Table(title="Ingestion Summary")
    table.add_column("Source Document", style="cyan")
    table.add_column("Doc ID", style="dim")
    table.add_column("Chunks", justify="right", style="green")
    table.add_column("Status", justify="center")
    table.add_column("Details", style="yellow")

    total_chunks = 0
    success_count = 0

    for res in results:
        status_str = "[bold green]SUCCESS[/bold green]" if res.success else "[bold red]FAILED[/bold red]"
        table.add_row(
            res.source_name,
            res.doc_id or "-",
            str(res.num_chunks),
            status_str,
            res.error_message or "Ingested & Indexed",
        )
        if res.success:
            total_chunks += res.num_chunks
            success_count += 1

    console.print(table)

    total_points = db_manager.count_points(target_collection)
    console.print(
        f"\n[bold green]✓ Ingestion completed in {elapsed:.2f}s.[/bold green] "
        f"Processed {len(results)} files ({success_count} succeeded), "
        f"generated {total_chunks} chunks. "
        f"Total points in collection '{target_collection}': [bold cyan]{total_points}[/bold cyan]."
    )


if __name__ == "__main__":
    cli_parser = argparse.ArgumentParser(description="Ingest documents into Zenos RAG DB")
    cli_parser.add_argument("--path", "-p", type=str, default="data/sample_docs", help="File or directory path to ingest")
    cli_parser.add_argument("--collection", "-c", type=str, default=None, help="Qdrant collection name")
    cli_parser.add_argument("--recreate", action="store_true", help="Recreate Qdrant collection before ingestion")
    cli_parser.add_argument("--memory", action="store_true", help="Use in-memory Qdrant database")

    args = cli_parser.parse_args()
    run_ingestion(
        input_path=args.path,
        collection_name=args.collection,
        recreate_db=args.recreate,
        use_memory=args.memory,
    )
