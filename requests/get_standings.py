from yahoo_api_handler import YahooAPIHandler
from config import LEAGUE_KEY
from parsing_responses.consts import save_response_to_file

def get_league_standings(week: str) -> None:
    """Fetch and display league standings from Yahoo Fantasy API."""
    try:
        print(f"Fetching league standings for week #{week}...")
        response = YahooAPIHandler.make_request(
            f"/league/{LEAGUE_KEY}/standings",
            method="GET",
            params={"format": "json"}
        )

        # Check if request was successful
        if response.status_code == 200:
            standings = response.json()

            path = f"response/standings_{week}.json"
            save_response_to_file(standings, path)

            print(f"✅ JSON response saved successfully to response/standings_{week}.json")
        else:
            print(f"Failed to fetch standings. Status code: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Failed to fetch league standings: {e}")