"""Simple ranking table visualization.

Rows: managers
Columns: categories (rank per category)
Extra column: manager average ranking ('Avg Rank')

Saves image to `visualization/graphs/week_{week}/Ranking_Table_Week_{week}.png`.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from matplotlib import pyplot as plt
from visualization._helpers import (
    format_text_with_direction,
    get_cell_color,
    load_scoreboard_json,
)



def build_ranking_df(df):
    """Return DataFrame of ranks per numeric category and an Avg Rank column."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    lower_is_better = {"TO"}

    # These columns are informative (counts), exclude them from Avg Rank
    exclude_from_avg = {"FGM", "FGA", "FTM", "FTA"}

    ranks = pd.DataFrame({"Team": df["Team"]})
    for col in numeric_cols:
        asc = col in lower_is_better
        # method='min' gives the best (1) to the top in our ordering
        ranks[col] = df[col].rank(ascending=asc, method="min")

    # Avg rank across selected numeric cols (omit informative count columns)
    avg_cols = [c for c in numeric_cols if c not in exclude_from_avg]
    ranks["Avg Rank"] = ranks[avg_cols].mean(axis=1)
    return ranks, numeric_cols


def save_ranking_table_image(ranks_df, numeric_cols, output_path="Ranking_Table.png", week=None):

    fig, ax = plt.subplots(figsize=(18, 10))
    ax.axis("tight")
    ax.axis("off")

    header = ["Team"] + numeric_cols + ["Avg Rank"]
    table_data = [header]
    cell_colors = [["#f0f0f0"] * len(header)]

    # For ranking tables: lower rank (1) is better for all columns
    for idx, row in ranks_df.iterrows():
        row_data = [format_text_with_direction(str(row["Team"]))]
        row_colors = ["#f0f0f0"]

        for col in header[1:]:
            value = row[col]
            if col == "Avg Rank":
                # Show average with two decimals
                row_data.append(f"{value:.2f}")
            else:
                # rank values are integers (or floats representing integers)
                # display as int
                try:
                    row_data.append(str(int(value)))
                except Exception:
                    row_data.append(str(value))

            # color: in ranking tables lower is always better (rank 1 is best)
            if col == "Avg Rank":
                col_vals = ranks_df["Avg Rank"]
            else:
                col_vals = ranks_df[col]

            color = get_cell_color(value, col_vals, lower_is_better=True)
            row_colors.append(color)

        table_data.append(row_data)
        cell_colors.append(row_colors)

    table = ax.table(cellText=table_data, cellLoc="center", loc="center", cellColours=cell_colors)
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1.2, 2.5)

    # Fit text to cells
    for i in range(len(table_data)):
        for j in range(len(header)):
            cell = table[(i, j)]
            cell.set_text_props(ha="center", va="center")
            if i == 0:
                cell.set_text_props(weight="bold")

    # Title
    if week is not None:
        title = f"Ranking Table week #{week}"
    else:
        title = "Ranking Table"
    plt.title(title, fontsize=14, pad=20)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()

    return str(Path(output_path).absolute())

def run_ranking_table_visualization(week: str) -> None:
    """Run ranking table visualization for given week number."""
    json_file = Path(f"league_data/weekly_scoreboard/parsed_scoreboard_week_{week}.json")

    if json_file.exists():
        print(f"Loading {json_file}...")
        df = load_scoreboard_json(str(json_file))
        print(f"Loaded {len(df)} teams/rows")

        ranks_df, numeric_cols = build_ranking_df(df)

        output_dir = Path(f"visualization/graphs/week_{week}")
        output_path = output_dir / f"Ranking_Table_Week_{week}.png"

        output_abs = save_ranking_table_image(ranks_df, numeric_cols, str(output_path), week=week)
        print(f"✓ Saved to: {output_abs}")
    else:
        print(f"File not found: {json_file}")


if __name__ == "__main__":
    json_file = Path("league_data/weekly_scoreboard/parsed_scoreboard_week_4.json")

    if json_file.exists():
        print(f"Loading {json_file}...")
        df = load_scoreboard_json(str(json_file))
        print(f"Loaded {len(df)} teams/rows")

        ranks_df, numeric_cols = build_ranking_df(df)

        # Extract week number from filename
        week = json_file.stem.split("_")[-1]
        output_dir = Path(f"visualization/graphs/week_{week}")
        output_path = output_dir / f"Ranking_Table_Week_{week}.png"

        output_abs = save_ranking_table_image(ranks_df, numeric_cols, str(output_path), week=week)
        print(f"✓ Saved to: {output_abs}")
    else:
        print(f"File not found: {json_file}")