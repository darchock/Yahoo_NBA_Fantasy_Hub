"""Simple totals table visualization.

Rows: managers
Columns: categories (rank per category)
Extra row: league average for each category ('League Average')

Saves image to `visualization/graphs/week_{week}/Totals_Table_Week_{week}.png`.
"""

from pathlib import Path
import pandas as pd
from typing import Any, Dict
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


def save_table_as_image(df, output_path="totals_table.png", week=None):
    """Convert DataFrame to styled image table and save."""

    sns.set_theme(style="whitegrid")
    sns.set_context("notebook", font_scale=1)
    avg_bg = sns.color_palette("coolwarm")[2]
    
    # Convert RGB tuples to hex strings
    avg_bg = f'#{int(avg_bg[0]*255):02x}{int(avg_bg[1]*255):02x}{int(avg_bg[2]*255):02x}'

    fig, ax = plt.subplots(figsize=(18, 10))
    fig.patch.set_facecolor("white")
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
                row_colors.append(avg_bg)
            else:
                col_vals = df[col].iloc[:-1]
                lower = col in lower_is_better
                color = get_cell_color(value, col_vals, lower_is_better=lower)
                row_colors.append(color)
        
        table_data.append(row_data)
        cell_colors.append(row_colors)
    
    table = ax.table(cellText=table_data, cellLoc="center", loc="center", cellColours=cell_colors)
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.2, 2.5)  # Increase cell width and height to fit text better
    
    # Fit text to cells
    for i in range(len(table_data)):
        for j in range(len(header)):
            cell = table[(i, j)]
            cell.set_text_props(ha="center", va="center")
            # Slightly bolder header/summary row
            if i == 0 or i == len(table_data) - 1:
                cell.set_text_props(weight="bold")
            # Add subtle borders for readability
            cell.set_edgecolor("#dddddd")
            cell.set_linewidth(0.5)
    
    league_avg_idx = len(table_data) - 1
    for i in range(len(header)):
        table[(league_avg_idx, i)].set_text_props(weight="bold")
    
    # Set title with week number if provided
    if week is not None:
        title = f"Totals Table week #{week}"
    else:
        title = "Team Totals Weekly"
    plt.title(title, fontsize=20, pad=20)
    
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


def create_styled_totals_table(df: pd.DataFrame, week: str, output_dir: Path, file_name: str) -> None:
    """Create styled totals table and save as image."""

    regular_stats = ['FGM','FGA', 'FTM','FTA','FG%', 'FT%', '3PTM', 'PTS', 'REB', 'AST', 'STL', 'BLK']
    revert_stats = ['TO']
    float_stats = ['FG%', 'FT%']
    integer_stats = ['FGM','FGA', 'FTM','FTA','3PTM', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TO']

    with_color_indices = [r for r in df.index.tolist() if r != "League Average"]
    subset_regular_cols = df.loc[with_color_indices, regular_stats].columns.tolist()
    subset_revert_cols = df.loc[with_color_indices, revert_stats].columns.tolist()

    def highlight_average(x):
        return ['background-color: #696969; font-weight: bold' if x.name == 'League Average' else '' for _ in x]

    def float_format(x):
        return f'{x:.3f}'

    def integer_format(x):
        return f'{x:.0f}'

    # league_avg_subset = (['League Average'], df.columns.tolist())
    title = f'Totals table - week {week}'
    totals_styled_df = (
        df.style
        .format(float_format, subset=float_stats)
        .format(integer_format,subset=integer_stats)
        .background_gradient(cmap='RdYlGn', subset=subset_regular_cols)
        .background_gradient(cmap='RdYlGn_r', subset=subset_revert_cols)
        .apply(highlight_average, axis=1)
        .set_caption(f"<b>{title}</b>")
        .hide(axis="index")
    )
    
    output_path = str(output_dir / file_name)
    styled: Any = totals_styled_df
    dfi.export(styled, output_path)

def run_totals_table_visualization(week: str) -> None:
    """Run totals table visualization for given week - been called from `main.py`"""
    json_file = Path(f"league_data/weekly_scoreboard/parsed_scoreboard_week_{week}.json")
    
    if json_file.exists():
        print(f"Loading {json_file}...")
        df = load_scoreboard_json(str(json_file))
        print(f"Loaded {len(df)} teams/rows")
        
        output_dir = Path(f"visualization/graphs/week_{week}")
        styled_file_name = f"styled_totals_week_{week}.png"
        
        try:
            df = append_league_average_row(df)
            create_styled_totals_table(df=df, week=week, output_dir=output_dir, file_name=styled_file_name)
            print(f"✅ Saved to: {str(output_dir / styled_file_name)}")
        except Exception as e:
            print(f"Error creating styled totals table: {e}")

        # file_name = f"Totals_Table_Week_{week}.png"
        # output_path = output_dir / file_name
        # output_abs_path = save_table_as_image(df, str(output_path), week=week)
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
        
        try:
            df = append_league_average_row(df)
            create_styled_totals_table(df=df, week=week, output_dir=output_dir, file_name=styled_file_name)
            print(f"✅ Saved to: {str(output_dir / styled_file_name)}")
        except Exception as e:
            print(f"Error creating styled totals table: {e}")

        # file_name = f"Totals_Table_Week_{week}.png"
        # output_path = output_dir / file_name
        # output_abs_path = save_table_as_image(df, str(output_path), week=week)
        # print(f"✓ Saved to: {str(Path(output_dir / file_name).absolute())}")
    else:
        print(f"File not found: {json_file}")
