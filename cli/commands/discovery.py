import typer
import httpx
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Myntra AI Discovery Engine CLI")
console = Console()

API_BASE = "http://localhost:8000"

@app.command("collect")
def trigger_collection(
    platform: str = typer.Option("google_play", "--platform", help="google_play | app_store | reddit | all"),
    app_name: str = typer.Option("myntra", "--app", help="myntra | all"),
    max_reviews: int = typer.Option(10000, "--max-reviews", help="Cap per app"),
):
    """Triggers review scraper collection pipeline across Play Store, App Store, or Reddit."""
    console.print(f"[bold pink]Triggering review collection for {platform} → {app_name}...[/bold pink]")
    try:
        with httpx.Client(timeout=10) as client:
            resp = client.post(f"{API_BASE}/collect/{platform}?app={app_name}&max_reviews={max_reviews}")
            resp.raise_for_status()
            data = resp.json()
            console.print(f"[bold green]Collection Run Started![/bold green] Run ID: [cyan]{data.get('run_id')}[/cyan]")
    except Exception as e:
        console.print(f"[bold red]Error triggering collection:[/bold red] {e}")


@app.command("analyze")
def trigger_analysis(
    use_llm: bool = typer.Option(True, "--use-llm", help="Enable Groq LLM deep classification"),
):
    """Triggers Dual-Engine classification & updates themes_summary.json artifact."""
    console.print("[bold purple]Running Dual-Engine classification (Keyword Regex + Groq LLM)...[/bold purple]")
    try:
        with httpx.Client(timeout=10) as client:
            resp = client.post(f"{API_BASE}/analyze/run?use_llm={str(use_llm).lower()}")
            resp.raise_for_status()
            console.print("[bold green]Analysis job started! themes_summary.json artifact updating...[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error triggering analysis:[/bold red] {e}")


@app.command("summary")
def get_summary():
    """Displays high-level dataset metrics and 8-theme breakdown."""
    try:
        with httpx.Client(timeout=10) as client:
            resp = client.get(f"{API_BASE}/insights/summary")
            resp.raise_for_status()
            data = resp.json()

            if data.get("status") == "no_data":
                console.print("[yellow]No analysis artifacts found. Run 'scapper discovery analyze' first.[/yellow]")
                return

            console.print(f"\n[bold pink]Discovery Pulse Summary[/bold pink]")
            console.print(f"Total Reviews Analyzed: [bold white]{data.get('total_reviews')}[/bold white]")
            console.print(f"Dominant Theme: [bold cyan]{data.get('dominant_theme_label')}[/bold cyan] ({data.get('dominant_theme_count')} reviews)\n")

            table = Table(title="Top Behavioral Themes")
            table.add_column("Rank", style="dim")
            table.add_column("Theme Label", style="bold")
            table.add_column("Review Count", style="green")
            table.add_column("Percentage", style="yellow")

            for i, theme in enumerate(data.get("top_5_themes", []), 1):
                table.add_row(
                    str(i),
                    theme.get("label"),
                    str(theme.get("count")),
                    f"{theme.get('percentage')}%"
                )

            console.print(table)
    except Exception as e:
        console.print(f"[bold red]Error fetching summary:[/bold red] {e}")


@app.command("ask")
def ask_assistant(question: str = typer.Argument(..., help="Question about Myntra/AJIO wishlist behavior")):
    """Asks the Groq grounded Insights Assistant a natural language research question."""
    console.print(f"[bold cyan]Asking Groq Insights Assistant:[/bold cyan] {question}\n")
    try:
        with httpx.Client(timeout=30) as client:
            resp = client.post(f"{API_BASE}/insights/ask?question={question}")
            resp.raise_for_status()
            data = resp.json()
            console.print("[bold green]Answer (Grounded on themes_summary.json):[/bold green]")
            console.print(data.get("answer"))
    except Exception as e:
        console.print(f"[bold red]Error calling Insights Assistant:[/bold red] {e}")
