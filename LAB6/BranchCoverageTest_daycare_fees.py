"""Branch and boundary tests for all three daycare functions."""
import pytest
from daycare_fees import extra_hours_fee, enrolment_allowed, pickup_status


@pytest.mark.parametrize("group,hours,sibling,message", [
    ("unknown", 20, False, "unknown age group"),
    ("infant", -1, False, "invalid hours"),
    ("toddler", -0.5, True, "invalid hours"),
])
def test_invalid_inputs(group, hours, sibling, message):
    with pytest.raises(ValueError, match=f"^{message}$"):
        extra_hours_fee(group, hours, sibling)


@pytest.mark.parametrize("group,hours,sibling,expected", [
    ("infant", 0, False, 0),
    ("infant", 20, False, 0),
    ("infant", 21, False, 14),
    ("infant", 21, True, 14),  # Infants receive no sibling hours.
    ("infant", 40, False, 280),  # Exactly 20 extra hours: base rate.
    ("infant", 41, False, 462),  # 21 extra hours: 14 + 5 + 3.
    ("toddler", 25, False, 0),
    ("toddler", 26, False, 9),
    ("toddler", 30, True, 0),
    ("toddler", 31, True, 9),
    ("toddler", 45, False, 180),
    ("toddler", 46, False, 294),
    ("preschool", 30, False, 0),
    ("preschool", 31, False, 9),
    ("preschool", 35, True, 0),
    ("preschool", 36, True, 9),
    ("preschool", 55, True, 180),
    ("preschool", 56, True, 294),
    ("toddler", 25.5, False, 4.5),
])
def test_fee_boundaries(group, hours, sibling, expected):
    assert extra_hours_fee(group, hours, sibling) == expected


@pytest.mark.parametrize("age,vacancies,pending,expected", [
    (11, 1, True, False),
    (12, 0, True, True),  # Current implementation ignores vacancies here.
    (13, 1, True, True),
    (5, 1, False, False),
    (6, 0, False, False),
    (6, 1, False, True),
    (24, 2, False, True),
])
def test_enrolment_boundaries(age, vacancies, pending, expected):
    assert enrolment_allowed(age, vacancies, pending) is expected


@pytest.mark.parametrize("aftercare,friday,cutoff", [
    (False, False, 10), (False, True, 20),
    (True, False, 20), (True, True, 30),
])
@pytest.mark.parametrize("offset,expected", [
    (1, "on_time"), (0, "on_time"), (-1, "late"),
    (-15, "late"), (-16, "overdue"),
])
def test_pickup_boundaries(aftercare, friday, cutoff, offset, expected):
    assert pickup_status(cutoff + offset, aftercare, friday) == expected
