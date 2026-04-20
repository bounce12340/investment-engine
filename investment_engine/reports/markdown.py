from __future__ import annotations

from importlib.resources import files

from jinja2 import Environment, FileSystemLoader, select_autoescape

from investment_engine.models import WeeklyReport


def render_weekly(report: WeeklyReport) -> str:
    template_dir = files("investment_engine.reports") / "templates"
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(disabled_extensions=("j2",)),
        trim_blocks=False,
        lstrip_blocks=False,
    )
    template = env.get_template("weekly.md.j2")
    return template.render(report=report)
