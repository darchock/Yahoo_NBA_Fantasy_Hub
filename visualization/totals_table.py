"""Simple totals table visualization.

Rows: managers
Columns: categories (rank per category)
Extra row: league average for each category ('League Average')

Saves image to `visualization/graphs/week_{week}/Totals_Table_Week_{week}.png`.
"""

from pathlib import Path
import pandas as pd
from typing import Any, Dict
from matplotlib import pyplot as plt
try:
    from visualization._helpers import (
        format_text_with_direction,
        load_scoreboard_json,
        get_cell_color,
    )
except ImportError:
    from _helpers import (
        format_text_with_direction,
        load_scoreboard_json,
        get_cell_color,
    )


def save_table_as_image(df, output_path="totals_table.png", week=None):
    """Convert DataFrame to styled image table and save."""
    
    fig, ax = plt.subplots(figsize=(18, 10))
    ax.axis("tight")
    ax.axis("off")
    
    header = ["Team/Category"] + [c for c in df.columns if c != "Team"]
    table_data = [header]
    cell_colors = [["#f0f0f0"] * len(header)]
    
    lower_is_better = {"TO"}
    for idx, row in df.iterrows():
        row_data = [format_text_with_direction(str(row["Team"]))]
        row_colors = ["#f0f0f0"]
        
        for col in header[1:]:
            value = row[col]
            # Format with 3 decimals for percentages, 1 decimal for others
            if isinstance(value, float):
                if col in ("FG%", "FT%"):
                    row_data.append(f"{value:.3f}")
                else:
                    row_data.append(f"{value:.1f}")
            else:
                row_data.append(str(value))
            
            if idx == len(df) - 1:
                row_colors.append("#e8e8e8")
            else:
                col_vals = df[col].iloc[:-1]
                lower = col in lower_is_better
                color = get_cell_color(value, col_vals, lower_is_better=lower)
                row_colors.append(color)
        
        table_data.append(row_data)
        cell_colors.append(row_colors)
    
    table = ax.table(cellText=table_data, cellLoc="center", loc="center", cellColours=cell_colors)
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1.2, 2.5)  # Increase cell width and height to fit text better
    
    # Fit text to cells
    for i in range(len(table_data)):
        for j in range(len(header)):
            cell = table[(i, j)]
            cell.set_text_props(ha="center", va="center")
            if i == 0 or i == len(table_data) - 1:
                cell.set_text_props(weight="bold")
    
    league_avg_idx = len(table_data) - 1
    for i in range(len(header)):
        table[(league_avg_idx, i)].set_text_props(weight="bold")
    
    # Set title with week number if provided
    if week is not None:
        title = f"Totals Table week #{week}"
    else:
        title = "Team Totals - Color Coded (Green = Best, Red = Worst)"
    plt.title(title, fontsize=14, pad=20)
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    
    return str(Path(output_path).absolute())


def append_league_average_row(df) -> pd.DataFrame:
    """Append a 'League Average' row to the DataFrame."""
    avg_row: Dict[str, Any] = {"Team": "League Average"}
    for col in df.columns:
        if col != "Team":
            try:
                avg_value = df[col].mean()
                avg_row[col] = avg_value
            except Exception:
                avg_row[col] = None
    df.loc[len(df)] = avg_row

    return df


def run_totals_table_visualization(week: str) -> None:
    """Run totals table visualization for given week."""
    json_file = Path(f"league_data/weekly_scoreboard/parsed_scoreboard_week_{week}.json")
    
    if json_file.exists():
        print(f"Loading {json_file}...")
        df = load_scoreboard_json(str(json_file))
        print(f"Loaded {len(df)} teams/rows")
        
        output_dir = Path(f"visualization/graphs/week_{week}")
        output_path = output_dir / f"Totals_Table_Week_{week}.png"
        
        output_abs_path = save_table_as_image(df, str(output_path), week=week)
        print(f"✓ Saved to: {output_abs_path}")
    else:
        print(f"File not found: {json_file}")


if __name__ == "__main__":
    json_file = Path("league_data/weekly_scoreboard/parsed_scoreboard_week_4.json")
    
    if json_file.exists():
        print(f"Loading {json_file}...")
        df = load_scoreboard_json(str(json_file))
        print(f"Loaded {len(df)} teams/rows")
        
        # Extract week number from filename
        week = json_file.stem.split("_")[-1]  # e.g., "parsed_scoreboard_week_4" -> "4"
        output_dir = Path(f"visualization/graphs/week_{week}")
        output_path = output_dir / f"Totals_Table_Week_{week}.png"
        
        df = append_league_average_row(df)
        output_abs_path = save_table_as_image(df, str(output_path), week=week)
        print(f"✓ Saved to: {output_abs_path}")
    else:
        print(f"File not found: {json_file}")
