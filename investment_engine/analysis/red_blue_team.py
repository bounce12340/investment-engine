def format_arguments(bull_points: list[str], bear_points: list[str]) -> dict[str, list[str]]:
    return {"blue_team": list(bull_points), "red_team": list(bear_points)}
