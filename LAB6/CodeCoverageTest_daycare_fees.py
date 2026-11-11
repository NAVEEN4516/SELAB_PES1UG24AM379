"""Tests exercising every executable statement in the daycare module."""
import pytest
from daycare_fees import extra_hours_fee, enrolment_allowed, pickup_status


def test_invalid_age_group():
    with pytest.raises(ValueError, match="^unknown age group$"):
        extra_hours_fee("school", 20, False)


def test_negative_hours():
    with pytest.raises(ValueError, match="^invalid hours$"):
        extra_hours_fee("infant", -1, False)


@pytest.mark.parametrize("group,hours,sibling,expected", [
    ("toddler", 30, True, 0),
    ("infant", 21, False, 14),
    ("toddler", 26, False, 9),
    ("infant", 41, False, 462),
    ("preschool", 51, False, 294),
])
def test_fee_paths(group, hours, sibling, expected):
    assert extra_hours_fee(group, hours, sibling) == expected


@pytest.mark.parametrize("age,vacancies,pending,expected", [
    (12, 0, True, True),
    (5, 1, False, False),
    (6, 1, False, True),
])
def test_enrolment_paths(age, vacancies, pending, expected):
    assert enrolment_allowed(age, vacancies, pending) is expected


@pytest.mark.parametrize("minutes,aftercare,friday,expected", [
    (30, True, True, "on_time"),
    (0, False, False, "late"),
    (-6, False, False, "overdue"),
])
def test_pickup_paths(minutes, aftercare, friday, expected):
    assert pickup_status(minutes, aftercare, friday) == expected
