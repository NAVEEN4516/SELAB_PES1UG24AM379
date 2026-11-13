# Lab 7 - Fuzz Testing: Daycare Fees

Student: NAVEEN4516 / PES1UG24AM379

Assignment source: https://github.com/SETAPESU26/L6_L7_48_daycare_fees/tree/main/Lab%207

## Objective and scope

Complete the three Hypothesis starter tests, discover failing inputs, fix the
causes and verify valid behavior with regression and property tests. The repository
specifies fuzz testing but includes no detailed handout; this submission follows
those repository instructions.

## Run

Use Python 3.12 and run from this directory:

```powershell
python -m pip install -r requirements.txt
python -m pytest -q test_daycare_fees.py --hypothesis-show-statistics
python -m coverage run --branch --source=daycare_fees -m pytest -q test_daycare_fees.py
python -m coverage report -m
```

To regenerate both before/after transcripts and JSON coverage:

```powershell
python run_lab7.py
```

The runner copies the original application and completed tests into a temporary
directory for the expected failing baseline. It does not overwrite the fixed app.

## Discovered failures

The uncompleted starter test file cannot be collected because its function bodies
are empty. It is preserved as `before/starter_test_daycare_fees.txt`. After filling
those tests, all three no-crash properties fail against the original application.
The exact traceback and Hypothesis-shrunk examples are in `reports/before_fuzz.txt`.

| Function | Examples Hypothesis found | Cause | Fix |
|---|---|---|---|
| `parse_enrolment` | `None`, `''`, `':'` | Calling split on None; missing fields; invalid float | Type guard, exact split, numeric validation |
| `hours_average` | `None`, `''` | Calling split on None; empty integer token | Type guard and integer conversion validation |
| `payable_fee` | `None`, `''`, `'|'` | Calling split on None; missing fields; invalid float | Type guard, exact split, numeric validation |

Explicit regression cases additionally address repeated delimiters, whitespace,
negative hours/amounts, NaN, infinity, floating-point overflow, an oversized integer
string and discounts exceeding the taxed fee. These explicit cases are distinct
from the automatically discovered examples above.

## Input contract and fixes

- Invalid input returns `None`; no blanket exception handling hides programming errors.
- Enrolment accepts a nonempty group name and finite, nonnegative numeric hours.
  Group names retain the original strip/title normalization; no new age-group list
  is imposed.
- Average accepts a nonempty CSV of nonnegative integers and preserves `sum // count`.
  A fractional token is rejected; a fractional mean is floored as in the original.
- Fees and discounts must be finite and nonnegative. The original 18% tax and
  zero minimum remain. An overflowing calculation returns `None`.
- The command-line entry point still prompts for all three inputs and displays
  the results, including `None` for malformed values.

Returning `None` and rejecting negative/non-finite values are documented robustness
choices because the repository provides no further invalid-input specification.

## Results

- Before fixes: **3 failing no-crash properties** (52 other tests deselected).
- After fixes: **55 passing pytest cases**.
- Six Hypothesis properties each generate 500 passing cases: **3,000 generated
  examples**, plus the explicit regression/example/CLI cases.
- Application coverage: **54/54 statements and 18/18 branches**, no partial branches:
  **100% line and branch coverage**.
- Deterministic Hypothesis generation and pinned dependencies support reproduction.

Hypothesis's `invalid` statistic means rejected generation attempts, not malformed
application inputs or test failures. Fuzzing is finite: passing these examples
improves confidence but does not prove safety for every possible string or
resource-exhaustion input.

## Files

- `test_daycare_fees.py`: completed fuzz tests, valid-data mathematical properties,
  regression cases and CLI checks.
- `daycare_fees.py`: corrected application.
- `before/`: original application and original starter test text.
- `reports/before_fuzz.txt`: real original failing run.
- `reports/after_fuzz.txt`: passing run with Hypothesis statistics.
- `reports/coverage.txt` and `reports/coverage.json`: coverage evidence.
- `run_lab7.py`: repeatable evidence generation.
- `requirements.txt`: exact tested dependency versions.

The reports are actual captured terminal output. They are text files, not
screenshots or reconstructed terminal images.

## Commit sequence

1. Complete fuzz tests and record the original failures.
2. Fix input handling and add passing evidence, analysis and reproduction commands.
