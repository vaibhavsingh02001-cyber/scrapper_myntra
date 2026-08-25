import click

# Patch Click 8.1+ parameter signature compatibility for Typer
_orig_make_metavar = click.Parameter.make_metavar
def _patched_make_metavar(self, ctx=None):
    try:
        return _orig_make_metavar(self, ctx)
    except TypeError:
        return _orig_make_metavar(self)
click.Parameter.make_metavar = _patched_make_metavar

import typer
from cli.commands import scrape, jobs, query, export, discovery

app = typer.Typer(
    name="scapper",
    help="Scapper & Myntra/AJIO AI Discovery Engine — Intelligent Web & Review Research Platform",
    add_completion=False,
    pretty_exceptions_enable=False
)

app.add_typer(scrape.app, name="scrape", help="Generic web page scraping")
app.add_typer(jobs.app, name="jobs", help="Scraping jobs management")
app.add_typer(query.app, name="query", help="Natural language queries on scraped data")
app.add_typer(export.app, name="export", help="Dataset exports to JSON/CSV")
app.add_typer(discovery.app, name="discovery", help="Myntra/AJIO review collection & behavioral analysis")

if __name__ == "__main__":
    app()
