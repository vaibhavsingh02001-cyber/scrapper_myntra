import typer
import httpx
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Manage and inspect scraping jobs")
console = Console()

API_BASE = "http://localhost:8000"

@app.command("list")
def list_jobs():
    """Lists all submitted jobs with status and creation timestamp."""
    try:
        with httpx.Client(timeout=10) as client:
            resp = client.get(f"{API_BASE}/jobs")
            resp.raise_for_status()
            jobs = resp.json()

            table = Table(title="Scapper — Scraping Jobs")
            table.add_column("Job ID", style="cyan", no_wrap=True)
            table.add_column("Status", style="bold")
            table.add_column("URL", style="dim")
            table.add_column("Created At", style="green")

            for job in jobs:
                status = job.get("status", "unknown")
                status_style = (
                    "[green]completed[/green]" if status == "completed"
                    else "[yellow]running[/yellow]" if status == "running"
                    else "[red]failed[/red]" if status == "failed"
                    else "[dim]queued[/dim]"
                )
                url_str = (job.get("url") or "")[:40]
                table.add_row(
                    job.get("job_id", "")[:8] + "...",
                    status_style,
                    url_str,
                    str(job.get("created_at", ""))[:19]
                )

            console.print(table)
    except Exception as e:
        console.print(f"[bold red]Error fetching jobs:[/bold red] {e}")


@app.command("get")
def get_job(job_id: str = typer.Argument(..., help="ID of job to inspect")):
    """Inspect details and extracted JSON results for a job."""
    try:
        with httpx.Client(timeout=10) as client:
            resp = client.get(f"{API_BASE}/jobs/{job_id}")
            resp.raise_for_status()
            data = resp.json()
            console.print_json(data=data)
    except Exception as e:
        console.print(f"[bold red]Error fetching job '{job_id}':[/bold red] {e}")


@app.command("delete")
def delete_job(job_id: str = typer.Argument(..., help="ID of job to delete")):
    """Deletes a job and its associated results."""
    try:
        with httpx.Client(timeout=10) as client:
            resp = client.delete(f"{API_BASE}/jobs/{job_id}")
            resp.raise_for_status()
            console.print(f"[bold green]Job '{job_id}' deleted successfully.[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error deleting job '{job_id}':[/bold red] {e}")
