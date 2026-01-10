"""Transaction visualizations.

Visualizations for league transaction data:
- Most added/dropped players
- Team transaction activity
- Transaction timeline
"""

from datetime import datetime
from pathlib import Path
from collections import Counter
from typing import Any, Dict, List
import json
import matplotlib.pyplot as plt
import pandas as pd

try:
    from visualization._helpers import format_text_with_direction
except ImportError:
    from _helpers import format_text_with_direction


def load_parsed_transactions(json_path: str) -> List[Dict[str, Any]]:
    """Load parsed transactions from JSON file."""
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_player_movement_counts(transactions: List[Dict[str, Any]]) -> Dict[str, Counter]:
    """Count adds and drops per player.

    Returns:
        Dict with 'adds' and 'drops' Counters keyed by player name
    """
    adds: Counter = Counter()
    drops: Counter = Counter()

    for txn in transactions:
        for player in txn.get("players", []):
            player_name = player.get("player_name", "Unknown")
            action = player.get("action_type", "")

            if action == "add":
                adds[player_name] += 1
            elif action == "drop":
                drops[player_name] += 1

    return {"adds": adds, "drops": drops}


def create_most_added_dropped_chart(
    transactions: List[Dict[str, Any]],
    output_path: str,
    top_n: int = 12
) -> str:
    """Create side-by-side bar charts for most added and dropped players.

    Args:
        transactions: List of parsed transaction dictionaries
        output_path: Path to save the output image
        top_n: Number of top players to show

    Returns:
        Absolute path to saved image
    """
    counts = get_player_movement_counts(transactions)

    # Get top N for each
    top_adds = counts["adds"].most_common(top_n)
    top_drops = counts["drops"].most_common(top_n)

    # Create figure with two subplots side by side
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 10))
    fig.patch.set_facecolor("white")

    # Color schemes
    add_color = "#2ecc71"  # Green for adds
    drop_color = "#e74c3c"  # Red for drops

    # Most Added Players (left chart)
    if top_adds:
        players_add = [p[0] for p in reversed(top_adds)]
        counts_add = [p[1] for p in reversed(top_adds)]

        y_pos = range(len(players_add))
        bars1 = ax1.barh(y_pos, counts_add, color=add_color, edgecolor="white", height=0.7)
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(players_add, fontsize=10)
        ax1.set_xlabel("Times Added", fontsize=12, fontweight="bold")
        ax1.set_title("Most Added Players", fontsize=14, fontweight="bold", pad=15)
        ax1.set_xlim(0, max(counts_add) * 1.15)

        # Add count labels on bars
        for bar, count in zip(bars1, counts_add):
            ax1.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height()/2,
                    str(count), va="center", fontsize=10, fontweight="bold")

        ax1.spines["top"].set_visible(False)
        ax1.spines["right"].set_visible(False)
        ax1.grid(axis="x", alpha=0.3, linestyle="--")

    # Most Dropped Players (right chart)
    if top_drops:
        players_drop = [p[0] for p in reversed(top_drops)]
        counts_drop = [p[1] for p in reversed(top_drops)]

        y_pos = range(len(players_drop))
        bars2 = ax2.barh(y_pos, counts_drop, color=drop_color, edgecolor="white", height=0.7)
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(players_drop, fontsize=10)
        ax2.set_xlabel("Times Dropped", fontsize=12, fontweight="bold")
        ax2.set_title("Most Dropped Players", fontsize=14, fontweight="bold", pad=15)
        ax2.set_xlim(0, max(counts_drop) * 1.15)

        # Add count labels on bars
        for bar, count in zip(bars2, counts_drop):
            ax2.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height()/2,
                    str(count), va="center", fontsize=10, fontweight="bold")

        ax2.spines["top"].set_visible(False)
        ax2.spines["right"].set_visible(False)
        ax2.grid(axis="x", alpha=0.3, linestyle="--")

    # Overall title
    total_txns = len(transactions)
    fig.suptitle(f"Player Movement Summary ({total_txns} Total Transactions)",
                 fontsize=16, fontweight="bold", y=0.98)

    plt.tight_layout(rect=(0, 0, 1, 0.95))

    # Save
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()

    return str(Path(output_path).absolute())


def create_team_activity_chart(
    transactions: List[Dict[str, Any]],
    output_path: str
) -> str:
    """Create horizontal bar chart showing transaction activity per team.

    Args:
        transactions: List of parsed transaction dictionaries
        output_path: Path to save the output image

    Returns:
        Absolute path to saved image
    """
    team_counts: Counter = Counter()

    for txn in transactions:
        for player in txn.get("players", []):
            dest_team = player.get("destination_team_name", "")
            src_team = player.get("source_team_name", "")
            action = player.get("action_type", "")

            if action == "add" and dest_team:
                team_counts[dest_team] += 1
            elif action == "drop" and src_team:
                team_counts[src_team] += 1
            elif action == "trade":
                if dest_team:
                    team_counts[dest_team] += 1

    if not team_counts:
        print("No team data found")
        return ""

    # Sort by count descending
    sorted_teams = sorted(team_counts.items(), key=lambda x: x[1], reverse=True)

    # Handle RTL text for Hebrew team names
    teams = [format_text_with_direction(t[0]) for t in reversed(sorted_teams)]
    counts = [t[1] for t in reversed(sorted_teams)]

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor("white")

    # Create color gradient based on activity
    colors = plt.cm._colormaps['Blues']([0.3 + 0.6 * (c / max(counts)) for c in counts])

    y_pos = range(len(teams))
    bars = ax.barh(y_pos, counts, color=colors, edgecolor="white", height=0.7)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(teams, fontsize=11)
    ax.set_xlabel("Total Transactions", fontsize=12, fontweight="bold")
    ax.set_title("Team Transaction Activity", fontsize=16, fontweight="bold", pad=15)
    ax.set_xlim(0, max(counts) * 1.12)

    # Add count labels
    for bar, count in zip(bars, counts):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                str(count), va="center", fontsize=11, fontweight="bold")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", alpha=0.3, linestyle="--")

    plt.tight_layout()

    # Save
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()

    return str(Path(output_path).absolute())


def run_most_added_dropped_visualization(folder_name: str) -> None:
    """Run the most added/dropped players visualization."""
    json_file = Path("league_data/transactions/parsed_league_transactions.json")

    if not json_file.exists():
        print(f"File not found: {json_file}")
        print("Please run parsing_transactions.py first to generate parsed data.")
        return

    print(f"Loading {json_file}...")
    transactions = load_parsed_transactions(str(json_file))
    print(f"Loaded {len(transactions)} transactions")

    output_dir = Path(f"visualization/graphs/transactions/{folder_name}")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "most_added_dropped_players.png"

    try:
        result_path = create_most_added_dropped_chart(transactions, str(output_path))
        print(f"Saved to: {result_path}")
    except Exception as e:
        print(f"Error creating visualization: {e}")


def get_waiver_tenure_data(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Calculate tenure for players picked up who are still rostered.

    Finds players where adds > drops per team (net positive = likely still rostered).
    Calculates tenure from first add to current date.

    Returns:
        List of dicts with player_name, team, add_date, tenure_days, still_rostered
    """
    from datetime import datetime
    from collections import defaultdict

    # Track adds and drops per (player, team) combination
    # Structure: {(player_name, team): {"adds": [(timestamp, source_type)], "drops": [timestamp]}}
    player_team_history: Dict[tuple, Dict[str, List]] = defaultdict(lambda: {"adds": [], "drops": []})

    for txn in transactions:
        timestamp = int(txn.get("timestamp", 0))
        for player in txn.get("players", []):
            player_name = player.get("player_name", "")
            action = player.get("action_type", "")
            source_type = player.get("source_type", "")
            dest_team = player.get("destination_team_name", "")
            src_team = player.get("source_team_name", "")

            if action == "add" and dest_team:
                key = (player_name, dest_team)
                player_team_history[key]["adds"].append((timestamp, source_type))

            elif action == "drop" and src_team:
                key = (player_name, src_team)
                player_team_history[key]["drops"].append(timestamp)

            elif action == "trade":
                # Trade out counts as leaving
                if src_team:
                    key = (player_name, src_team)
                    player_team_history[key]["drops"].append(timestamp)
                # Trade in counts as add
                if dest_team:
                    key = (player_name, dest_team)
                    player_team_history[key]["adds"].append((timestamp, "trade"))

    # Find players still rostered (adds > drops)
    tenures: List[Dict[str, Any]] = []
    current_time = max(int(t.get("timestamp", 0)) for t in transactions)

    for (player_name, team), history in player_team_history.items():
        adds = history["adds"]
        drops = history["drops"]

        # Player is still rostered if they have more adds than drops
        if len(adds) > len(drops):
            # Get the most recent add that doesn't have a corresponding drop
            adds_sorted = sorted(adds, key=lambda x: x[0])
            drops_sorted = sorted(drops)

            # Find the add that's still active (last unmatched add)
            # Simple approach: if adds > drops, the last add is active
            last_add_ts, last_add_source = adds_sorted[-1]

            # Skip if this was just a very recent add (less than 1 day)
            tenure_seconds = current_time - last_add_ts
            tenure_days = tenure_seconds / 86400
            if tenure_days < 1:
                continue

            add_date = datetime.fromtimestamp(last_add_ts).strftime("%Y-%m-%d")

            tenures.append({
                "player_name": player_name,
                "team": team,
                "add_date": add_date,
                "source_type": last_add_source,
                "tenure_days": round(tenure_days, 1),
                "still_rostered": True
            })

    return tenures


def create_waiver_tenure_chart(
    transactions: List[Dict[str, Any]],
    output_path: str,
    top_n: int = 15
) -> str:
    """Create bar chart showing longest tenure for players still rostered.

    Shows players who were added and are still on the team (adds > drops).

    Args:
        transactions: List of parsed transaction dictionaries
        output_path: Path to save the output image
        top_n: Number of top players to show

    Returns:
        Absolute path to saved image
    """
    tenures = get_waiver_tenure_data(transactions)

    if not tenures:
        print("No tenure data found")
        return ""

    # Sort by tenure (longest first) and take top N
    sorted_tenures = sorted(tenures, key=lambda x: x["tenure_days"], reverse=True)[:top_n]

    # Prepare data (reverse for horizontal bar chart)
    sorted_tenures = list(reversed(sorted_tenures))

    labels = [f"{t['player_name']} ({format_text_with_direction(t['team'])})" for t in sorted_tenures]
    days = [t["tenure_days"] for t in sorted_tenures]
    sources = [t.get("source_type", "") for t in sorted_tenures]

    # Create figure
    fig, ax = plt.subplots(figsize=(14, 10))
    fig.patch.set_facecolor("white")

    # Color by source type
    color_map = {"waivers": "#e74c3c", "freeagents": "#3498db", "trade": "#9b59b6"}
    colors = [color_map.get(s, "#95a5a6") for s in sources]

    y_pos = range(len(labels))
    bars = ax.barh(y_pos, days, color=colors, edgecolor="white", height=0.7)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlabel("Days on Roster (Still Rostered)", fontsize=12, fontweight="bold")
    ax.set_title("Longest Tenure - Players Still Rostered After Pickup", fontsize=16, fontweight="bold", pad=15)
    ax.set_xlim(0, max(days) * 1.12)

    # Add day count labels
    for bar, d in zip(bars, days):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                f"{d:.0f}", va="center", fontsize=10, fontweight="bold")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", alpha=0.3, linestyle="--")

    # Add legend for source types
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="#e74c3c", label="From Waivers"),
        Patch(facecolor="#3498db", label="From Free Agents"),
        Patch(facecolor="#9b59b6", label="From Trade")
    ]
    ax.legend(handles=legend_elements, loc="lower right", fontsize=10)

    plt.tight_layout()

    # Save
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()

    return str(Path(output_path).absolute())


def run_waiver_tenure_visualization(folder_name: str) -> None:
    """Run the waiver wire tenure visualization."""
    json_file = Path("league_data/transactions/parsed_league_transactions.json")

    if not json_file.exists():
        print(f"File not found: {json_file}")
        print("Please run parsing_transactions.py first to generate parsed data.")
        return

    print(f"Loading {json_file}...")
    transactions = load_parsed_transactions(str(json_file))
    print(f"Loaded {len(transactions)} transactions")

    output_dir = Path(f"visualization/graphs/transactions/{folder_name}")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "waiver_tenure.png"

    try:
        result_path = create_waiver_tenure_chart(transactions, str(output_path))
        print(f"Saved to: {result_path}")
    except Exception as e:
        print(f"Error creating visualization: {e}")


def run_team_activity_visualization(folder_name: str) -> None:
    """Run the team transaction activity visualization."""
    json_file = Path("league_data/transactions/parsed_league_transactions.json")

    if not json_file.exists():
        print(f"File not found: {json_file}")
        print("Please run parsing_transactions.py first to generate parsed data.")
        return

    print(f"Loading {json_file}...")
    transactions = load_parsed_transactions(str(json_file))
    print(f"Loaded {len(transactions)} transactions")

    output_dir = Path(f"visualization/graphs/transactions/{folder_name}")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "team_transaction_activity.png"

    try:
        result_path = create_team_activity_chart(transactions, str(output_path))
        print(f"Saved to: {result_path}")
    except Exception as e:
        print(f"Error creating visualization: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("Transaction Visualizations")
    print("=" * 60)
    print("\nChoose visualization:")
    print("1. Most Added/Dropped Players")
    print("2. Team Transaction Activity")
    print("3. Waiver Wire Tenure (longest keepers)")
    print("4. All")

    choice = input("\nEnter choice (1-4): ").strip()

    folder_name = datetime.now().strftime("%Y-%m-%d")
    if choice == "1":
        run_most_added_dropped_visualization(folder_name)
    elif choice == "2":
        run_team_activity_visualization(folder_name)
    elif choice == "3":
        run_waiver_tenure_visualization(folder_name)
    elif choice == "4":
        run_most_added_dropped_visualization(folder_name)
        print()
        run_team_activity_visualization(folder_name)
        print()
        run_waiver_tenure_visualization(folder_name)
    else:
        print("Invalid choice")
