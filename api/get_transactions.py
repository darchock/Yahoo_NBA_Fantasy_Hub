import sys
from pathlib import Path

try:
    from yahoo_api_handler import YahooAPIHandler
    from config import LEAGUE_KEY
    from parsing_responses.consts import save_response_to_file, MANAGER_ID_TO_NAME_MAP
except ImportError:
    # Add parent directory to path for relative imports
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from yahoo_api_handler import YahooAPIHandler
    from config import LEAGUE_KEY
    from parsing_responses.consts import save_response_to_file, MANAGER_ID_TO_NAME_MAP

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


def get_team_transactions(team_id: str, week: str, is_main: bool = False) -> None:
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
                path = f"response/main_transactions_team_{team_id}_week_{week}.json"
            else:
                path = f"response/_team_{team_id}_week_{week}.json"

            save_response_to_file(transactions, path)
            print(f"✅ JSON response saved successfully to {path}")
        else:
            print(f"Failed to fetch team transactions. Status code: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Failed to fetch team transactions: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("GET transactions")
    print("=" * 60)

    print("\nChoose which transaction type:")
    print("1. League Transactions")
    print("2. Team Transactions")
    choice = input("Enter choice (1 or 2): ").strip()

    if choice not in {"1", "2"}:
        print("Invalid choice. Exiting.")
        exit(1)
    
    week = input("Enter week number (e.g., 1, 2, ...): ").strip()
    if not week.isdigit() or int(week) < 1:
        print("Invalid week number. Exiting.")
        exit(1)

    if choice == "1":

        get_league_transactions(week=week, is_main=True)
    elif choice == "2":
        print("\nParsing Team Transactions...")
        print("\nChoose team to parse:")
        print(f"1. {MANAGER_ID_TO_NAME_MAP.get('1', 'Unknown Team')}")
        print(f"2. {MANAGER_ID_TO_NAME_MAP.get('2', 'Unknown Team')}")
        print(f"3. {MANAGER_ID_TO_NAME_MAP.get('3', 'Unknown Team')}")
        print(f"4. {MANAGER_ID_TO_NAME_MAP.get('4', 'Unknown Team')}")
        print(f"5. {MANAGER_ID_TO_NAME_MAP.get('5', 'Unknown Team')}")
        print(f"6. {MANAGER_ID_TO_NAME_MAP.get('6', 'Unknown Team')}")
        print(f"7. {MANAGER_ID_TO_NAME_MAP.get('7', 'Unknown Team')}")
        print(f"8. {MANAGER_ID_TO_NAME_MAP.get('8', 'Unknown Team')}")
        print(f"9. {MANAGER_ID_TO_NAME_MAP.get('9', 'Unknown Team')}")
        print(f"10. {MANAGER_ID_TO_NAME_MAP.get('10', 'Unknown Team')}")

        team_choice = input("Enter choice (1 ... 10): ").strip()

        if team_choice not in {"1", "2", "3", "4", "5", "6", "7", "8", "9", "10"}:
            print("Invalid choice. Exiting.")
            exit(1)

        team_name = MANAGER_ID_TO_NAME_MAP.get(team_choice, "Unknown Team")
        print(f"\nSelected Team: {team_name} (ID: {team_choice})")

        get_team_transactions(team_id=team_choice, week=week, is_main=True)