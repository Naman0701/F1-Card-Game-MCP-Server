"""Unit tests for src/data/constants.py — validate reference data integrity."""

from src.data.constants import (
    CARDS_PER_PLAYER,
    NAME_PATTERN,
    POINTS_GAME_LOSS_PENALTY,
    POINTS_GAME_WIN_BONUS,
    POINTS_PER_ROUND_DRAW,
    POINTS_PER_ROUND_WIN,
    ROUNDS_PER_GAME,
    TRACK_MULTIPLIER_MAX,
    TRACK_MULTIPLIER_MIN,
)
from src.data.seed_data import (
    COUNTRIES,
    DRIVER_SKILL_OVERRIDES,
    DRIVERS,
    SKILLS,
    TEAMS,
    TRACKS,
)


class TestDriverConstants:
    def test_driver_count(self):
        assert len(DRIVERS) == 59

    def test_driver_tuple_structure(self):
        for drv in DRIVERS:
            assert len(drv) == 7, f"Driver tuple has wrong length: {drv}"
            _id, name, number, gp_wins, team, peak_year, country = drv
            assert isinstance(_id, int)
            assert isinstance(name, str) and len(name) > 0
            assert isinstance(number, int)
            assert isinstance(gp_wins, int) and gp_wins >= 0
            assert isinstance(team, str)
            assert isinstance(peak_year, int)
            assert isinstance(country, str)

    def test_driver_ids_are_sequential(self):
        ids = [d[0] for d in DRIVERS]
        assert ids == list(range(1, 60))

    def test_driver_ids_unique(self):
        ids = [d[0] for d in DRIVERS]
        assert len(ids) == len(set(ids))

    def test_all_driver_teams_exist(self):
        for drv in DRIVERS:
            assert (
                drv[4] in TEAMS
            ), f"Team '{drv[4]}' for driver '{drv[1]}' not in TEAMS"

    def test_all_driver_countries_exist(self):
        for drv in DRIVERS:
            assert (
                drv[6] in COUNTRIES
            ), f"Country '{drv[6]}' for driver '{drv[1]}' not in COUNTRIES"


class TestTrackConstants:
    def test_track_count(self):
        assert len(TRACKS) == 36

    def test_track_tuple_structure(self):
        valid_types = {"street", "high_speed", "technical", "power", "mixed"}
        for trk in TRACKS:
            assert len(trk) == 5, f"Track tuple has wrong length: {trk}"
            name, country, laps, circuit_type, description = trk
            assert isinstance(name, str) and len(name) > 0
            assert isinstance(country, str)
            assert isinstance(laps, int) and laps > 0
            assert (
                circuit_type in valid_types
            ), f"Invalid circuit_type '{circuit_type}' for '{name}'"
            assert isinstance(description, str) and len(description) > 10

    def test_all_track_countries_exist(self):
        for trk in TRACKS:
            assert (
                trk[1] in COUNTRIES
            ), f"Country '{trk[1]}' for track '{trk[0]}' not in COUNTRIES"

    def test_track_names_unique(self):
        names = [t[0] for t in TRACKS]
        assert len(names) == len(set(names))


class TestSkillConstants:
    def test_skill_count(self):
        assert len(SKILLS) == 6

    def test_skill_names(self):
        expected = {
            "pace",
            "racecraft",
            "awareness",
            "experience",
            "wet_weather",
            "tire_management",
        }
        actual = {s[0] for s in SKILLS}
        assert actual == expected

    def test_skill_overrides_have_six_values(self):
        for name, values in DRIVER_SKILL_OVERRIDES.items():
            assert (
                len(values) == 6
            ), f"Override for '{name}' has {len(values)} values, expected 6"
            for v in values:
                assert 0 <= v <= 100, f"Skill value {v} for '{name}' out of range"

    def test_skill_overrides_match_known_drivers(self):
        driver_names = {d[1] for d in DRIVERS}
        for name in DRIVER_SKILL_OVERRIDES:
            assert (
                name in driver_names
            ), f"Override for '{name}' doesn't match any driver"


class TestTeamConstants:
    def test_all_team_countries_exist(self):
        for team_name, country_name in TEAMS.items():
            assert (
                country_name in COUNTRIES
            ), f"Country '{country_name}' for team '{team_name}' not in COUNTRIES"


class TestGameConstants:
    def test_cards_per_player(self):
        assert CARDS_PER_PLAYER == 5

    def test_rounds_per_game(self):
        assert ROUNDS_PER_GAME == 5

    def test_cards_equals_rounds(self):
        assert CARDS_PER_PLAYER == ROUNDS_PER_GAME

    def test_round_points(self):
        assert POINTS_PER_ROUND_WIN == 2
        assert POINTS_PER_ROUND_DRAW == 1

    def test_game_bonus_penalty(self):
        assert POINTS_GAME_WIN_BONUS == 5
        assert POINTS_GAME_LOSS_PENALTY == 5

    def test_multiplier_range(self):
        assert TRACK_MULTIPLIER_MIN == 0.5
        assert TRACK_MULTIPLIER_MAX == 2.0


class TestNamePattern:
    def test_valid_names(self):
        for name in ["ab", "Player1", "test_user", "A" * 20, "abc_123"]:
            assert NAME_PATTERN.match(name), f"'{name}' should be valid"

    def test_invalid_names(self):
        for name in [
            "a",
            "",
            "A" * 21,
            "has space",
            "special!",
            "dash-name",
            "dot.name",
        ]:
            assert not NAME_PATTERN.match(name), f"'{name}' should be invalid"
