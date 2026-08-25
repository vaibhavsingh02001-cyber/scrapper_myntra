import typer
import httpx
from rich.console import Console

app = typer.Typer(help="Export scraped data to JSON or CSV files")
console = Console()

API_BASE = "http://localhost:8000"

@app.command("run")
def export_data(
    job_id: str = typer.Option(..., "--job-id", help="Job ID to export"),
    format_type: str = typer.Option("json", "--format", help="json | csv"),
    output_path: str = typer.Option(..., "--output", help="Output file path"),
):
    """Downloads extracted dataset in JSON or CSV format."""
    console.print(f"[bold cyan]Downloading {format_type.upper()} export for job {job_id[:8]}...[/bold cyan]")
    try:
        with httpx.Client(timeout=30) as client:
            resp = client.get(f"{API_BASE}/export/{job_id}?format={format_type}")
            resp.raise_for_status()
            with open(output_path, "wb") as f:
                f.write(resp.content)
            console.print(f"[bold green]Saved export to {output_path} successfully![/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error downloading export:[/bold red] {e}")
