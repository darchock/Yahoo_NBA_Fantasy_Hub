# Yahoo NBA Fantasy Hub (CLI Tool)

A command-line Python application for tracking and visualizing Yahoo Fantasy Basketball league statistics.

## Features

- OAuth2 authentication with Yahoo Fantasy API
- Weekly scoreboard and standings data fetching
- Visual reports generation (PNG images):
  - **Totals Table** - Team stats per category with color gradients (weekly or periodical)
  - **Ranking Table** - Teams ranked 1-10 per category with average rank (weekly or periodical)
  - **Head-to-Head Matrix** - Win-loss-tie records between all teams
  - **Standings Bump Chart** - Ranking changes over multiple weeks
  - **Transaction Analysis** - Most added/dropped players, team activity, pickup tenure

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment variables

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Then edit `.env` with your values:
- **YAHOO_CLIENT_ID** / **YAHOO_CLIENT_SECRET** - Get these from [Yahoo Developer Apps](https://developer.yahoo.com/apps/)
- **LEAGUE_ID** - Your Yahoo Fantasy league ID (found in your league URL)

### 3. Create config.py

Create `config.py` that reads from environment variables:

```python
import os
from dotenv import load_dotenv

load_dotenv()

YAHOO_CLIENT_ID = os.getenv("YAHOO_CLIENT_ID")
YAHOO_CLIENT_SECRET = os.getenv("YAHOO_CLIENT_SECRET")
YAHOO_REDIRECT_URI = os.getenv("YAHOO_REDIRECT_URI", "https://localhost:8080/callback")
TOKEN_FILE = "token_cache.json"
LEAGUE_ID = os.getenv("LEAGUE_ID")
LEAGUE_KEY = f"nba.l.{LEAGUE_ID}"
```

## Usage

```bash
# Run the application (prompts for week number)
python main.py

# Authentication commands
python main.py --auth <code>  # Complete OAuth with authorization code
python main.py --test         # Test token validity
python main.py --reset        # Clear cached token
```

## Scoring Categories

The league uses 9 roto-style scoring categories:
- FG%, FT%, 3PTM, PTS, REB, AST, STL, BLK, TO

## Output

- Weekly visualizations: `visualization/graphs/week_{N}/`
- Periodical visualizations: `visualization/graphs/weeks_{start}_to_{end}/`
