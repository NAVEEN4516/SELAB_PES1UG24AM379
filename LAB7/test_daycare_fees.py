"""Fuzzing plus mathematical properties and explicit regression examples."""
import math
import runpy
from pathlib import Path

import pytest
from hypothesis import given, settings, strategies as st
from daycare_fees import parse_enrolment, hours_average, payable_fee

settings.register_profile("lab7", max_examples=500, derandomize=True, deadline=None)
settings.load_profile("lab7")


@given(st.text() | st.none())
def test_parse_enrolment_no_crash(s):
    result = parse_enrolment(s)
    if result is not None:
        group, hours = result
        assert group and group == group.strip().title()
        assert math.isfinite(hours) and hours >= 0


@given(st.text() | st.none())
def test_hours_average_no_crash(s):
    result = hours_average(s)
    assert result is None or (isinstance(result, int) and result >= 0)


@given(st.text() | st.none())
def test_payable_fee_no_crash(s):
    result = payable_fee(s)
    assert result is None or (math.isfinite(result) and result >= 0)


@given(st.sampled_from(["infant", "toddler", "preschool"]),
       st.integers(min_value=0, max_value=10000))
def test_valid_enrolment(group, hours):
    assert parse_enrolment(f"  {group.upper()}  : {hours} ") == (group.title(), float(hours))


@given(st.lists(st.integers(min_value=0, max_value=10000), min_size=1, max_size=100))
def test_average_matches_floor_of_arithmetic_mean(values):
    result = hours_average(",".join(map(str, values)))
    assert result == sum(values) // len(values)
    assert min(values) <= result <= max(values)


@given(st.integers(min_value=0, max_value=1000000),
       st.integers(min_value=0, max_value=1000000))
def test_valid_payable_fee(fee, discount):
    assert payable_fee(f"{fee}|{discount}") == pytest.approx(max(fee * 1.18 - discount, 0))


@pytest.mark.parametrize("s", [None, "", "toddler", "a:1:2", ":2", " :2",
    "infant:", "infant:x", "infant:-1", "infant:nan", "infant:inf", "infant:1e309"])
def test_enrolment_regressions(s):
    assert parse_enrolment(s) is None


@pytest.mark.parametrize("s", [None, "", ",", "1,", ",1", "1,,2", "x", "2.5", "-1,2", "9" * 5000])
def test_average_regressions(s):
    assert hours_average(s) is None


@pytest.mark.parametrize("s", [None, "", "3000", "1|2|3", "|2", "2|", "x|2",
    "2|x", "-1|0", "1|-1", "nan|0", "0|nan", "inf|0", "0|inf", "1.79e308|0"])
def test_fee_regressions(s):
    assert payable_fee(s) is None


@pytest.mark.parametrize("s,expected", [("toddler:25", ("Toddler",25.0)),
    ("infant:0", ("Infant",0.0)), ("preschool:2.5", ("Preschool",2.5))])
def test_enrolment_examples(s, expected):
    assert parse_enrolment(s) == expected


@pytest.mark.parametrize("s,expected", [("20,25,30",25), ("1,2",1), ("0",0), (" 2 , 4 ",3)])
def test_average_examples(s, expected):
    assert hours_average(s) == expected


@pytest.mark.parametrize("s,expected", [("3000|250",3290.0), ("0|0",0.0), ("10|100",0.0)])
def test_fee_examples(s, expected):
    assert payable_fee(s) == pytest.approx(expected)


@pytest.mark.parametrize("responses", [("toddler:25","20,25,30","3000|250"),
                                      ("bad","","bad")])
def test_cli(monkeypatch, capsys, responses):
    answers = iter(responses)
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    runpy.run_path(str(Path(__file__).with_name("daycare_fees.py")), run_name="__main__")
    output = capsys.readouterr().out
    assert "Age Group and Hours:" in output
    assert "Average Hours:" in output
    assert "Payable Fee:" in output
