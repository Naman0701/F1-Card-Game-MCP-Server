"""Unit tests for src/services/fetch_service.py — pure functions only.

These tests do NOT call external APIs; they test the computation logic
(skills, multipliers, helpers) and the data assembly from constants.
"""

from src.services.fetch_service import (
    _deterministic_variation,
    _fuzzy_match,
    compute_all_driver_skills,
    compute_all_track_multipliers,
    fetch_countries,
    fetch_drivers,
    fetch_skills,
    fetch_teams,
    fetch_tracks,
)


class TestDeterministicVariation:
    def test_returns_float(self):
        result = _deterministic_variation("Lewis Hamilton", "pace")
        assert isinstance(result, float)

    def test_within_spread(self):
        for spread in [4, 8, 16]:
            result = _deterministic_variation("Test Driver", "awareness", spread=spread)
            assert -spread <= result <= spread

    def test_deterministic(self):
        a = _deterministic_variation("Max Verstappen", "racecraft")
        b = _deterministic_variation("Max Verstappen", "racecraft")
        assert a == b

    def test_different_inputs_differ(self):
        a = _deterministic_variation("Driver A", "pace")
        b = _deterministic_variation("Driver B", "pace")
        assert a != b

    def test_different_skills_differ(self):
        a = _deterministic_variation("Same Driver", "pace")
        b = _deterministic_variation("Same Driver", "awareness")
        assert a != b


class TestFuzzyMatch:
    def test_exact_match(self):
        assert _fuzzy_match("Silverstone", "Silverstone")

    def test_substring_match(self):
        assert _fuzzy_match("Silverstone", "Silverstone Circuit")

    def test_reverse_substring(self):
        assert _fuzzy_match("Silverstone Circuit", "Silverstone")

    def test_case_insensitive(self):
        assert _fuzzy_match("MONZA", "monza")

    def test_no_match(self):
        assert not _fuzzy_match("Monaco", "Silverstone")


class TestFetchCountries:
    def test_returns_dict(self):
        result = fetch_countries()
        assert isinstance(result, dict)

    def test_has_expected_countries(self):
        result = fetch_countries()
        assert "United Kingdom" in result
        assert result["United Kingdom"] == "GBR"
        assert "Italy" in result


class TestFetchSkills:
    def test_returns_six_skills(self):
        assert len(fetch_skills()) == 6

    def test_skill_tuples(self):
        for name, desc in fetch_skills():
            assert isinstance(name, str)
            assert isinstance(desc, str)


class TestFetchTeams:
    def test_returns_dict(self):
        result = fetch_teams()
        assert isinstance(result, dict)
        assert len(result) > 0

    def test_known_teams(self):
        result = fetch_teams()
        assert "Ferrari" in result
        assert result["Ferrari"] == "Italy"


class TestFetchDrivers:
    def test_returns_59_drivers(self):
        result = fetch_drivers()
        assert len(result) == 59

    def test_driver_dict_keys(self):
        expected_keys = {
            "id",
            "name",
            "number",
            "gp_wins",
            "team",
            "peak_year",
            "country",
        }
        for d in fetch_drivers():
            assert set(d.keys()) == expected_keys

    def test_hamilton_data(self):
        drivers = fetch_drivers()
        hamilton = next(d for d in drivers if d["name"] == "Lewis Hamilton")
        assert hamilton["id"] == 1
        assert hamilton["gp_wins"] == 105
        assert hamilton["team"] == "Ferrari"
        assert hamilton["country"] == "United Kingdom"

    def test_ids_sequential(self):
        ids = [d["id"] for d in fetch_drivers()]
        assert ids == list(range(1, 60))


class TestFetchTracks:
    def test_returns_36_tracks(self):
        result = fetch_tracks()
        assert len(result) == 36

    def test_track_dict_keys(self):
        expected_keys = {"name", "country", "laps", "circuit_type", "description"}
        for t in fetch_tracks():
            assert set(t.keys()) == expected_keys

    def test_track_has_description(self):
        for t in fetch_tracks():
            assert t["description"] is not None
            assert len(t["description"]) > 10


class TestComputeAllDriverSkills:
    def test_returns_59_entries(self):
        result = compute_all_driver_skills()
        assert len(result) == 59

    def test_six_skills_per_driver(self):
        for name, skills in compute_all_driver_skills().items():
            assert len(skills) == 6, f"{name} has {len(skills)} skills"

    def test_values_in_range(self):
        for name, skills in compute_all_driver_skills().items():
            for skill_name, value in skills.items():
                assert 0 <= value <= 100, f"{name}.{skill_name} = {value}"

    def test_top_drivers_use_overrides(self):
        result = compute_all_driver_skills()
        assert result["Lewis Hamilton"]["pace"] == 96
        assert result["Max Verstappen"]["pace"] == 98
        assert result["Ayrton Senna"]["wet_weather"] == 99

    def test_deterministic(self):
        a = compute_all_driver_skills()
        b = compute_all_driver_skills()
        assert a == b

    def test_top_drivers_generally_higher(self):
        result = compute_all_driver_skills()
        hamilton_avg = sum(result["Lewis Hamilton"].values()) / 6
        last_driver_avg = sum(result["Arvid Lindblad"].values()) / 6
        assert hamilton_avg > last_driver_avg


class TestComputeAllTrackMultipliers:
    def test_total_count(self):
        result = compute_all_track_multipliers()
        assert len(result) == 59 * 36

    def test_tuple_structure(self):
        for driver_name, track_name, mult in compute_all_track_multipliers():
            assert isinstance(driver_name, str)
            assert isinstance(track_name, str)
            assert isinstance(mult, float)

    def test_multiplier_range(self):
        for _, _, mult in compute_all_track_multipliers():
            assert 0.5 <= mult <= 2.0

    def test_deterministic(self):
        a = compute_all_track_multipliers()
        b = compute_all_track_multipliers()
        assert a == b
