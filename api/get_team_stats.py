import sys
from pathlib import Path

try:
    from yahoo_api_handler import YahooAPIHandler
    from config import LEAGUE_KEY
    from parsing_responses.consts import save_response_to_file, MANAGER_NAME_TO_ID_MAP
except ImportError:
    # Add parent directory to path for relative imports
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from yahoo_api_handler import YahooAPIHandler
    from config import LEAGUE_KEY
    from parsing_responses.consts import save_response_to_file, MANAGER_NAME_TO_ID_MAP


def get_team_stats(team_id: str, is_main: bool = False) -> None:
    """Fetch and display team information from Yahoo Fantasy API."""
    try:
        print(f"Fetching team information for team ID {team_id}...")
        response = YahooAPIHandler.make_request(
            f"/team/{LEAGUE_KEY}.t.{team_id}/stats",
            method="GET",
            params={"format": "json"}
        )

        # Check if request was successful
        if response.status_code == 200:
            team_info = response.json()

            if is_main:
                path = f"response/main_team_stats_{team_id}.json"
            else:
                path = f"response/team__stats_{team_id}.json"

            save_response_to_file(team_info, path)
            print(f"✅ JSON response saved successfully to {path}")
        else:
            print(f"Failed to fetch team information. Status code: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Failed to fetch team information: {e}")

if __name__ == "__main__":
    team_id = MANAGER_NAME_TO_ID_MAP['The Perfumer']
    get_team_stats(team_id=team_id, is_main=True)