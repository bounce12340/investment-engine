from __future__ import annotations

import json
import os
import platform
import shutil
import sys
from pathlib import Path

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import IntPrompt, Prompt
from rich.table import Table

from investment_engine import scheduler
from investment_engine.analysis.kill_switches import triggered
from investment_engine.reports.obsidian import write_to_vault
from investment_engine.watcher import InvestmentWatcher

load_dotenv()

app = typer.Typer(help="Investment-Engine: triangulation valuation + kill-switches + Obsidian reports")
schedule_app = typer.Typer(help="Manage recurring runs via macOS launchd")
app.add_typer(schedule_app, name="schedule")

console = Console()

DEFAULT_REGISTRY = Path(__file__).resolve().parent.parent / "data" / "monitor-registry.json"
DEFAULT_VAULT = os.environ.get("OBSIDIAN_VAULT", "/Users/chunghsutsai/Vault")

WEEKDAY_NAMES = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]


@app.command()
def analyze(
    ticker: str = typer.Argument(..., help="Ticker symbol, e.g. NVDA"),
    registry: Path = typer.Option(DEFAULT_REGISTRY, "--registry", help="Path to monitor-registry.json"),
    no_price: bool = typer.Option(False, "--no-price", help="Skip fetching live price from yfinance"),
    no_performance: bool = typer.Option(False, "--no-performance", help="Skip fetching 3y history for performance stats"),
    no_technicals: bool = typer.Option(False, "--no-technicals", help="Skip technical indicators (RSI/MACD/MA)"),
    no_fundamentals: bool = typer.Option(False, "--no-fundamentals", help="Skip fundamentals reality-check"),
) -> None:
    """Print a console summary of the ticker's triangulation and kill-switch status."""
    watcher = InvestmentWatcher(registry)
    report = watcher.build_report(
        ticker.upper(),
        fetch_price=not no_price,
        fetch_performance=not no_performance,
        fetch_technicals=not no_technicals,
        fetch_fundamentals=not no_fundamentals,
    )

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

    if report.technicals:
        console.print()
        tech = report.technicals
        rsi_tag = ""
        if tech.rsi_14 >= 70:
            rsi_tag = " [red](overbought)[/red]"
        elif tech.rsi_14 <= 30:
            rsi_tag = " [green](oversold)[/green]"
        tech_table = Table(title="Technical Snapshot")
        tech_table.add_column("Indicator")
        tech_table.add_column("Value", justify="right")
        tech_table.add_row("Price", f"${tech.price:.2f}")
        tech_table.add_row("RSI(14)", f"{tech.rsi_14:.1f}{rsi_tag}")
        tech_table.add_row("MACD", f"{tech.macd:.3f}")
        tech_table.add_row("MACD signal", f"{tech.macd_signal:.3f}")
        tech_table.add_row("MACD histogram", f"{tech.macd_histogram:+.3f}")
        tech_table.add_row(
            "50-day MA",
            f"${tech.ma_50:.2f} ({tech.distance_from_ma50_pct:+.1f}%)",
        )
        tech_table.add_row(
            "200-day MA",
            f"${tech.ma_200:.2f} ({tech.distance_from_ma200_pct:+.1f}%)",
        )
        console.print(tech_table)

    if report.performance and report.performance.periods:
        console.print()
        perf_table = Table(title="Historical Performance")
        perf_table.add_column("Period")
        perf_table.add_column("Return", justify="right")
        perf_table.add_column("Vol", justify="right")
        perf_table.add_column("Sharpe", justify="right")
        perf_table.add_column("Sortino", justify="right")
        perf_table.add_column("Max DD", justify="right")
        perf_table.add_column("α vs VOO", justify="right")
        perf_table.add_column("β", justify="right")
        for p in report.performance.periods:
            perf_table.add_row(
                p.period,
                f"{p.annualized_return*100:+.1f}%",
                f"{p.annualized_volatility*100:.1f}%",
                f"{p.sharpe:.2f}",
                f"{p.sortino:.2f}",
                f"{p.max_drawdown*100:.1f}%",
                f"{p.alpha_vs_voo*100:+.1f}%",
                f"{p.beta_vs_voo:.2f}",
            )
        console.print(perf_table)

    if report.fundamentals:
        console.print()
        f = report.fundamentals
        fund_table = Table(title="Fundamentals Reality-Check")
        fund_table.add_column("Metric")
        fund_table.add_column("Value", justify="right")
        if f.trailing_pe is not None:
            fund_table.add_row("Trailing P/E", f"{f.trailing_pe:.2f}")
        if f.forward_pe is not None:
            fund_table.add_row("Forward P/E", f"{f.forward_pe:.2f}")
        if f.market_cap is not None:
            fund_table.add_row("Market Cap", f"${f.market_cap/1e9:.1f}B")
        if f.live_beta is not None:
            fund_table.add_row("Live β (yfinance)", f"{f.live_beta:.2f}")
        if f.dividend_yield_pct is not None:
            fund_table.add_row("Dividend yield", f"{f.dividend_yield_pct:.2f}%")
        if f.analyst_target_mean is not None:
            fund_table.add_row("Analyst target (mean)", f"${f.analyst_target_mean:,.2f}")
        if f.analyst_recommendation is not None:
            fund_table.add_row("Analyst rec (1=SB/5=SS)", f"{f.analyst_recommendation:.2f}")
        if f.registry_fcf is not None and f.live_fcf is not None:
            fund_table.add_row(
                "FCF registry / live / Δ",
                f"${f.registry_fcf/1e9:.1f}B / ${f.live_fcf/1e9:.1f}B / {f.fcf_delta_pct:+.1f}%",
            )
        if f.registry_shares is not None and f.live_shares is not None:
            fund_table.add_row(
                "Shares registry / live / Δ",
                f"{f.registry_shares/1e9:.2f}B / {f.live_shares/1e9:.2f}B / {f.shares_delta_pct:+.1f}%",
            )
        console.print(fund_table)
        for flag in f.flags:
            console.print(f"  {flag}")

    console.print()
    st = report.stress_test
    score_color = "green" if st.conviction_score >= 7 else "yellow" if st.conviction_score >= 4 else "red"
    st_table = Table(title="Thesis Stress Test")
    st_table.add_column("Metric")
    st_table.add_column("Value", justify="right")
    st_table.add_row("Conviction score", f"[bold {score_color}]{st.conviction_score:.1f} / 10[/bold {score_color}]")
    st_table.add_row("Bull / Bear", f"{st.bull_count} / {st.bear_count}")
    st_table.add_row("Kill-switches triggered", f"{st.kill_switches_triggered} / {st.kill_switches_total}")
    if st.bull_bear_ratio is not None:
        st_table.add_row("Bull/Bear ratio", f"{st.bull_bear_ratio:.2f}")
    console.print(st_table)

    for f in st.flags:
        icon = {"alert": "[red]🔴", "warning": "[yellow]⚠️ ", "info": "[green]ℹ️ "}[f.severity]
        close = "[/red]" if f.severity == "alert" else "[/yellow]" if f.severity == "warning" else "[/green]"
        console.print(f"{icon} {f.message}{close}")


@app.command()
def weekly(
    ticker: str = typer.Argument(..., help="Ticker symbol, e.g. NVDA"),
    registry: Path = typer.Option(DEFAULT_REGISTRY, "--registry", help="Path to monitor-registry.json"),
    vault: Path = typer.Option(Path(DEFAULT_VAULT), "--vault", help="Obsidian vault path"),
    no_price: bool = typer.Option(False, "--no-price", help="Skip fetching live price from yfinance"),
    no_performance: bool = typer.Option(False, "--no-performance", help="Skip fetching 3y history for performance stats"),
    no_technicals: bool = typer.Option(False, "--no-technicals", help="Skip technical indicators (RSI/MACD/MA)"),
    no_fundamentals: bool = typer.Option(False, "--no-fundamentals", help="Skip fundamentals reality-check"),
) -> None:
    """Generate a weekly Markdown report and write it into the Obsidian vault."""
    watcher = InvestmentWatcher(registry)
    report = watcher.build_report(
        ticker.upper(),
        fetch_price=not no_price,
        fetch_performance=not no_performance,
        fetch_technicals=not no_technicals,
        fetch_fundamentals=not no_fundamentals,
    )
    path = write_to_vault(report, vault)
    console.print(f"[green]✓[/green] Wrote weekly report: {path}")


def _parse_time(raw: str) -> tuple[int, int]:
    parts = raw.strip().split(":")
    if len(parts) != 2:
        raise ValueError(f"time must be HH:MM (got {raw!r})")
    hour, minute = int(parts[0]), int(parts[1])
    return hour, minute


def _require_macos() -> None:
    if platform.system() != "Darwin":
        raise typer.BadParameter(
            "schedule commands require macOS (launchd). Detected: " + platform.system()
        )


def _resolve_cli_path() -> str:
    path = shutil.which("investment-engine")
    if not path:
        # Fallback: sys.executable -m investment_engine.cli works but launchd
        # needs an absolute path to a binary. Build a venv-bin guess.
        guess = Path(sys.executable).parent / "investment-engine"
        if guess.exists():
            return str(guess)
        raise typer.BadParameter(
            "could not locate the installed `investment-engine` entry-point; "
            "run `pip install -e .` in your venv first"
        )
    return path


@schedule_app.command("create")
def schedule_create(
    name: str = typer.Option(None, "--name", help="Short label (e.g. morning-check). Lowercase + hyphen."),
    frequency: str = typer.Option(None, "--frequency", help="daily | weekly | monthly"),
    time: str = typer.Option(None, "--time", help="HH:MM (24h)"),
    weekday: int = typer.Option(None, "--weekday", help="0=Sun..6=Sat (weekly only)"),
    day: int = typer.Option(None, "--day", help="1-31 (monthly only)"),
    tickers: str = typer.Option(None, "--tickers", help="Comma-separated tickers; empty = all from registry"),
    command: str = typer.Option("weekly", "--command", help="weekly | analyze"),
    vault: Path = typer.Option(Path(DEFAULT_VAULT), "--vault"),
    registry: Path = typer.Option(DEFAULT_REGISTRY, "--registry"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation before loading into launchd"),
) -> None:
    """Create a recurring schedule. Missing fields are prompted interactively."""
    _require_macos()

    if not name:
        name = Prompt.ask("Schedule name (e.g. morning-check)")
    if not frequency:
        frequency = Prompt.ask(
            "Frequency", choices=["daily", "weekly", "monthly"], default="daily"
        )
    if not time:
        time = Prompt.ask("Time (HH:MM, 24h)", default="09:00")
    hour, minute = _parse_time(time)

    if frequency == "weekly" and weekday is None:
        console.print("Weekday: 0=Sun 1=Mon 2=Tue 3=Wed 4=Thu 5=Fri 6=Sat")
        weekday = IntPrompt.ask("Weekday", default=1)
    if frequency == "monthly" and day is None:
        day = IntPrompt.ask("Day of month (1-31)", default=1)

    available_tickers = scheduler.tickers_from_registry(registry)
    if tickers is None:
        tickers_str = Prompt.ask(
            f"Tickers (comma-separated, or blank for all {len(available_tickers)})",
            default="",
        )
    else:
        tickers_str = tickers
    ticker_list = [t.strip().upper() for t in tickers_str.split(",") if t.strip()]
    unknown = [t for t in ticker_list if t not in available_tickers]
    if unknown:
        raise typer.BadParameter(
            f"unknown ticker(s): {unknown}. Known: {available_tickers}"
        )

    spec = scheduler.ScheduleSpec(
        name=name,
        frequency=frequency,  # type: ignore[arg-type]
        hour=hour,
        minute=minute,
        weekday=weekday,
        day=day,
        tickers=ticker_list,
        vault=vault,
        command=command,  # type: ignore[arg-type]
    )
    resolved = ticker_list or available_tickers

    console.print()
    console.print("[bold]About to install:[/bold]")
    console.print(f"  label:     {spec.label}")
    console.print(f"  frequency: {frequency} at {hour:02d}:{minute:02d}")
    if frequency == "weekly":
        console.print(f"  weekday:   {WEEKDAY_NAMES[weekday]}")
    if frequency == "monthly":
        console.print(f"  day:       {day}")
    console.print(f"  tickers:   {', '.join(resolved)}")
    console.print(f"  command:   {command} --vault {vault}")
    console.print(f"  plist:     {scheduler.plist_path(name)}")
    console.print(f"  script:    {scheduler.script_path(name)}")
    console.print(f"  log:       {scheduler.log_path(name)}")

    if not yes and not typer.confirm("\nLoad into launchd?", default=True):
        console.print("[yellow]aborted[/yellow]")
        raise typer.Exit(code=1)

    cli_path = _resolve_cli_path()
    plist_file = scheduler.install(spec, cli_path, registry)
    console.print(f"[green]✓[/green] scheduled. plist: {plist_file}")


@schedule_app.command("list")
def schedule_list() -> None:
    """List installed investment-engine schedules."""
    _require_macos()
    jobs = scheduler.list_jobs()
    if not jobs:
        console.print("[dim]no schedules installed[/dim]")
        return

    table = Table(title="Scheduled jobs")
    table.add_column("Name")
    table.add_column("When")
    table.add_column("Log")
    for j in jobs:
        cal = j["calendar"]
        hour = cal.get("Hour", 0)
        minute = cal.get("Minute", 0)
        when = f"{hour:02d}:{minute:02d}"
        if "Weekday" in cal:
            when = f"{WEEKDAY_NAMES[cal['Weekday']]} {when}"
        elif "Day" in cal:
            when = f"day {cal['Day']} {when}"
        else:
            when = f"daily {when}"
        table.add_row(j["name"], when, j["log"])
    console.print(table)


@schedule_app.command("remove")
def schedule_remove(
    name: str = typer.Argument(..., help="Schedule name to remove"),
) -> None:
    """Unload and delete a schedule."""
    _require_macos()
    plist_deleted, script_deleted = scheduler.remove(name)
    if not plist_deleted and not script_deleted:
        console.print(f"[yellow]no such schedule:[/yellow] {name}")
        raise typer.Exit(code=1)
    console.print(f"[green]✓[/green] removed schedule {name}")


@schedule_app.command("show")
def schedule_show(name: str = typer.Argument(...)) -> None:
    """Show details of a single schedule (plist + wrapper script)."""
    _require_macos()
    pp = scheduler.plist_path(name)
    sp = scheduler.script_path(name)
    if not pp.exists():
        console.print(f"[yellow]no such schedule:[/yellow] {name}")
        raise typer.Exit(code=1)
    console.print(f"[bold]plist:[/bold] {pp}")
    console.print(pp.read_text())
    if sp.exists():
        console.print(f"[bold]script:[/bold] {sp}")
        console.print(sp.read_text())


if __name__ == "__main__":
    app()
