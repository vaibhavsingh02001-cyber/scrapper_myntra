import typer
import httpx
from rich.console import Console

app = typer.Typer(help="Natural language queries on scraped datasets")
console = Console()

API_BASE = "http://localhost:8000"

@app.command("ask")
def query_job(
    job_id: str = typer.Option(..., "--job-id", help="Job ID containing data"),
    question: str = typer.Argument(..., help="Natural language question to ask Groq"),
):
    """Executes a natural language query against a scraped job's extracted JSON."""
    console.print(f"[bold cyan]Asking Groq LLM about Job {job_id[:8]}...[/bold cyan]")
    try:
        with httpx.Client(timeout=30) as client:
            resp = client.post(f"{API_BASE}/query", json={"job_id": job_id, "query": question})
            resp.raise_for_status()
            data = resp.json()
            console.print("\n[bold green]Groq Answer:[/bold green]")
            console.print(data.get("answer", "No answer received."))
    except Exception as e:
        console.print(f"[bold red]Error executing query:[/bold red] {e}")
