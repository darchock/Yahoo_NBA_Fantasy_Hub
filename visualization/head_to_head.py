from pathlib import Path
import dataframe_image as dfi
import pandas as pd
import itertools
from typing import Any, cast

try:
    from _helpers import  load_scoreboard_json
except ImportError:
    # allow running as script from main.py
    from visualization._helpers import load_scoreboard_json


def build_head_to_head_df(df: pd.DataFrame, week: str, output_dir: Path, file_name: str) -> None:
    scoring_cats = ['FG%', 'FT%', '3PTM', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TO']

    teams = df['Team'].tolist()
    h2h_matrix = pd.DataFrame(index=teams, columns=teams)
    totals = {team: {'wins': 0, 'losses': 0, 'ties': 0} for team in teams}

    for team1, team2 in itertools.combinations(teams, 2):
        wins, losses, ties = 0, 0, 0

        for cat in scoring_cats:
            rank1 = df[df['Team'] == team1][cat].values[0]
            rank2 = df[df['Team'] == team2][cat].values[0]

            if cat == 'TO':
                if rank1 < rank2:
                    wins += 1
                elif rank1 > rank2:
                    losses += 1
                else:
                    ties += 1
            elif cat in ['FG%', 'FT%'] and (rank1 == rank2):
                if cat == 'FG%':
                    team1_attempts = df[df['Team'] == team1]['FGA'].values[0]
                    team2_attempts = df[df['Team'] == team2]['FGA'].values[0]
                else:
                    team1_attempts = df[df['Team'] == team1]['FTA'].values[0]
                    team2_attempts = df[df['Team'] == team2]['FTA'].values[0]

                if team1_attempts > team2_attempts:
                    wins += 1
                elif team1_attempts < team2_attempts:
                    losses += 1
                else:
                    ties += 1
            else:
                if rank1 > rank2:
                    wins += 1
                elif rank1 < rank2:
                    losses += 1
                else:
                    ties += 1

        h2h_matrix.loc[team1, team2] = f"{wins}-{losses}-{ties}"
        h2h_matrix.loc[team2, team1] = f"{losses}-{wins}-{ties}"

        totals[team1]['wins'] += wins
        totals[team1]['losses'] += losses
        totals[team1]['ties'] += ties
        totals[team2]['wins'] += losses
        totals[team2]['losses'] += wins
        totals[team2]['ties'] += ties

    # Fill diagonal with "-"
    for team in teams:
        h2h_matrix.loc[team, team] = "-"

    h2h_matrix['W-L-T'] = [f"{totals[team]['wins']}-{totals[team]['losses']}-{totals[team]['ties']}" 
                          for team in teams]
    
    h2h_matrix['Win%'] = [
        (totals[team]['wins'] + 0.5 * totals[team]['ties']) / 
        (totals[team]['wins'] + totals[team]['losses'] + totals[team]['ties']) * 100
        for team in teams
    ]

    title = f"Head-to-Head Matchups - Week {week}"
    styled_df = h2h_matrix.style.set_properties(subset=None, **{
        'text-align': 'center',
        'white-space': 'nowrap',
        'padding': '5px',
        'font-family': 'Segoe UI, Arial, sans-serif'
    }).set_table_styles([
        {'selector': 'caption', 'props': [
            ('caption-side', 'top'),
            ('text-align', 'center'),
            ('font-size', '20px'),
            ('font-weight', '700'),
            ('font-family', '"Segoe UI", Arial, sans-serif'),
            ('padding', '8px')
        ]},
        {'selector': 'th', 'props': [('text-align', 'center')]},
        {'selector': 'td', 'props': [('text-align', 'center')]}
    ]).background_gradient(
        cmap='RdYlGn', 
        subset=['Win%']
    ).format({'Win%': '{:.1f}%'}
    ).set_caption(title)
    

    output_path = str(output_dir / file_name)
    dfi.export(cast(Any, styled_df), output_path)


def run_head_to_head_visualization(week: str) -> None:
    json_file = Path(f"league_data/weekly_scoreboard/parsed_scoreboard_week_{week}.json")

    if json_file.exists():
        print(f"Loading {json_file}...")
        df = load_scoreboard_json(str(json_file))
        print(f"Loaded {len(df)} teams/rows")
        
        output_dir = Path(f"visualization/graphs/week_{week}")
        h2h_file_name = f"H2H_week_{week}.png"

        try:
            build_head_to_head_df(df=df, week=week, output_dir=output_dir, file_name=h2h_file_name)
            print(f"✓ Saved to: {str(output_dir / h2h_file_name)}")
        except Exception as e:
            print(f"Error creating head to head table: {e}")
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
        h2h_file_name = f"H2H_week_{week}.png"

        try:
            build_head_to_head_df(df=df, week=week, output_dir=output_dir, file_name=h2h_file_name)
            print(f"✓ Saved to: {str(output_dir / h2h_file_name)}")
        except Exception as e:
            print(f"Error creating head to head table: {e}")
    else:
        print(f"File not found: {json_file}")
