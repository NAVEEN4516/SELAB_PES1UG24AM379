# Lab 6 - Code and Branch Coverage

Student: NAVEEN4516 (PES1UG24AM379)

Source: https://github.com/SETAPESU26/L6_L7_48_daycare_fees/tree/main/Lab%206
Fork: https://github.com/NAVEEN4516/L6_L7_48_daycare_fees

The original application and starter tests are retained unchanged.

## Reproduce code coverage

Run from this directory:

```powershell
python -m pip install -r requirements.txt
python -m coverage run --source=daycare_fees -m pytest -q CodeCoverageTest_daycare_fees.py
python -m coverage report -m
```

The 13 code coverage cases execute all 37 statements: **100% line coverage**.
The starter suite has 2 passing tests and 38% line coverage (23 missing statements).
Tests include invalid age groups and hours, included-hour limits, sibling allowances,
normal and premium rates, enrolment outcomes and all pickup statuses.

![Code coverage output](reports/code_coverage.png)

The image is a rendering of the actual captured terminal transcript in
`reports/code_coverage.txt`, rather than a desktop screenshot. The JSON report
provides machine-readable coverage evidence.
