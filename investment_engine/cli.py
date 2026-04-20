from __future__ import annotations

import os
from pathlib import Path

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from investment_engine.analysis.kill_switches import triggered
from investment_engine.reports.obsidian import write_to_vault
from investment_engine.watcher import InvestmentWatcher

load_dotenv()

app = typer.Typer(help="Investment-Engine: triangulation valuation + kill-switches + Obsidian reports")
console = Console()

DEFAULT_REGISTRY = Path(__file__).resolve().parent.parent / "data" / "monitor-registry.json"
DEFAULT_VAULT = os.environ.get("OBSIDIAN_VAULT", "/Users/chunghsutsai/Vault")


@app.command()
def analyze(
    ticker: str = typer.Argument(..., help="Ticker symbol, e.g. NVDA"),
    registry: Path = typer.Option(DEFAULT_REGISTRY, "--registry", help="Path to monitor-registry.json"),
    no_price: bool = typer.Option(False, "--no-price", help="Skip fetching live price from yfinance"),
) -> None:
    """Print a console summary of the ticker's triangulation and kill-switch status."""
    watcher = InvestmentWatcher(registry)
    report = watcher.build_report(ticker.upper(), fetch_price=not no_price)

    header = f"[bold cyan]{report.ticker}[/bold cyan] — {report.name} ({report.year}-W{report.week:02d})"
    if report.current_price is not None:
        header += f"  |  price ${report.current_price:.2f}"
    console.print(header)
    console.print()

    val_table = Table(title="Valuation Triangulation")
    val_table.add_column("Model")
    val_table.add_column("Target", justify="right")
    val_table.add_row("Two-Stage DCF", f"${report.valuation.dcf_target:.2f}")
    val_table.add_row("Probabilistic", f"${report.valuation.probabilistic_target:.2f}")
    val_table.add_row("Relative", f"${report.valuation.relative_target:.2f}")
    val_table.add_row("[bold]Triangulated[/bold]", f"[bold]${report.valuation.triangulated:.2f}[/bold]")
    console.print(val_table)

    if report.current_price is not None:
        upside = (report.valuation.triangulated / report.current_price - 1) * 100
        console.print(f"Upside vs current price: [bold]{upside:+.1f}%[/bold]")

    console.print()
    ks_table = Table(title="Kill-Switch Status")
    ks_table.add_column("Trigger")
    ks_table.add_column("Current", justify="right")
    ks_table.add_column("Threshold", justify="right")
    ks_table.add_column("Status")
    for k in report.kill_switches:
        status = "[red]🔴 TRIGGERED[/red]" if k.triggered else "[green]🟢 Safe[/green]"
        ks_table.add_row(k.name, str(k.current_value), f"{k.direction} {k.threshold}", status)
    console.print(ks_table)

    fired = triggered(report.kill_switches)
    if fired:
        console.print(f"\n[bold red]⚠ {len(fired)} kill-switch(es) triggered.[/bold red]")


@app.command()
def weekly(
    ticker: str = typer.Argument(..., help="Ticker symbol, e.g. NVDA"),
    registry: Path = typer.Option(DEFAULT_REGISTRY, "--registry", help="Path to monitor-registry.json"),
    vault: Path = typer.Option(Path(DEFAULT_VAULT), "--vault", help="Obsidian vault path"),
    no_price: bool = typer.Option(False, "--no-price", help="Skip fetching live price from yfinance"),
) -> None:
    """Generate a weekly Markdown report and write it into the Obsidian vault."""
    watcher = InvestmentWatcher(registry)
    report = watcher.build_report(ticker.upper(), fetch_price=not no_price)
    path = write_to_vault(report, vault)
    console.print(f"[green]✓[/green] Wrote weekly report: {path}")


if __name__ == "__main__":
    app()
