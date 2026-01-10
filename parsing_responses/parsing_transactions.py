"""Parse transaction responses from Yahoo Fantasy API.

Handles both league-wide and team-specific transaction responses.
Extracts: transaction type, timestamp, players involved, source/destination info.
"""

from datetime import datetime
from typing import Any, Dict, List

try:
    from consts import safe_get, extract_from_list_of_dicts, MANAGER_ID_TO_NAME_MAP
except ImportError:
    from parsing_responses.consts import safe_get, extract_from_list_of_dicts, MANAGER_ID_TO_NAME_MAP


def parse_player_from_transaction(player_data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse a single player entry from a transaction."""
    player_info = player_data.get("player", [])

    if not player_info or len(player_info) < 2:
        return {}

    # First element is a list of player attributes
    player_attrs = player_info[0] if isinstance(player_info[0], list) else []

    player_id = extract_from_list_of_dicts(player_attrs, "player_id")
    name_dict = extract_from_list_of_dicts(player_attrs, "name") or {}
    player_name = name_dict.get("full", "") if isinstance(name_dict, dict) else ""
    nba_team = extract_from_list_of_dicts(player_attrs, "editorial_team_abbr") or ""
    position = extract_from_list_of_dicts(player_attrs, "display_position") or ""

    # Second element contains transaction_data
    transaction_data_wrapper = player_info[1] if len(player_info) > 1 else {}
    transaction_data = transaction_data_wrapper.get("transaction_data", {})

    # transaction_data can be a dict or a list with one dict
    if isinstance(transaction_data, list) and len(transaction_data) > 0:
        transaction_data = transaction_data[0]
    
    # Ensure transaction_data is a dict before calling .get()
    if not isinstance(transaction_data, dict):
        transaction_data = {}

    return {
        "player_id": player_id,
        "player_name": player_name,
        "nba_team": nba_team,
        "position": position,
        "action_type": transaction_data.get("type", ""),
        "source_type": transaction_data.get("source_type", ""),
        "source_team_name": transaction_data.get("source_team_name", ""),
        "destination_type": transaction_data.get("destination_type", ""),
        "destination_team_name": transaction_data.get("destination_team_name", ""),
    }


def parse_single_transaction(transaction_data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse a single transaction entry."""
    transaction_list = transaction_data.get("transaction", [])

    if not transaction_list or len(transaction_list) < 2:
        return {}

    # First element contains transaction metadata
    meta = transaction_list[0]
    transaction_id = meta.get("transaction_id", "")
    transaction_type = meta.get("type", "")
    status = meta.get("status", "")
    timestamp_raw = meta.get("timestamp", "")

    # Convert timestamp to readable date
    try:
        timestamp_int = int(timestamp_raw)
        transaction_date = datetime.fromtimestamp(timestamp_int).strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        transaction_date = ""

    # Trade-specific fields
    trader_team_name = meta.get("trader_team_name", "")
    tradee_team_name = meta.get("tradee_team_name", "")

    # Second element contains players
    players_wrapper = transaction_list[1]
    players_dict = players_wrapper.get("players", {})

    players = []
    player_count = players_dict.get("count", 0)

    for i in range(player_count):
        player_data = players_dict.get(str(i), {})
        if player_data:
            parsed_player = parse_player_from_transaction(player_data)
            if parsed_player:
                players.append(parsed_player)

    return {
        "transaction_id": transaction_id,
        "type": transaction_type,
        "status": status,
        "timestamp": timestamp_raw,
        "date": transaction_date,
        "trader_team_name": trader_team_name,
        "tradee_team_name": tradee_team_name,
        "players": players,
    }


def parse_league_transactions(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Parse league-wide transactions response.

    Args:
        data: Raw JSON response from /league/{key}/transactions endpoint

    Returns:
        List of parsed transaction dictionaries
    """
    print("Parsing league transactions...")
    result = []

    try:
        league_data = safe_get(data, "fantasy_content", "league")

        if not isinstance(league_data, list) or len(league_data) < 2:
            print("Invalid league data structure")
            return result

        transactions_wrapper = league_data[1]
        transactions_dict = transactions_wrapper.get("transactions", {})

        transaction_count = transactions_dict.get("count", 0)
        print(f"Found {transaction_count} transactions")

        for i in range(transaction_count):
            transaction_data = transactions_dict.get(str(i), {})
            if transaction_data:
                parsed = parse_single_transaction(transaction_data)
                if parsed and parsed.get("transaction_id"):
                    result.append(parsed)

    except Exception as e:
        print(f"Error parsing league transactions: {e}")

    print(f"Successfully parsed {len(result)} transactions")
    return result


def parse_team_transactions(data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse team-specific transactions response.

    Args:
        data: Raw JSON response from /team/{key}/transactions endpoint

    Returns:
        Dictionary with team info and list of transactions
    """
    print("Parsing team transactions...")
    result = {
        "team_id": "",
        "team_name": "",
        "number_of_moves": 0,
        "number_of_trades": 0,
        "transactions": []
    }

    try:
        team_data = safe_get(data, "fantasy_content", "team")

        if not isinstance(team_data, list) or len(team_data) < 2:
            print("Invalid team data structure")
            return result

        # First element is team info (list of dicts)
        team_info = team_data[0]
        if isinstance(team_info, list):
            result["team_id"] = extract_from_list_of_dicts(team_info, "team_id") or ""
            result["team_name"] = extract_from_list_of_dicts(team_info, "name") or ""
            result["number_of_moves"] = extract_from_list_of_dicts(team_info, "number_of_moves") or 0
            result["number_of_trades"] = extract_from_list_of_dicts(team_info, "number_of_trades") or "0"

        print(f"Team: {result['team_name']} (ID: {result['team_id']})")
        print(f"Total moves: {result['number_of_moves']}, Trades: {result['number_of_trades']}")

        # Second element contains transactions
        transactions_wrapper = team_data[1]
        transactions_dict = transactions_wrapper.get("transactions", {})

        transaction_count = transactions_dict.get("count", 0)
        print(f"Found {transaction_count} transactions")

        for i in range(transaction_count):
            transaction_data = transactions_dict.get(str(i), {})
            if transaction_data:
                parsed = parse_single_transaction(transaction_data)
                if parsed and parsed.get("transaction_id"):
                    result["transactions"].append(parsed)

    except Exception as e:
        print(f"Error parsing team transactions: {e}")

    print(f"Successfully parsed {len(result['transactions'])} transactions")
    return result


def get_transaction_summary(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate summary statistics from parsed transactions.

    Args:
        transactions: List of parsed transaction dictionaries

    Returns:
        Summary dictionary with counts and breakdowns
    """
    summary = {
        "total_transactions": len(transactions),
        "by_type": {"add": 0, "drop": 0, "add/drop": 0, "trade": 0},
        "by_team": {},
        "most_added_players": {},
        "most_dropped_players": {},
    }

    for txn in transactions:
        txn_type = txn.get("type", "")
        if txn_type in summary["by_type"]:
            summary["by_type"][txn_type] += 1

        for player in txn.get("players", []):
            player_name = player.get("player_name", "Unknown")
            action = player.get("action_type", "")
            dest_team = player.get("destination_team_name", "")
            src_team = player.get("source_team_name", "")

            # Track team activity
            if dest_team:
                summary["by_team"][dest_team] = summary["by_team"].get(dest_team, 0) + 1
            if src_team and action == "drop":
                summary["by_team"][src_team] = summary["by_team"].get(src_team, 0) + 1

            # Track player movements
            if action == "add":
                summary["most_added_players"][player_name] = \
                    summary["most_added_players"].get(player_name, 0) + 1
            elif action == "drop":
                summary["most_dropped_players"][player_name] = \
                    summary["most_dropped_players"].get(player_name, 0) + 1

    return summary


def save_league_transactions(new_transactions: List[Dict[str, Any]]) -> Path:
    """Save parsed league transactions, merging with existing data.

    Loads existing transactions if file exists, merges with new transactions
    (deduplicating by transaction_id), and saves the combined result.

    Args:
        new_transactions: List of newly parsed transaction dictionaries

    Returns:
        Path to saved file
    """
    import json
    from pathlib import Path

    output_dir = Path("league_data/transactions")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "parsed_league_transactions.json"

    # Load existing transactions if file exists
    existing_transactions = []
    if output_path.exists():
        with open(output_path, "r", encoding="utf-8") as f:
            existing_transactions = json.load(f)

    # Merge transactions, deduplicating by transaction_id
    existing_ids = {t["transaction_id"] for t in existing_transactions}
    merged = existing_transactions.copy()

    new_count = 0
    for txn in new_transactions:
        if txn["transaction_id"] not in existing_ids:
            merged.append(txn)
            new_count += 1

    # Sort by timestamp (newest first)
    merged.sort(key=lambda x: int(x.get("timestamp", 0)), reverse=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)

    print(f"Added {new_count} new transactions (total: {len(merged)})")
    return output_path


def save_team_transactions(new_team_data: Dict[str, Any]) -> Path:
    """Save parsed team transactions, merging with existing data.

    Args:
        new_team_data: Parsed team transaction data with 'team_id' and 'transactions'

    Returns:
        Path to saved file
    """
    import json
    from pathlib import Path

    output_dir = Path("league_data/transactions")
    output_dir.mkdir(parents=True, exist_ok=True)

    team_id = new_team_data.get("team_id", "unknown")
    output_path = output_dir / f"parsed_transactions_team_{team_id}.json"

    # Load existing data if file exists
    existing_data = {"team_id": team_id, "team_name": "", "transactions": []}
    if output_path.exists():
        with open(output_path, "r", encoding="utf-8") as f:
            existing_data = json.load(f)

    # Merge transactions
    existing_ids = {t["transaction_id"] for t in existing_data.get("transactions", [])}
    merged_txns = existing_data.get("transactions", []).copy()

    new_count = 0
    for txn in new_team_data.get("transactions", []):
        if txn["transaction_id"] not in existing_ids:
            merged_txns.append(txn)
            new_count += 1

    # Sort by timestamp (newest first)
    merged_txns.sort(key=lambda x: int(x.get("timestamp", 0)), reverse=True)

    # Update team data
    result = {
        "team_id": new_team_data.get("team_id", existing_data.get("team_id", "")),
        "team_name": new_team_data.get("team_name", existing_data.get("team_name", "")),
        "number_of_moves": new_team_data.get("number_of_moves", existing_data.get("number_of_moves", 0)),
        "number_of_trades": new_team_data.get("number_of_trades", existing_data.get("number_of_trades", 0)),
        "transactions": merged_txns
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Added {new_count} new transactions for team {team_id} (total: {len(merged_txns)})")
    return output_path


if __name__ == "__main__":
    import json
    from pathlib import Path

    print("=" * 60)
    print("Transaction Parser")
    print("=" * 60)

    print("\nChoose parsing:")
    print("1. League Transactions")
    print("2. Team Transactions")
    choice = input("Enter choice (1 or 2): ").strip()

    if choice not in {"1", "2"}:
        print("Invalid choice. Exiting.")
        exit(1)

    if choice == "1":
        print("\nParsing League Transactions...")

        # Parse league transactions
        league_file = Path("response/parsed_league_transactions.json")
        if league_file.exists():
            print(f"\nLoading {league_file}...")
            with open(league_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            transactions = parse_league_transactions(data)
            output_path = save_league_transactions(transactions)
            print(f"Saved to: {output_path}")

            # Print summary
            summary = get_transaction_summary(transactions)
            print(f"\nSummary:")
            print(f"  Total transactions: {summary['total_transactions']}")
            print(f"  By type: {summary['by_type']}")
            sorted_teams = sorted(summary['by_team'].items(), key=lambda x: -x[1])
            print(f"  Top 5 teams by activity:")
            for team, count in sorted_teams[:5]:
                try:
                    print(f"    {team}: {count}")
                except UnicodeEncodeError:
                    print(f"    [Team with special chars]: {count}")
        else:
            print(f"League transactions file not found: {league_file}")
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

        # Parse team transactions
        team_file = Path(f"response/main_team_transactions_{team_choice}.json")
        if team_file.exists():
            print(f"\nLoading {team_file}...")
            with open(team_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            team_data = parse_team_transactions(data)
            output_path = save_team_transactions(team_data)
            print(f"Saved to: {output_path}")
        else:
            print(f"Team transactions file not found: {team_file}")
