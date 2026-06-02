#!/usr/bin/env python3
"""
Fetch FIFA World Cup 2026 matches for a given team and write to games.json.

Usage:
    python fetch_matches.py                         # defaults to Brazil (BRA)
    python fetch_matches.py --country BRA
    python fetch_matches.py --country ARG
    python fetch_matches.py --team "Argentina"
"""

import argparse
import json
import sys
from datetime import datetime, timezone

import requests

FIFA_API = "https://api.fifa.com/api/v3/calendar/matches"
ID_COMPETITION = "17"
ID_SEASON = "285023"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
}


def fetch_all_matches() -> list[dict]:
    params = {
        "idCompetition": ID_COMPETITION,
        "idSeason": ID_SEASON,
        "count": 500,
        "language": "en-GB",
    }
    resp = requests.get(FIFA_API, params=params, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("Results", [])


def locale_str(arr: list[dict] | None) -> str:
    if not arr:
        return ""
    for item in arr:
        if item.get("Locale") in ("en-GB", "en-US"):
            return item["Description"]
    return arr[0].get("Description", "") if arr else ""


def team_matches(matches: list[dict], country_code: str | None, team_name: str | None) -> list[dict]:
    result = []
    for m in matches:
        home = m.get("Home") or {}
        away = m.get("Away") or {}
        home_country = (home.get("IdCountry") or "").upper()
        away_country = (away.get("IdCountry") or "").upper()
        home_name = locale_str(home.get("TeamName") or []).lower()
        away_name = locale_str(away.get("TeamName") or []).lower()

        match_found = False
        if country_code:
            code = country_code.upper()
            match_found = home_country == code or away_country == code
        if team_name and not match_found:
            name = team_name.lower()
            match_found = name in home_name or name in away_name

        if match_found:
            result.append(m)
    return result


def format_match(m: dict) -> dict:
    home = m.get("Home") or {}
    away = m.get("Away") or {}
    stadium = m.get("Stadium") or {}

    home_score = m.get("HomeTeamScore")
    away_score = m.get("AwayTeamScore")

    return {
        "matchNumber": m.get("MatchNumber"),
        "idMatch": m.get("IdMatch"),
        "dateUtc": m.get("Date"),
        "dateLocal": m.get("LocalDate"),
        "stage": locale_str(m.get("StageName") or []),
        "group": locale_str(m.get("GroupName") or []) or None,
        "matchday": m.get("MatchDay"),
        "matchStatus": m.get("MatchStatus"),
        "home": {
            "name": locale_str(home.get("TeamName") or []) or home.get("Abbreviation"),
            "country": home.get("IdCountry"),
            "abbreviation": home.get("Abbreviation"),
            "idTeam": home.get("IdTeam"),
            "flagUrl": home.get("PictureUrl"),
        },
        "away": {
            "name": locale_str(away.get("TeamName") or []) or away.get("Abbreviation"),
            "country": away.get("IdCountry"),
            "abbreviation": away.get("Abbreviation"),
            "idTeam": away.get("IdTeam"),
            "flagUrl": away.get("PictureUrl"),
        },
        "score": {
            "home": home_score,
            "away": away_score,
            "homePenalty": m.get("HomeTeamPenaltyScore"),
            "awayPenalty": m.get("AwayTeamPenaltyScore"),
        },
        "venue": {
            "stadium": locale_str(stadium.get("Name") or []),
            "city": locale_str(stadium.get("CityName") or []),
            "country": stadium.get("IdCountry"),
        },
        "winner": m.get("Winner"),
    }


def main():
    parser = argparse.ArgumentParser(description="Fetch FIFA World Cup 2026 matches for a team.")
    parser.add_argument("--country", default="BRA", help="FIFA 3-letter country code (e.g. BRA, ARG, FRA)")
    parser.add_argument("--team", default=None, help="Team name (e.g. 'Brazil'). Used if --country has no match.")
    parser.add_argument("--output", default="games.json", help="Output file path (default: games.json)")
    args = parser.parse_args()

    print(f"Fetching matches from FIFA API...")
    try:
        all_matches = fetch_all_matches()
    except requests.RequestException as e:
        print(f"Error fetching data: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Total matches fetched: {len(all_matches)}")

    filtered = team_matches(all_matches, args.country, args.team)
    print(f"Matches found for {args.country or args.team}: {len(filtered)}")

    if not filtered:
        print("No matches found. Check your --country or --team value.", file=sys.stderr)
        sys.exit(1)

    team_name = locale_str((filtered[0].get("Home") or {}).get("TeamName") or [])
    country_code = (filtered[0].get("Home") or {}).get("IdCountry")
    for m in filtered:
        for side in [m.get("Home") or {}, m.get("Away") or {}]:
            if (side.get("IdCountry") or "").upper() == (args.country or "").upper():
                team_name = locale_str(side.get("TeamName") or [])
                country_code = side.get("IdCountry")
                break

    output = {
        "tournament": "FIFA World Cup 2026",
        "idCompetition": ID_COMPETITION,
        "idSeason": ID_SEASON,
        "team": args.country or args.team,
        "teamName": team_name,
        "source": f"{FIFA_API}?idCompetition={ID_COMPETITION}&idSeason={ID_SEASON}",
        "generatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "matchCount": len(filtered),
        "matches": [format_match(m) for m in sorted(filtered, key=lambda x: x.get("Date") or "")],
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Written to {args.output}")


if __name__ == "__main__":
    main()
