import typer
import httpx
import time
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

app = typer.Typer(help="Trigger generic web scraping jobs")
console = Console()

API_BASE = "http://localhost:8000"

@app.command("run")
def run_scrape(
    url: str = typer.Option(..., "--url", help="URL to scrape"),
    prompt: str = typer.Option(..., "--prompt", help="Extraction prompt"),
    mode: str = typer.Option("auto", "--mode", help="Scrape mode: auto|static|dynamic"),
    wait: bool = typer.Option(True, "--wait", help="Wait for job completion"),
):
    """Submits a new scraping job to the Scapper FastAPI backend."""
    console.print(f"[bold pink]Submitting scrape job for:[/bold pink] {url}")
    
    payload = {"url": url, "prompt": prompt, "mode": mode}
    
    try:
        with httpx.Client(timeout=30) as client:
            resp = client.post(f"{API_BASE}/scrape", json=payload)
            resp.raise_for_status()
            data = resp.json()
            job_id = data.get("job_id")
            console.print(f"[bold green]Job Created successfully![/bold green] Job ID: [cyan]{job_id}[/cyan]")

            if not wait:
                return

            # Poll for completion
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                task = progress.add_task(description="Scraping & Groq LLM parsing in progress...", total=None)
                while True:
                    time.sleep(2)
                    job_resp = client.get(f"{API_BASE}/jobs/{job_id}")
                    if job_resp.status_code == 200:
                        job_data = job_resp.json()
                        status = job_data.get("status")
                        if status == "completed":
                            progress.update(task, description="Completed!")
                            console.print("\n[bold green]✓ Scraping Complete![/bold green]")
                            console.print_json(data=job_data.get("result", {}))
                            break
                        elif status in ("failed", "blocked"):
                            console.print(f"\n[bold red]✗ Job {status}:[/bold red] {job_data.get('error_message')}")
                            break

    except Exception as e:
        console.print(f"[bold red]Error communicating with API backend:[/bold red] {e}")
