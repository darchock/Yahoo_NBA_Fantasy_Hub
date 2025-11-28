from pathlib import Path
import json
from typing import Any, Dict, List

try:
    from consts import MANAGER_ID_TO_NAME_MAP, STAT_ID_TO_NAME_MAP, safe_get, extract_from_list_of_dicts
except ImportError:
    # allow running as script from main.py
    from parsing_responses.consts import MANAGER_ID_TO_NAME_MAP, STAT_ID_TO_NAME_MAP, safe_get, extract_from_list_of_dicts

def parse_weekly_standings(data: Dict[str, Any], week: str) -> List[Dict[str, Any]]:
    print(f"Parsing week {week} standings")
    result = []
    try:
        # 1️⃣ Extract matchups safely
        standings_structure = safe_get(
            data,
            "fantasy_content", "league", "standings"
        )

        if not standings_structure is None:
            standings = safe_get(
                standings_structure[0],
                "teams"
            )

            if isinstance(standings, dict):

                # 2️⃣ Iterate through all teams standings dict structure
                for standing, team in standings.items():
                    if not isinstance(team, dict):
                        continue

                    team_lst = team["team"]
                    team_info = team_lst[0]

                    team_id = extract_from_list_of_dicts(
                        team_info,
                        "team_id"
                    )

                    team_stats_dict = team_lst[1]

                    if isinstance(team_stats_dict, dict):

                        stats_map = {}
                        stats_lst = team_stats_dict["team_stats"]["stats"]

                        # 4️⃣ Iterate through the list of the extracted stats
                        for stat in stats_lst:
                            stat_dict = stat["stat"]
                            stat_id = stat_dict["stat_id"]
                            stat_value = stat_dict["value"]
                            if stat_id == "9004003" or stat_id == "9007006":
                                made, attempts = str(stat_value).split("/")
                                throw_type = "FG" if stat_id == "9004003" else "FT"
                                stats_map[f"{throw_type}M"] = int(made)
                                stats_map[f"{throw_type}A"] = int(attempts)
                                continue
                                
                            stat_name = STAT_ID_TO_NAME_MAP.get(str(stat_id))
                            stats_map[stat_name] = stat_value

                        # Extract win rate
                        team_standings_dict = team_lst[2]
                        team_standings = team_standings_dict["team_standings"]
                        win_rate_raw = team_standings["outcome_totals"]["percentage"]
                        win_rate = float(win_rate_raw) * 100 if win_rate_raw else 0.0
                        
                        # 5️⃣ Append to results
                        team_name = MANAGER_ID_TO_NAME_MAP.get(str(team_id))
                        result.append({
                            "team_name": team_name,
                            "standing": int(standing)+1,
                            "win_rate": win_rate,
                            "stats": stats_map
                        })
    except Exception as e:
        print(f"Error parsing weekly standings for week {week}: {e}")

    print(f"✅ Successfully completed parsing week {week} standings")
    return result


if __name__ == "__main__":
    week = "4"
    json_file = Path(f"response/standings_{week}.json")

    if json_file.exists():
        print(f"Loading {json_file}...")
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            standings = parse_weekly_standings(data, week=week)
            print(f"Parsed {len(standings)} teams' standings for week {week}")
            
            output_file = Path(f"league_data/weekly_standings_and_totals/parsed_standings_week_{week}.json")
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(standings, f, indent=4)
            
            print(f"✓ Saved parsed standings to: {output_file}")
        except Exception as e:
            print(f"Error loading or parsing JSON file: {e}")
    else:
        print(f"File not found: {json_file}")
