"""
Functions that fetch driver / track / team details from FastF1, the Ergast
community API, or fall back to hardcoded constants.

Every public function returns plain dicts / lists — no DB models involved.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any

import httpx

from src.data.constants import (
    COUNTRIES,
    DRIVER_SKILL_OVERRIDES,
    DRIVERS,
    ERGAST_BASE_URL,
    SKILLS,
    TEAMS,
    TRACKS,
)

logger = logging.getLogger(__name__)


# ── FastF1 helpers ────────────────────────────────────────────────────────


def _try_fastf1_driver_numbers(season: int = 2025) -> dict[str, int]:
    """Load a FastF1 session and extract driver numbers.

    Args:
        season: F1 season year to fetch data for.

    Returns:
        Mapping of driver full name to race number, or empty dict on failure.
    """
    try:
        import fastf1

        fastf1.Cache.enable_cache(".f1cache")
        session = fastf1.get_session(season, 1, "R")
        session.load(telemetry=False, weather=False, laps=False, messages=False)
        numbers: dict[str, int] = {}
        for _, row in session.results.iterrows():
            name = f"{row['FirstName']} {row['LastName']}"
            numbers[name] = int(row["DriverNumber"])
        logger.info("FastF1: fetched %d driver numbers for %d", len(numbers), season)
        return numbers
    except Exception as exc:
        logger.warning("FastF1 driver‑number fetch failed: %s", exc)
        return {}


def _try_fastf1_track_laps(season: int = 2025) -> dict[str, int]:
    """Fetch total race laps per track from FastF1 session data.

    Args:
        season: F1 season year to fetch data for.

    Returns:
        Mapping of event name to total laps, or empty dict on failure.
    """
    try:
        import fastf1

        fastf1.Cache.enable_cache(".f1cache")
        schedule = fastf1.get_event_schedule(season)
        laps_map: dict[str, int] = {}
        for _, event in schedule.iterrows():
            name = event.get("EventName") or event.get("OfficialEventName", "")
            if not name:
                continue
            try:
                race = fastf1.get_session(season, name, "R")
                race.load(telemetry=False, weather=False, laps=True, messages=False)
                total = int(race.laps["LapNumber"].max())
                laps_map[name] = total
            except Exception:
                continue
        logger.info(
            "FastF1: fetched lap counts for %d tracks in %d", len(laps_map), season
        )
        return laps_map
    except Exception as exc:
        logger.warning("FastF1 track‑laps fetch failed: %s", exc)
        return {}


# ── Ergast community API helpers ──────────────────────────────────────────


def _ergast_get(path: str) -> dict | None:
    """Send a GET request to the Ergast community API mirror.

    Args:
        path: API path appended to the base URL (e.g. "2025/drivers.json").

    Returns:
        Parsed JSON response dict, or None on failure.
    """
    url = f"{ERGAST_BASE_URL}/{path}"
    try:
        resp = httpx.get(url, timeout=10, follow_redirects=True)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        logger.warning("Ergast request failed (%s): %s", url, exc)
        return None


def _fetch_ergast_driver_list(season: int = 2025) -> dict[str, dict[str, Any]]:
    """Fetch the driver list for a season from the Ergast API.

    Args:
        season: F1 season year.

    Returns:
        Mapping of driver full name to a dict with number, code,
        nationality, and date of birth.
    """
    data = _ergast_get(f"{season}/drivers.json?limit=100")
    if not data:
        return {}
    try:
        drivers_raw = data["MRData"]["DriverTable"]["Drivers"]
        result: dict[str, dict[str, Any]] = {}
        for d in drivers_raw:
            name = f"{d['givenName']} {d['familyName']}"
            result[name] = {
                "number": int(d.get("permanentNumber", 0)),
                "code": d.get("code", ""),
                "nationality": d.get("nationality", ""),
                "dob": d.get("dateOfBirth", ""),
            }
        logger.info("Ergast: fetched %d drivers for %d", len(result), season)
        return result
    except (KeyError, TypeError):
        return {}


def _fetch_ergast_circuits() -> dict[str, dict[str, Any]]:
    """Fetch all known circuits from the Ergast API.

    Returns:
        Mapping of circuit name to a dict with country, locality,
        latitude, and longitude.
    """
    data = _ergast_get("circuits.json?limit=100")
    if not data:
        return {}
    try:
        circuits = data["MRData"]["CircuitTable"]["Circuits"]
        result: dict[str, dict[str, Any]] = {}
        for c in circuits:
            result[c["circuitName"]] = {
                "country": c["Location"]["country"],
                "locality": c["Location"]["locality"],
                "lat": c["Location"].get("lat"),
                "lng": c["Location"].get("long"),
            }
        logger.info("Ergast: fetched %d circuits", len(result))
        return result
    except (KeyError, TypeError):
        return {}


def _fetch_ergast_career_stats(driver_id: str) -> dict[str, Any]:
    """Fetch career race results for a driver from the Ergast API.

    Args:
        driver_id: Ergast-style driver identifier (e.g. "hamilton").

    Returns:
        Dict with races, wins, and podiums counts, or empty dict on failure.
    """
    data = _ergast_get(f"drivers/{driver_id}/results.json?limit=500")
    if not data:
        return {}
    try:
        races = data["MRData"]["RaceTable"]["Races"]
        wins = sum(1 for r in races if r["Results"][0]["position"] == "1")
        podiums = sum(1 for r in races if int(r["Results"][0]["position"]) <= 3)
        return {"races": len(races), "wins": wins, "podiums": podiums}
    except (KeyError, TypeError, IndexError, ValueError):
        return {}


# ── Public fetch functions ────────────────────────────────────────────────


def fetch_countries() -> dict[str, str]:
    """Return all countries referenced by drivers and tracks.

    Returns:
        Mapping of country name to ISO 3166-1 alpha-3 code.
    """
    return dict(COUNTRIES)


def fetch_skills() -> list[tuple[str, str]]:
    """Return the 6 skill definitions used in the card game.

    Returns:
        List of (skill_name, description) tuples.
    """
    return list(SKILLS)


def fetch_teams() -> dict[str, str]:
    """Return all F1 teams with their headquarters country.

    Returns:
        Mapping of team name to country name.
    """
    return dict(TEAMS)


def fetch_drivers() -> list[dict[str, Any]]:
    """Return enriched driver dicts for all 59 drivers.

    Tries FastF1 then the Ergast API for driver numbers, falling
    back to the hardcoded constants values.

    Returns:
        List of dicts with id, name, number, gp_wins, team,
        peak_year, and country.
    """
    fastf1_numbers = _try_fastf1_driver_numbers()
    ergast_drivers: dict[str, dict[str, Any]] = {}
    if not fastf1_numbers:
        ergast_drivers = _fetch_ergast_driver_list()

    results: list[dict[str, Any]] = []
    for driver_id, name, number, gp_wins, team, peak_year, country in DRIVERS:
        resolved_number = (
            fastf1_numbers.get(name)
            or ergast_drivers.get(name, {}).get("number")
            or number
        )
        results.append(
            {
                "id": driver_id,
                "name": name,
                "number": resolved_number,
                "gp_wins": gp_wins,
                "team": team,
                "peak_year": peak_year,
                "country": country,
            }
        )
    return results


def fetch_tracks() -> list[dict[str, Any]]:
    """Return enriched track dicts for all 36 tracks.

    Tries FastF1 for actual lap counts, falling back to
    hardcoded values from constants.

    Returns:
        List of dicts with name, country, laps, and circuit_type.
    """
    fastf1_laps = _try_fastf1_track_laps()

    results: list[dict[str, Any]] = []
    for name, country, laps, circuit_type, description in TRACKS:
        resolved_laps = laps
        for ff1_name, ff1_laps in fastf1_laps.items():
            if _fuzzy_match(name, ff1_name):
                resolved_laps = ff1_laps
                break

        results.append(
            {
                "name": name,
                "country": country,
                "laps": resolved_laps,
                "circuit_type": circuit_type,
                "description": description,
            }
        )
    return results


# ── Skill & multiplier computation ────────────────────────────────────────


def compute_all_driver_skills(
    drivers: list[dict[str, Any]] | None = None,
) -> dict[str, dict[str, int]]:
    """Compute skill ratings (0-100) for all 59 drivers.

    Top-20 drivers use curated profiles from DRIVER_SKILL_OVERRIDES.
    Remaining drivers use an algorithmic approach based on their
    serial id and GP wins with deterministic per-skill variation.

    Args:
        drivers: Pre-fetched driver list, or None to auto-fetch.

    Returns:
        Mapping of driver name to a dict of skill_name: value (0-100).
    """
    if drivers is None:
        drivers = fetch_drivers()

    skill_names = [s[0] for s in SKILLS]
    result: dict[str, dict[str, int]] = {}

    for drv in drivers:
        name = drv["name"]
        if name in DRIVER_SKILL_OVERRIDES:
            overrides = DRIVER_SKILL_OVERRIDES[name]
            result[name] = dict(zip(skill_names, overrides))
            continue

        serial = drv["id"]
        gp_wins = drv["gp_wins"]

        base = max(97 - (serial - 1) * 0.85, 48)
        wins_bonus = min(gp_wins * 0.15, 4)

        skills: dict[str, int] = {}
        for skill_name in skill_names:
            variation = _deterministic_variation(name, skill_name, spread=8)
            raw = base + wins_bonus + variation
            skills[skill_name] = int(min(100, max(0, round(raw))))
        result[name] = skills

    return result


def compute_all_track_multipliers(
    drivers: list[dict[str, Any]] | None = None,
    tracks: list[dict[str, Any]] | None = None,
) -> list[tuple[str, str, float]]:
    """Compute track affinity multipliers for every driver × track pair.

    Uses deterministic SHA-256 hashing so results are reproducible.
    Higher-ranked drivers get a slight upward bias. Each driver also
    gets a per-circuit-type affinity adjustment.

    Args:
        drivers: Pre-fetched driver list, or None to auto-fetch.
        tracks: Pre-fetched track list, or None to auto-fetch.

    Returns:
        List of (driver_name, track_name, multiplier) tuples with
        multiplier in the range [0.5, 2.0].
    """
    if drivers is None:
        drivers = fetch_drivers()
    if tracks is None:
        tracks = fetch_tracks()

    results: list[tuple[str, str, float]] = []
    for drv in drivers:
        name = drv["name"]
        serial = drv["id"]
        for trk in tracks:
            track_name = trk["name"]
            circuit_type = trk["circuit_type"]

            digest = hashlib.sha256(f"{name}|{track_name}".encode()).digest()
            v1 = digest[0] / 255.0
            v2 = digest[1] / 255.0
            base = 0.65 + ((v1 + v2) / 2) * 1.05

            type_digest = hashlib.sha256(f"{name}|{circuit_type}".encode()).digest()
            type_adj = (type_digest[0] / 255.0 - 0.5) * 0.3

            rank_bonus = max(0, (30 - serial) * 0.004)

            multiplier = round(min(2.0, max(0.5, base + type_adj + rank_bonus)), 2)
            results.append((name, track_name, multiplier))

    return results


# ── Internal utilities ────────────────────────────────────────────────────


def _deterministic_variation(
    driver_name: str, skill_name: str, spread: int = 8
) -> float:
    """Generate a deterministic pseudo-random variation from a name+skill hash.

    Args:
        driver_name: Driver's full name.
        skill_name: Name of the skill being varied.
        spread: Maximum absolute deviation.

    Returns:
        Float in the range [-spread, +spread].
    """
    digest = hashlib.sha256(f"{driver_name}:{skill_name}".encode()).digest()
    normalised = digest[0] / 255.0
    return (normalised * 2 - 1) * spread


def _fuzzy_match(a: str, b: str) -> bool:
    """Check if two strings match via case-insensitive substring containment.

    Args:
        a: First string.
        b: Second string.

    Returns:
        True if either string contains the other (case-insensitive).
    """
    a_lower, b_lower = a.lower(), b.lower()
    return a_lower in b_lower or b_lower in a_lower
