"""
Main entry point for Yahoo NBA Fantasy Hub application.
Handles OAuth authentication and token management.
"""

import sys
import json
from yahoo_api_handler import YahooAPIHandler
from config import LEAGUE_KEY

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

    # TODO: Add your application logic here
    print("Ready to make API requests to Yahoo Fantasy API")
    get_league_standings()

def get_league_standings() -> None:
    """Fetch and display league standings from Yahoo Fantasy API."""
    try:
        print("Fetching league standings...")
        response = YahooAPIHandler.make_request(f"/league/{LEAGUE_KEY}/standings", method="GET", params={"format": "json"})
        # Check if request was successful
        if response.status_code == 200:
            standings = response.json()

            # Save to file
            with open("response/standings.json", "w", encoding="utf-8") as f:
                json.dump(standings, f, indent=2, ensure_ascii=False)

            print("✅ JSON response saved successfully to response.json")
        else:
            print(f"Failed to fetch standings. Status code: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Failed to fetch league standings: {e}")

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
            with open(f"response/scoreboard_week_{week}.json", "w", encoding="utf-8") as f:
                json.dump(scoreboard, f, indent=2, ensure_ascii=False)

            print(f"✅ JSON response saved successfully to scoreboard_week_{week}.json")
        else:
            print(f"Failed to fetch scoreboard for week {week}. Status code: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Failed to fetch league scoreboard for week {week}: {e}")

if __name__ == "__main__":
    print(f"League specs: {LEAGUE_KEY}")
    main()
