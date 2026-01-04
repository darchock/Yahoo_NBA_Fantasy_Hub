import sys
from pathlib import Path

try:
    from yahoo_api_handler import YahooAPIHandler
    from config import LEAGUE_KEY
    from parsing_responses.consts import save_response_to_file
except ImportError:
    # Add parent directory to path for relative imports
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from yahoo_api_handler import YahooAPIHandler
    from config import LEAGUE_KEY
    from parsing_responses.consts import save_response_to_file

def get_league_transactions(week: str, is_main: bool = False) -> None:
    """Fetch and display league transactions from Yahoo Fantasy API."""
    try:
        print("Fetching league transactions...")
        response = YahooAPIHandler.make_request(
            f"/league/{LEAGUE_KEY}/transactions",
            method="GET",
            params={"format": "json"}
        )

        # Check if request was successful
        if response.status_code == 200:
            transactions = response.json()

            if is_main:
                path = f"response/main_transactions_week_{week}.json"
            else:
                path = f"response/transactions_week_{week}.json"

            save_response_to_file(transactions, path)
            print(f"✅ JSON response saved successfully to {path}")
        else:
            print(f"Failed to fetch league transactions. Status code: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Failed to fetch league transactions: {e}")


def get_team_transactions(team_id: str, is_main: bool = False) -> None:
    """Fetch and display team transactions from Yahoo Fantasy API."""
    try:
        print(f"Fetching transactions for team ID {team_id}...")
        response = YahooAPIHandler.make_request(
            f"/team/{LEAGUE_KEY}.t.{team_id}/transactions",
            method="GET",
            params={"format": "json"}
        )

        # Check if request was successful
        if response.status_code == 200:
            transactions = response.json()

            if is_main:
                path = f"response/main_team_transactions_{team_id}.json"
            else:
                path = f"response/team_transactions_{team_id}.json"

            save_response_to_file(transactions, path)
            print(f"✅ JSON response saved successfully to {path}")
        else:
            print(f"Failed to fetch team transactions. Status code: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Failed to fetch team transactions: {e}")


if __name__ == "__main__":
    week = "10"
    get_league_transactions(week=week, is_main=True)