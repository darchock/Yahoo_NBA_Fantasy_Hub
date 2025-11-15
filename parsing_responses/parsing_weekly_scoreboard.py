from typing import Any, Dict, List
from consts import *

def parse_weekly_scoreboard(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    # 1️⃣ Extract matchups safely
    matchups = safe_get(
        data,
        "fantasy_content", "league", "scoreboard", "matchups"
    )

    result = []

    if isinstance(matchups, dict):
        
        # 2️⃣ Iterate through all matchups → teams
        for matchup in matchups.values():
            teams = safe_get(matchup, "teams", default={})

            if isinstance(teams, dict):
                
                # 3️⃣ Iterate through the two teams competing in the matchup
                for team in teams.values():
                    if not isinstance(team, dict):
                        continue

                    team_lst = team["team"]
                    team_info = team_lst[0]

                    team_id = extract_from_list_of_dicts(team_info, "team_id")
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
                            "stats": stats_map
                        })
                    
    return result