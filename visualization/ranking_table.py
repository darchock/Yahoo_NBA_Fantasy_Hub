"""Simple ranking table visualization.

Rows: managers
Columns: categories (rank per category)
Extra column: manager average ranking ('Avg Rank')

Saves image to `visualization/graphs/week_{week}/Ranking_Table_Week_{week}.png`.
"""

from pathlib import Path
import pandas as pd
from typing import Any
import numpy as np
import dataframe_image as dfi
import seaborn as sns
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
    """Convert ranking DataFrame to styled image table and save."""

    sns.set_theme(style="whitegrid")
    sns.set_context("notebook", font_scale=1)

    fig, ax = plt.subplots(figsize=(18, 10))
    fig.patch.set_facecolor("white")
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
    table.set_fontsize(9)
    table.scale(1.2, 2.5)

    # Fit text to cells
    for i in range(len(table_data)):
        for j in range(len(header)):
            cell = table[(i, j)]
            cell.set_text_props(ha="center", va="center")
            if i == 0:
                cell.set_text_props(weight="bold")
            cell.set_edgecolor("#dddddd")
            cell.set_linewidth(0.5)

    # Title
    if week is not None:
        title = f"Ranking Table week #{week}"
    else:
        title = "Ranking Table Weekly"
    plt.title(title, fontsize=20, pad=20)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()

    return str(Path(output_path).absolute())


def create_styled_rankings_table(df: pd.DataFrame, week: str, output_dir: Path, file_name: str):
    """Convert ranking DataFrame to styled image table and save."""
    ranked_df = df.rank(ascending=False)
    ranked_df['TO'] = df['TO'].rank(ascending=True)

    exclude_cols = ['FGM', 'FGA', 'FTM', 'FTA']
    ranked_df['Avg_Rank'] = (
        ranked_df.drop(columns=exclude_cols)
        .mean(axis=1)
    )
    # ranked_df.drop(columns=['FGM', 'FGA', 'FTM', 'FTA']).sum(axis=1).divide(len(df.index))
    ranked_df['Manager'] = df['Team']
    ranked_df = ranked_df.drop(columns=['Team'])
    cols = ['Manager'] + [c for c in ranked_df.columns if c != 'Manager']
    ranked_df = ranked_df[cols]

    stats = ['FGM', 'FGA', 'FTM', 'FTA', 'FG%', 'FT%', '3PTM', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TO', 'Avg_Rank']
    float_stats = ['Avg_Rank']
    integer_stats = ['FGM', 'FGA', 'FTM', 'FTA', 'FG%', 'FT%', '3PTM', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TO']

    title = f'Ranking table - week {week}'
    # Style with rankings and color gradient
    df_ranked_and_sorted_by_avg = ranked_df.sort_values(by='Avg_Rank')
    ranked_styled_df = (
        df_ranked_and_sorted_by_avg.style
        .format('{:.0f}', subset=integer_stats)
        .format('{:.2f}', subset=float_stats)
        .background_gradient(
            cmap='RdYlGn_r', 
            subset=stats
        )
        .set_caption(f"<b>{title}</b>")
        .hide(axis="index")
    )

    output_path = str(output_dir / file_name)
    styled: Any = ranked_styled_df
    dfi.export(styled, output_path)


def run_ranking_table_visualization(week: str) -> None:
    """Run ranking table visualization for given week - been called from `main.py`"""
    json_file = Path(f"league_data/weekly_scoreboard/parsed_scoreboard_week_{week}.json")

    if json_file.exists():
        print(f"Loading {json_file}...")
        df = load_scoreboard_json(str(json_file))
        print(f"Loaded {len(df)} teams/rows")

        output_dir = Path(f"visualization/graphs/week_{week}")
        styled_file_name = f"styled_ranking_week_{week}.png"

        try:
            create_styled_rankings_table(df, week=week, output_dir=output_dir, file_name=styled_file_name)
            print(f"✓ Saved to: {str(output_dir / styled_file_name)}")
        except Exception as e:
            print(f"Error creating styled rankings table: {e}")

        # file_name = f"Ranking_Table_Week_{week}.png"
        # output_path = output_dir / file_name
        # ranks_df, numeric_cols = build_ranking_df(df)
        # output_abs = save_ranking_table_image(ranks_df, numeric_cols, str(output_path), week=week)
        # print(f"✓ Saved to: {str(Path(output_dir / file_name).absolute())}")
    else:
        print(f"File not found: {json_file}")


if __name__ == "__main__":
    week = "5"
    json_file = Path(f"league_data/weekly_scoreboard/parsed_scoreboard_week_{week}.json")

    if json_file.exists():
        print(f"Loading {json_file}...")
        df = load_scoreboard_json(str(json_file))
        print(f"Loaded {len(df)} teams/rows")

        output_dir = Path(f"visualization/graphs/week_{week}")
        styled_file_name = f"styled_ranking_week_{week}.png"

        create_styled_rankings_table(df, week=week, output_dir=output_dir, file_name=styled_file_name)
        print(f"✓ Saved to: {str(output_dir / styled_file_name)}")

        # file_name = f"Ranking_Table_Week_{week}.png"
        # output_path = output_dir / file_name
        # ranks_df, numeric_cols = build_ranking_df(df)
        # output_abs = save_ranking_table_image(ranks_df, numeric_cols, str(output_path), week=week)
        # print(f"✓ Saved to: {str(Path(output_dir / file_name).absolute())}")
    else:
        print(f"File not found: {json_file}")