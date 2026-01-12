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

The league uses classic 9 categories scoring system:
- FG%, FT%, 3PTM, PTS, REB, AST, STL, BLK, TO
- FGM, FGA, FTM and FTA are included in both totals and ranking tables but aren't part of the scoring system or calculation system for the weekly average ranking.

## Output

- Weekly visualizations: `visualization/graphs/week_{N}/`
- Periodical visualizations: `visualization/graphs/weeks_{start}_to_{end}/`

## Graph Examples
### Weekly Totals Table
<img width="708" height="379" alt="styled_totals_week_12" src="https://github.com/user-attachments/assets/9dd01266-2da4-47c7-ae57-ce453aa81ba9" />

### Weekly Ranking Table
<img width="778" height="349" alt="styled_ranking_week_12" src="https://github.com/user-attachments/assets/1efaa1de-204c-489c-88c0-cf314614d4c0" />

### Head-to-Head Matrix
<img width="1268" height="424" alt="H2H_week_12" src="https://github.com/user-attachments/assets/24bce969-cc21-47ad-9e8a-17fc5659440a" />

### Standings Bump Chart
<img width="2084" height="1185" alt="Standings_Bump_Chart_Until_Week_12" src="https://github.com/user-attachments/assets/d6cc29ad-01bf-4752-baaa-7344a832083c" />

### Transactions Visualizations
  #### Most Added/Dropped Players
  <img width="2385" height="1473" alt="most_added_dropped_players" src="https://github.com/user-attachments/assets/a601f6cf-8f45-43f7-a780-fad7428de742" />
  
  #### Team Transactions Activity
  <img width="2084" height="1483" alt="team_transaction_activity" src="https://github.com/user-attachments/assets/aa4c05d5-6622-4125-b0c1-974aaab8c36a" />
  
  #### Longest Pickups Tenure
  <img width="2085" height="1483" alt="pickup_tenure" src="https://github.com/user-attachments/assets/d4d325f3-76c2-464d-b834-486501782697" />
