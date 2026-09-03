from pathlib import Path

import polars as pl
import typer
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from rich.console import Console
from rich.panel import Panel


app = typer.Typer(no_args_is_help=True)
console = Console()


@app.command()
def sample(output: Path = typer.Argument(Path("output/sales.csv"), help="CSV file to create.")) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "date,category,amount\n2026-09-01,books,120.50\n2026-09-01,coffee,18.90\n2026-09-02,books,89.90\n",
        encoding="utf-8",
    )
    console.print(f"[green]CSV written:[/green] {output}")


@app.command()
def analyze(
    csv_path: Path = typer.Argument(..., help="CSV file to analyze."),
    pdf: Path | None = typer.Option(None, "--pdf", help="Optional PDF output."),
) -> None:
    frame = pl.read_csv(csv_path)
    summary = frame.group_by("category").agg(pl.len().alias("rows"), pl.col("amount").sum().alias("total"))
    console.print(
        Panel.fit(
            f"Total CSV rows: [bold]{frame.height}[/bold]\n"
            f"Total columns: [bold]{frame.width}[/bold]\n"
            f"Grouped rows: [bold]{summary.height}[/bold]",
            title="Summary",
        )
    )
    console.print(summary)
    if pdf:
        pdf.parent.mkdir(parents=True, exist_ok=True)
        doc = canvas.Canvas(str(pdf), pagesize=letter)
        doc.drawString(72, 740, "Sales Report")
        y = 700
        for row in summary.to_dicts():
            doc.drawString(72, y, str(row))
            y -= 24
        doc.save()
        console.print(f"[green]PDF written:[/green] {pdf}")
