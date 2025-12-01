"""
Main entry point for Yahoo NBA Fantasy Hub application.
Handles OAuth authentication and token management.
"""

import sys
import json
from yahoo_api_handler import YahooAPIHandler
from config import LEAGUE_KEY
from parsing_responses.parsing_weekly_scoreboard import parse_weekly_scoreboard
from parsing_responses.parsing_weekly_standings import parse_weekly_standings
from parsing_responses.consts import *
from api.get_standings import get_league_standings
from api.get_scoreboard import get_league_weekly_scoreboard
from visualization.totals_table import run_totals_table_visualization
from visualization.ranking_table import run_ranking_table_visualization
from visualization.head_to_head import run_head_to_head_visualization

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

    # TODO: Add await for user input logic 
    print("Ready to make API requests to Yahoo Fantasy API")
    week_num = "4"
    get_league_standings(week=week_num)
    get_league_weekly_scoreboard(week=week_num)

    response_scoreboard_weekly = json.load(open(f"response/scoreboard_week_{week_num}.json", "r", encoding="utf-8")) 
    parsed_scoreboard_weekly = parse_weekly_scoreboard(data=response_scoreboard_weekly, week=week_num)

    # Save to file
    path = f"league_data/weekly_scoreboard/parsed_scoreboard_week_{week_num}.json"
    save_parsed_response_to_file(parsed_scoreboard_weekly, path)

    response_standings_weekly = json.load(open(f"response/standings_{week_num}.json", "r", encoding="utf-8"))
    parsed_standings_weekly = parse_weekly_standings(data=response_standings_weekly, week=week_num)

    # Save to file
    path = f"league_data/weekly_standings_and_totals/parsed_standings_week_{week_num}.json"
    save_parsed_response_to_file(parsed_standings_weekly, path)

    ## Run visualization generation ##
    print("\nGenerating visualizations...")
    os.makedirs(f"visualization/graphs/week_{week_num}", exist_ok=True)
    print("Created directory:", f"visualization/graphs/week_{week_num}")

    # Run Totals Table generation
    run_totals_table_visualization(week=week_num)

    # Run Ranking Table generation
    run_ranking_table_visualization(week=week_num)

    # Run Head-to-Head matrix generation
    run_head_to_head_visualization(week=week_num)


if __name__ == "__main__":
    print(f"League specs: {LEAGUE_KEY}")
    main()
