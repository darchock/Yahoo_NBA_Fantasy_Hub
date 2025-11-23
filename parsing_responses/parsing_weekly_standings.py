from typing import Any, Dict, List
from parsing_responses.consts import *

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

                            # 5️⃣ Append to results
                            team_name = MANAGER_ID_TO_NAME_MAP.get(str(team_id))
                            result.append({
                                "team_name": team_name,
                                "standing": int(standing)+1,
                                "stats": stats_map
                            })
    except Exception as e:
        print(f"Error parsing weekly standings for week {week}: {e}")

    print(f"✅ Successfully completed parsing week {week} standings")
    return result