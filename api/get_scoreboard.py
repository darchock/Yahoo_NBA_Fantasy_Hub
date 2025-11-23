from yahoo_api_handler import YahooAPIHandler
from config import LEAGUE_KEY
from parsing_responses.consts import save_response_to_file
import json

def get_league_weekly_scoreboard(week: str) -> None:
    """Fetch and display league weekly scoreboard from Yahoo Fantasy API."""
    try:
        print(f"Fetching league scoreboard for week {week}...")
        response = YahooAPIHandler.make_request(
            f"/league/{LEAGUE_KEY}/scoreboard;week={week}",
            method="GET",
            params={"format": "json"}
        )
        # Check if request was successful
        if response.status_code == 200:
            scoreboard = response.json()

            # Save to file
            path = f"response/scoreboard_week_{week}.json"
            save_response_to_file(scoreboard, path)

            print(f"✅ JSON response saved successfully to scoreboard_week_{week}.json")
        else:
            print(f"Failed to fetch scoreboard for week {week}. Status code: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Failed to fetch league scoreboard for week {week}: {e}")

def get_league_scoreboard() -> None:
    """Fetch and display league scoreboard from Yahoo Fantasy API."""
    try:
        print("Fetching league scoreboard...")
        response = YahooAPIHandler.make_request(
            f"/league/{LEAGUE_KEY}/scoreboard",
            method="GET", 
            params={"format": "json"}
        )
        # Check if request was successful
        if response.status_code == 200:
            scoreboard = response.json()

            # Save to file
            with open("response/scoreboard.json", "w", encoding="utf-8") as f:
                json.dump(scoreboard, f, indent=2, ensure_ascii=False)

            print("✅ JSON response saved successfully to scoreboard.json")
        else:
            print(f"Failed to fetch scoreboard. Status code: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Failed to fetch league scoreboard: {e}")    