"""Daycare input helpers. Invalid inputs return None without raising."""
import math


def parse_enrolment(text):
    """Parse group:hours; hours must be finite and nonnegative."""
    if not isinstance(text, str):
        return None
    try:
        age_group, hours_text = text.split(":")
        hours = float(hours_text)
    except ValueError:
        return None
    age_group = age_group.strip().title()
    if not age_group or not math.isfinite(hours) or hours < 0:
        return None
    return age_group, hours


def hours_average(hours_csv):
    """Return the original integer floor average of nonnegative hours."""
    if not isinstance(hours_csv, str):
        return None
    try:
        values = [int(value) for value in hours_csv.split(",")]
    except ValueError:
        return None
    if any(value < 0 for value in values):
        return None
    return sum(values) // len(values)


def payable_fee(text):
    """Apply 18% tax and discount; invalid or overflowing fees return None."""
    if not isinstance(text, str):
        return None
    try:
        fee_text, discount_text = text.split("|")
        fee, discount = float(fee_text), float(discount_text)
    except ValueError:
        return None
    if not math.isfinite(fee) or not math.isfinite(discount):
        return None
    if fee < 0 or discount < 0:
        return None
    total = fee * 1.18 - discount
    if not math.isfinite(total):
        return None
    return max(total, 0)


def main():
    print("==== Running parse_enrolment ====")
    user_input = input("Enter age group:hours (e.g. toddler:25): ")
    result = parse_enrolment(user_input)
    print("Age Group and Hours:", result)

    print("\n==== Running hours_average ====")
    user_input = input("Enter weekly hours as CSV (e.g. 20,25,30): ")
    result = hours_average(user_input)
    print("Average Hours:", result)

    print("\n==== Running payable_fee ====")
    user_input = input("Enter fee|discount (e.g. 3000|250): ")
    result = payable_fee(user_input)
    print("Payable Fee:", result)

if __name__ == "__main__":
    main()
