from typing import Any, Dict, List
import json
import os

# Stat ID → readable name
STAT_ID_TO_NAME_MAP = {
    "5":  "FG%",
    "8": "FT%",
    "10": "3PTM",
    "12": "PTS",
    "15": "REB",
    "16": "AST",
    "17": "STL",
    "18": "BLK",
    "19": "TO",
    "9004003": "FGM/FGA",
    "9007006": "FTM/FTA"
}

# Manager ID → Manager Name
MANAGER_ID_TO_NAME_MAP = {
    "1": "Bucharest Panthers",
    "2": "The Perfumer",
    "3": "Nahi's BOYS",
    "4": "LeBrother In Law",
    "5": "F.C HATERS",
    "6": "LevinSons",
    "7": "Maple Mamba",
    "8": "Tomitz Tapuzim B.C",
    "9": "המטביל",
    "10": "ג'יי ג'יי רדי"
}


def safe_get(d, *keys, default=None):
    """
    Robust nested getter for Yahoo Fantasy API responses.

    Behavior summary:
      - If d is dict and key in d -> follow it.
      - If d is dict and key is int -> try str(key) as a dict key (handles "0","1" style).
      - If d is dict and key is str but not present -> search dict values for a dict containing key.
      - If d is list and key is int -> index the list.
      - If d is list and key is str -> search list elements for the first dict that contains key.
      - If a step can't be resolved -> return default.
    """
    for key in keys:
        if d is None:
            return default

        # --- Case A: current node is a dict ---
        if isinstance(d, dict):
            # Direct hit
            if key in d:
                d = d[key]
                continue

            # If key is int but dict uses numeric-string indices
            if isinstance(key, int):
                sk = str(key)
                if sk in d:
                    d = d[sk]
                    continue

            # If key is a str but not present: search values for a dict that contains this key
            if isinstance(key, str):
                found = False
                for v in d.values():
                    # If a value is a dict and contains the key directly, use it
                    if isinstance(v, dict) and key in v:
                        d = v[key]
                        found = True
                        break
                    # If a value is a dict with numeric-string subkeys (like {"0": {...}}),
                    # check those inner dicts as well
                    if isinstance(v, dict):
                        for inner in v.values():
                            if isinstance(inner, dict) and key in inner:
                                d = inner[key]
                                found = True
                                break
                        if found:
                            break
                if found:
                    continue

            # Not found on this dict
            return default

        # --- Case B: current node is a list ---
        if isinstance(d, list):
            # If user asked numeric index
            if isinstance(key, int):
                if 0 <= key < len(d):
                    d = d[key]
                    continue
                else:
                    return default

            # If user asked for a string key: scan list elements for that key
            if isinstance(key, str):
                found = False
                for item in d:
                    if isinstance(item, dict) and key in item:
                        d = item[key]
                        found = True
                        break
                if found:
                    continue

                # As fallback, check dict elements which themselves have numeric-string keys
                for item in d:
                    if isinstance(item, dict):
                        for v in item.values():
                            if isinstance(v, dict) and key in v:
                                d = v[key]
                                found = True
                                break
                        if found:
                            break
                if found:
                    continue

                return default

        # Any other type cannot be traversed
        return default

    return d

def extract_from_list_of_dicts(lst, key):
    """Given a list like [{a:1}, {b:2}, ...], return the value for dict[key]."""
    if not isinstance(lst, list):
        return None
    for item in lst:
        if isinstance(item, dict) and key in item:
            return item[key]
    return None

def save_parsed_response_to_file(response: List[Dict[str, Any]], path: str) -> None:
    """Save parsed response to a JSON file"""
    
    file_name, file_extension = os.path.splitext(path)
    if file_extension.lower() != ".json":
        path = f"{file_name}.json"

    try:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(response, file, indent=2, ensure_ascii=False)
        print(f"Parsed response saved to {path}")
    except Exception as e:
        print(f"Failed to save parsed response to {path}: {e}")

def save_response_to_file(response: Dict[str, Any], path: str) -> None:
    """Save parsed response to a JSON file"""
    
    file_name, file_extension = os.path.splitext(path)
    if file_extension.lower() != ".json":
        path = f"{file_name}.json"
        
    try:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(response, file, indent=2, ensure_ascii=False)
        print(f"Parsed response saved to {path}")
    except Exception as e:
        print(f"Failed to save parsed response to {path}: {e}")

# def extract_stats_from_response(stats_structure: list[Any]) -> List[Dict[str, Any]]:
#     return []

# # `safe_get` helper function for parsing Yahoo's inconsistent response structures
# # returns the nested value if exists
# # if doesn't exist OR index out of range OR type mismatch it returns `default`
# def safe_get(d, *keys, default=None):
#     """Safely get nested values from Yahoo's wildly inconsistent structures."""
#     for key in keys:
#         if d is None:
#             return default

#         # Case 1: dict with string key
#         if isinstance(d, dict) and key in d:
#             d = d[key]
#             continue

#         # Case 2: dict pretending to be a list ("0", "1", ...)
#         if isinstance(d, dict) and isinstance(key, int):
#             str_key = str(key)
#             if str_key in d:
#                 d = d[str_key]
#                 continue

#         # Case 3: normal list index
#         if isinstance(d, list) and isinstance(key, int) and key < len(d):
#             d = d[key]
#             continue

#         # Key not found
#         return default

#     return d