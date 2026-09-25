"""Script to initialize or reset Qdrant collection with dual dense and sparse indexing."""

import argparse
import sys
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from config import settings
from db.qdrant import QdrantManager

console = Console()


def setup_database(collection_name: str = None, recreate: bool = False, use_memory: bool = False):
    target_collection = collection_name or settings.qdrant_collection_name
    console.print(
        Panel.fit(
            f"[bold cyan]Zenos Qdrant Initialization[/bold cyan]\n"
            f"Collection: [yellow]{target_collection}[/yellow]\n"
            f"Dense Vector: [green]{settings.dense_vector_name}[/green] (dim: {settings.embedding_dimension})\n"
            f"Sparse Vector: [green]{settings.sparse_vector_name}[/green] (BM25 / Lexical)\n"
            f"Mode: {'In-Memory' if use_memory else f'{settings.qdrant_host}:{settings.qdrant_port}'}\n"
            f"Recreate: [bold {'red' if recreate else 'blue'}]{recreate}[/bold]",
            title="Database Setup",
        )
    )

    manager = QdrantManager(use_memory=use_memory)

    try:
        manager.init_collection(collection_name=target_collection, recreate=recreate)
        info = manager.get_collection_info(collection_name=target_collection)

        table = Table(title="Collection Details")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="magenta")

        table.add_row("Collection Name", target_collection)
        table.add_row("Status", str(info["status"]))
        table.add_row("Points Count", str(info["points_count"]))
        table.add_row("Vectors Config", str(info["vectors_config"]))
        table.add_row("Sparse Vectors Config", str(info["sparse_vectors_config"]))

        console.print(table)
        console.print("[bold green]✓ Qdrant collection successfully initialized and verified![/bold green]")
    except Exception as e:
        console.print(f"[bold red]✗ Failed to initialize collection: {e}[/bold red]")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize Qdrant collection for Zenos")
    parser.add_argument("--collection", type=str, default=None, help="Collection name")
    parser.add_argument("--recreate", action="store_true", help="Delete and recreate collection if it exists")
    parser.add_argument("--memory", action="store_true", help="Use in-memory Qdrant (for testing)")

    args = parser.parse_args()
    setup_database(collection_name=args.collection, recreate=args.recreate, use_memory=args.memory)
