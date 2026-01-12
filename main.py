"""
Main entry point for Yahoo NBA Fantasy Hub application.
Handles OAuth authentication and token management.

Weekly workflow (run on Monday - first day of matchup):
1. Fetch standings, scoreboard, and transactions from Yahoo API
2. Parse all response data
3. Generate visualizations for WhatsApp group sharing
"""

from pathlib import Path
import sys
import json
from yahoo_api_handler import YahooAPIHandler
from config import LEAGUE_KEY
from parsing_responses.parsing_weekly_scoreboard import parse_weekly_scoreboard
from parsing_responses.parsing_weekly_standings import parse_weekly_standings
from parsing_responses.parsing_transactions import parse_league_transactions, save_league_transactions
from parsing_responses.consts import *
from api.get_standings import get_league_standings
from api.get_scoreboard import get_league_weekly_scoreboard
from api.get_transactions import get_league_transactions
from visualization.totals_table import run_totals_table_visualization, run_periodical_totals_table_visualization
from visualization.ranking_table import run_ranking_table_visualization, run_periodical_ranking_table_visualization
from visualization.head_to_head import run_head_to_head_visualization
from visualization.standings_bump_chart import run_standings_bump_chart
from visualization.transactions import (
    run_most_added_dropped_visualization,
    run_team_activity_visualization,
    run_pickup_tenure_visualization
)


def authenticate_if_needed() -> bool:
    """
    Check if valid token exists, authenticate if needed.

    Returns:
        True if valid token is available, False otherwise.
    """
    access_token = YahooAPIHandler.get_valid_access_token()

    if access_token:
        print("✓ Valid OAuth token found in cache")
        return True

    print("✗ No valid OAuth token found")
    print("\nTo authenticate, follow these steps:")
    print("1. Visit the authorization URL below:")
    print(f"   {YahooAPIHandler.get_authorization_url()}")
    print("\n2. Log in with your Yahoo account and authorize the application")
    print("3. You will be redirected to a URL with an authorization code")
    print("4. Run the following command with the code:")
    print("   python main.py --auth <authorization_code>")
    return False


def handle_auth(auth_code: str) -> None:
    """
    Exchange authorization code for access token.

    Args:
        auth_code: The authorization code from OAuth callback.
    """
    try:
        print("Exchanging authorization code for token...")
        token_data = YahooAPIHandler.fetch_token(auth_code)
        print("✓ Successfully authenticated and saved token")
        print(f"  Token expires in {token_data.get('expires_in', 'unknown')} seconds")
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        sys.exit(1)


def main() -> None:
    """Main application entry point."""
    print("=" * 50)
    print("Yahoo NBA Fantasy Hub")
    print("=" * 50)

    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--auth" and len(sys.argv) > 2:
            handle_auth(sys.argv[2])
            return
        elif sys.argv[1] == "--reset":
            YahooAPIHandler.reset_token()
            print("Token cache cleared. Please authenticate again.")
            return
        elif sys.argv[1] == "--test":
            # Run a simple authenticated request to validate the token
            try:
                print("Running token validity test request...")
                # Request the current user; use format=json to get JSON output
                resp = YahooAPIHandler.make_request(
                    "/users;use_login=1", method="GET", params={"format": "json"}
                )
                print(f"Response status: {resp.status_code}")
                # Try to print JSON body if possible, else raw text
                try:
                    print(resp.json())
                except Exception:
                    print(resp.text)
                return
            except Exception as e:
                print(f"Token test request failed: {e}")
                sys.exit(1)
        else:
            print("Usage:")
            print("  python main.py              - Run application (requires valid token)")
            print("  python main.py --auth CODE  - Authenticate with authorization code")
            print("  python main.py --reset      - Clear cached token")
            print("  python main.py --test      - Run a test authenticated API request")
            sys.exit(1)

    # Main application flow
    if not authenticate_if_needed():
        print("\nPlease authenticate first before running the application.")
        sys.exit(1)

    # Application logic goes here
    print("\n" + "=" * 50)
    print("Application running...")
    print("=" * 50)

    print("Ready to make API requests to Yahoo Fantasy API")
    week_num = input("Enter the week number to process (e.g., 1, 2, ...): ").strip()
    if not week_num.isdigit() or int(week_num) < 1:
        print("Invalid week number. Please enter a positive integer.")
        sys.exit(1)

    print(f"\nWorking on week: {week_num}")
    print("-" * 40)

    # === FETCH DATA FROM API ===
    print("\n[1/3] Fetching data from Yahoo API...")
    get_league_standings(week=week_num)
    get_league_weekly_scoreboard(week=week_num)
    get_league_transactions(week=week_num, is_main=True)

    # === PARSE SCOREBOARD ===
    print("\n[2/3] Parsing response data...")
    is_scoreboard_parsing_exists = False
    weekly_scoreboard_file = Path(f"response/scoreboard_week_{week_num}.json")
    if not weekly_scoreboard_file.exists():
        print(f"  ✗ Scoreboard file not found: {weekly_scoreboard_file}")
    else:
        is_scoreboard_parsing_exists = True
        with open(weekly_scoreboard_file, "r", encoding="utf-8") as f:
            response_scoreboard_weekly = json.load(f)
        parsed_scoreboard_weekly = parse_weekly_scoreboard(data=response_scoreboard_weekly, week=week_num)

        # Save to file
        path = f"league_data/weekly_scoreboard/parsed_scoreboard_week_{week_num}.json"
        save_parsed_response_to_file(parsed_scoreboard_weekly, path)
        print("  ✓ Scoreboard parsed and saved")

    # === PARSE STANDINGS ===
    is_standings_parsing_exists = False
    weekly_standings_file = Path(f"response/standings_{week_num}.json")
    if not weekly_standings_file.exists():
        print(f"  ✗ Standings file not found: {weekly_standings_file}")
    else:
        is_standings_parsing_exists = True
        with open(weekly_standings_file, "r", encoding="utf-8") as f:
            response_standings_weekly = json.load(f)
        parsed_standings_weekly = parse_weekly_standings(data=response_standings_weekly, week=week_num)

        # Save to file
        path = f"league_data/weekly_standings_and_totals/parsed_standings_week_{week_num}.json"
        save_parsed_response_to_file(parsed_standings_weekly, path)
        print("  ✓ Standings parsed and saved")

    # === PARSE TRANSACTIONS ===
    is_transactions_parsing_exists = False
    transactions_file = Path(f"response/main_transactions_week_{week_num}.json")
    if not transactions_file.exists():
        print(f"  ✗ Transactions file not found: {transactions_file}")
    else:
        is_transactions_parsing_exists = True
        with open(transactions_file, "r", encoding="utf-8") as f:
            response_transactions = json.load(f)
        parsed_transactions = parse_league_transactions(data=response_transactions)
        save_league_transactions(parsed_transactions)
        print("  ✓ Transactions parsed and merged")

    if not is_standings_parsing_exists and not is_scoreboard_parsing_exists:
        print("\n✗ Neither weekly standings nor scoreboard were parsed due to technical errors")
        sys.exit(1)

    # === GENERATE VISUALIZATIONS ===
    print("\n[3/3] Generating visualizations...")
    os.makedirs(f"visualization/graphs/week_{week_num}", exist_ok=True)

    if is_standings_parsing_exists:
        # Run Standings Bump Chart generation
        print("\n  → Standings Bump Chart")
        run_standings_bump_chart(week_end=week_num, week_start="1")

    if is_scoreboard_parsing_exists:
        # Run Totals Table generation
        print("\n  → Totals Table (Weekly)")
        run_totals_table_visualization(week=week_num)

        # Run Ranking Table generation
        print("\n  → Ranking Table (Weekly)")
        run_ranking_table_visualization(week=week_num)

        # Run Head-to-Head matrix generation
        print("\n  → Head-to-Head Matrix")
        run_head_to_head_visualization(week=week_num)

        # Run Periodical Totals Table generation (Weeks current week - 3 to current week)
        print(f"\n  → Totals Table (Periodical: Weeks {int(week_num)-3}-{week_num})")
        run_periodical_totals_table_visualization(end_week=int(week_num), start_week=int(week_num)-3)

        # Run Periodical Ranking Table generation (Weeks current week - 3 to current week)
        print(f"\n  → Ranking Table (Periodical: Weeks {int(week_num)-3}-{week_num})")
        run_periodical_ranking_table_visualization(end_week=int(week_num), start_week=int(week_num)-3)

    if is_transactions_parsing_exists:
        # Run Transaction visualizations
        print("\n  → Transaction Visualizations")
        folder_name = f"week_{week_num}"
        run_most_added_dropped_visualization(folder_name)
        run_team_activity_visualization(folder_name)
        run_pickup_tenure_visualization(folder_name)

    print("\n" + "=" * 50)
    print("✓ All visualizations generated successfully!")
    print(f"  Output folder: visualization/graphs/week_{week_num}/")
    print("=" * 50)


if __name__ == "__main__":
    print(f"League specs: {LEAGUE_KEY}")
    main()
