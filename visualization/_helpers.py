"""Shared helpers for visualization modules.

Provides:
- is_rtl_text
- format_text_with_direction
- get_cell_color
- load_scoreboard_json
"""

import json
import unicodedata
import pandas as pd


def is_rtl_text(text: str) -> bool:
    for char in text:
        bidi = unicodedata.bidirectional(char)
        if bidi in ("R", "AL"):
            return True
    return False


def format_text_with_direction(text: str) -> str:
    if is_rtl_text(text):
        return text[::-1]
    return text


def get_cell_color(value, col_data, lower_is_better: bool = False) -> str:
    """Get hex color for a cell value (green=best, red=worst)."""
    col_data = col_data.dropna()
    if len(col_data) < 2:
        return "#ffffff"

    if lower_is_better:
        percentile = 1.0 - (col_data <= value).sum() / len(col_data)
    else:
        percentile = (col_data <= value).sum() / len(col_data)

    if percentile < 0.5:
        r = 255
        g = int(255 * (percentile * 2))
        b = 0
    else:
        r = int(255 * (2 * (1 - percentile)))
        g = 255
        b = 0

    return f"#{r:02x}{g:02x}{b:02x}"


def load_scoreboard_json(json_path: str) -> pd.DataFrame:
    """Load parsed scoreboard JSON and convert to DataFrame.

    Expected JSON format: list of {"team_name": str, "stats": {stat: value, ...}}
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    rows = []
    for team_entry in data:
        row = {"Team": team_entry.get("team_name")}
        for stat_name, stat_value in team_entry.get("stats", {}).items():
            try:
                row[stat_name] = float(stat_value)
            except (ValueError, TypeError):
                row[stat_name] = stat_value
        rows.append(row)

    df = pd.DataFrame(rows)
    return df
