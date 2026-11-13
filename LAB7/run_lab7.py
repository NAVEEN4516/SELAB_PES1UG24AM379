"""Reproduce baseline crashes and passing fuzz/coverage reports."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / "reports"


def run(args, cwd, destination):
    result = subprocess.run([sys.executable, *args], cwd=cwd,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, encoding="utf-8", errors="replace")
    destination.write_text(result.stdout, encoding="utf-8")
    print(result.stdout)
    return result.returncode


def main():
    REPORTS.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="lab7_baseline_") as directory:
        baseline = Path(directory)
        shutil.copyfile(ROOT / "before/original_daycare_fees.py", baseline / "daycare_fees.py")
        shutil.copyfile(ROOT / "test_daycare_fees.py", baseline / "test_daycare_fees.py")
        status = run(["-m", "pytest", "-q", "test_daycare_fees.py", "-k", "no_crash",
                      "--tb=short"], baseline, REPORTS / "before_fuzz.txt")
        if status != 1:
            raise SystemExit("Expected test failures (exit 1) in the original application")
    status = run(["-m", "coverage", "run", "--branch", "--source=daycare_fees",
                  "-m", "pytest", "-q", "test_daycare_fees.py",
                  "--hypothesis-show-statistics"], ROOT, REPORTS / "after_fuzz.txt")
    if status:
        raise SystemExit(status)
    status = run(["-m", "coverage", "report", "-m"], ROOT, REPORTS / "coverage.txt")
    if status:
        raise SystemExit(status)
    subprocess.run([sys.executable, "-m", "coverage", "json", "-o",
                    str(REPORTS / "coverage.json")], cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
