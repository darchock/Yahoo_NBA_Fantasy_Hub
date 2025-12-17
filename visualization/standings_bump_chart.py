from pathlib import Path
import pandas as pd
import json
import matplotlib.pyplot as plt

try:
    from visualization._helpers import (
        format_text_with_direction
    )
except ImportError:
    from _helpers import (
        format_text_with_direction
    )


def get_league_standings(week_start: str, week_end: str) -> pd.DataFrame:
    """
    Fetch league standings for a given week.

    Args:
        week_start: The first week number as a string.
        week_end: The last week number as a string.
    Returns:
        DataFrame containing team standings.
    """

    weeks = list(range(int(week_start), int(week_end) + 1))
    weekly_dataframes = []
    combined_df = pd.DataFrame()
    json_path = Path("league_data") / "weekly_standings_and_totals"
    for week in weeks:
        file_name = f"parsed_standings_week_{week}.json"
        try:
            print(f"Loading data for week {week} from {file_name}")
            with open(json_path / file_name, "r", encoding="utf-8") as f:
                weekly_data = json.load(f)
        except FileNotFoundError:
            print(f"File for week {week} not found. Aborting.")
            return pd.DataFrame()  # Return empty DataFrame if any week file is missing

        week_df = pd.DataFrame([
            {
                "team_name": team["team_name"],
                "standing": team["standing"],
                "week": week
            }
            for team in weekly_data
        ])

        weekly_dataframes.append(week_df)
        print(f"Loaded Week {week}: {len(week_df)} teams")

        combined_df = pd.concat(weekly_dataframes, ignore_index=True)

        combined_df.sort_values(['week', 'standing'], inplace=True)

    return combined_df


def plot_standings_bump_chart(week_end: str, week_start: str = "1") -> None:
    """
    Plot a bump chart showing team rankings over the weeks.

    Args:
        week_end: The last week to include in the chart.
        week_start: The first week to include in the chart.
    """

    print(f"Generating standings bump chart from week {week_start} to week {week_end}...")
    combined_df = get_league_standings(week_start=week_start, week_end=week_end)
    if combined_df.empty:
        print("No data available to plot.")
        return
    
    fig, ax = plt.subplots(figsize=(14, 8), dpi=150)

    # Get unique teams and sort by their final week standing
    final_week = combined_df['week'].max()
    final_standings = combined_df[
        combined_df['week'] == final_week
    ].sort_values('standing')

    # Generate distinct colors for each team
    cmap = plt.get_cmap('tab10')
    colors = [cmap(i) for i in range(len(final_standings))]

    # Plot each team's journey
    for idx, team_name in enumerate(final_standings['team_name']):
        team_data = combined_df[
            combined_df['team_name'] == team_name
        ].sort_values('week')

        team_name = format_text_with_direction(team_name)
        
        ax.plot(team_data['week'], team_data['standing'], 
                marker='o', linewidth=3, markersize=8,
                label=team_name, color=colors[idx], alpha=0.8)

    title = f"Fantasy League Standings Over Time (Weeks {week_start} to {week_end})"
    # Customize the chart
    ax.set_xlabel('Week', fontsize=14, fontweight='bold')
    ax.set_ylabel('Rank', fontsize=14, fontweight='bold')
    ax.set_title(title, fontsize=18, fontweight='bold', pad=20)

    # Invert y-axis so rank 1 is at top
    ax.invert_yaxis()

    # Set integer ticks for both axes
    weeks = sorted(combined_df['week'].unique())
    ax.set_xticks(weeks)
    ax.set_yticks(range(1, len(final_standings) + 1))

    # Add grid for readability
    ax.grid(True, alpha=0.3, linestyle='--')

    # Position legend outside plot area
    ax.legend(bbox_to_anchor=(1.05, 0.5), loc='center left',
                fontsize=10, frameon=True, fancybox=True, shadow=True)

    # Tight layout to prevent label cutoff
    plt.tight_layout()

    output_path = Path(f"visualization/graphs/week_{week_end}") / f"Standings_Bump_Chart_Until_Week_{week_end}.png"
    # Save with high quality
    plt.savefig(output_path, dpi=150, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    print(f"✅ Standings Bump chart saved to {output_path}")


def run_standings_bump_chart(week_end: str, week_start: str = "1") -> None:
    """
    Wrapper function to run the standings bump chart generation.
    To be called from main.py

    Args:
        week_end: The last week to include in the chart.
        week_start: The first week to include in the chart.
    """

    try:
        plot_standings_bump_chart(week_end=week_end, week_start=week_start)
    except Exception as e:
        print(f"Error generating bump chart from week {week_start} to {week_end}: {e}")


if __name__ == "__main__":
    print("Generate Standings Bump Chart")
    week_start = input("Enter the week number that you'd like to start from (e.g., 1, 2, ...): ").strip()
    if not week_start.isdigit() or int(week_start) < 1:
        print("Invalid week number. Please enter a positive integer.")
        exit(1)

    week_end = input("Enter the week number that you'd like to end at (e.g., 1, 2, ...): ").strip()
    if not week_end.isdigit() or int(week_end) < 1:
        print("Invalid week number. Please enter a positive integer.")
        exit(1)

    print(f"Generating bump chart from week {week_start} to week {week_end}...")
    try:
        plot_standings_bump_chart(week_end=week_end, week_start=week_start)
    except Exception as e:
        print(f"Error generating bump chart from week {week_start} to {week_end}: {e}")