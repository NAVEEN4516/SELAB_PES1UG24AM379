# Lab 5 — Static Code Analysis: Identified Issues

**Student:** Naveen Prasad M — PES1UG24AM379
**Assigned repo:** [SETAPESU26/L5_18_supplier_orders](https://github.com/SETAPESU26/L5_18_supplier_orders)
**File analysed:** `supplier_orders.py`

## Baseline (before any fixes)

| Tool | Result |
|------|--------|
| Pylint | **2.41/10** — 22 messages |
| Bandit | **3 findings** — 1 High, 1 Medium, 1 Low |
| Flake8 | **4 findings** — 3 × E501, 1 × E225 |

Full reports: [`before/pylint_report.txt`](before/pylint_report.txt),
[`before/bandit_report.txt`](before/bandit_report.txt),
[`before/flake8_report.txt`](before/flake8_report.txt)

## Issue table

Ordered by severity: security findings first, then correctness, then style.
Line numbers refer to the original file as handed out.

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| Shell command built from input (`B605`) | Security — **High** | 21 | `os.system("echo notifying warehouse about " + supplier)` concatenates a supplier name into a string and hands it to a shell. A supplier recorded as `Acme; rm -rf ~` would run as a second command (CWE-78). | The shell was only ever being used to echo a line, so the whole subprocess is unnecessary. Replaced with `print()`. This removes the vulnerability at the root rather than hardening around it, and lets the `os` import be dropped entirely. |
| SQL injection (`B608`) | Security — **Medium** | 11 | The INSERT is assembled with `%`-formatting: `"... VALUES ('%s', '%s', %d, 0)" % (supplier, item, quantity)`. A supplier name containing a quote breaks out of the string literal, so `', '', 0); DROP TABLE orders; --` is executable SQL (CWE-89). | Replaced with a parameterised query using `?` placeholders, passing values as a tuple. SQLite binds them as *data*, so no value can ever be parsed as SQL. |
| Silently swallowed exceptions (`B110`) | Security / Correctness — Low | 27–28 | `except Exception: pass` in `cleanup` discards every failure without a trace. A locked database, a schema mismatch or a disk error would all look exactly like success, so fulfilled orders would quietly pile up with nobody aware (CWE-703). | Narrowed to `except sqlite3.Error` and the error is now printed. Any non-database exception propagates instead of vanishing. |
| Mutable global counter (`W0603`) | Bug | 6, 10, 12 | `order_total` was a module-level counter mutated through `global`. It duplicates information the database already holds, and the two can silently diverge — `cleanup()` deletes rows without ever adjusting the counter, so after a cleanup the printed total is simply wrong. | Deleted the global. `total_quantity()` now derives the total with `SELECT SUM(quantity)`, making the database the single source of truth. A value that is computed cannot drift from one that is stored. |
| Shadowed connection parameter (`W0621`) | Bug risk | 9, 16, 24, 31 | Every function took a parameter named `conn`, shadowing the module-level `conn`. If a call site ever omitted the argument the function would silently fall back to the global instead of failing, which is a hard bug to see. | The connection is created inside `main()` by `create_connection()` and passed explicitly as `connection`. There is no module-level connection left to shadow. |
| Dropped argument (`W0613`) | Bug | 16 | `markReceived(conn, order_id, remarks)` accepted `remarks` and never used it. Every call site believes it is recording delivery notes; nothing is stored. | Added a `remarks` column to the table and the UPDATE now writes it. The parameter does what its name promises. |
| `%`-formatting over f-string (`C0209`) | Quality | 11 | Pylint flagged the `%` formatting as outdated style. | Resolved by the parameterised query — the string is no longer formatted at all, which is both the secure and the idiomatic answer. |
| Non-PEP 8 naming (`C0103`) | Style | 6, 9, 16, 20, 31 | Functions used camelCase (`placeOrder`, `markReceived`, `notifyWarehouse`, `pendingCount`) and `order_total` was a lowercase module-level constant. | All functions renamed to snake_case. The `order_total` complaint disappeared along with the global itself. |
| Missing docstrings (`C0114`, `C0116`) | Maintainability | 1 and every function | No module docstring and no function docstrings — nothing stated what `received` means or what the return values are. | Added a module docstring and one for all seven functions. |
| Line too long (`C0301`, `E501`) | Style | 5, 11, 32 | The CREATE TABLE line ran to 122 characters and the INSERT to 131 — over Pylint's 100 limit and well over PEP 8's 79. The COUNT query was 87. | All three wrapped across multiple lines using implicit string concatenation. |
| Missing whitespace around operator (`E225`) | Style | 12 | `order_total+=quantity` with no spaces. | Fixed implicitly — the line was deleted when the global counter was removed. |

## Result (after fixes)

| Tool | Before | After |
|------|--------|-------|
| Pylint | 2.41/10 | **10.00/10** |
| Bandit | 1 High, 1 Medium, 1 Low | **No issues identified** |
| Flake8 | 4 findings | **0 findings** |

Full reports: [`after/pylint_report.txt`](after/pylint_report.txt),
[`after/bandit_report.txt`](after/bandit_report.txt),
[`after/flake8_report.txt`](after/flake8_report.txt)

No `# nosec` suppressions were needed — every Bandit finding was fixed at
the source.

The program's behaviour is unchanged. `python supplier_orders.py` prints
exactly the same two lines before and after:

```
notifying warehouse about Acme
1 540
```

## One thing the tools did not catch

Nothing is ever committed. `sqlite3` opens a transaction implicitly, and
`conn.commit()` is never called, so on a file-backed database every order
placed would be rolled back when the connection closed. The demo survives this
only because the database is `:memory:` and the process reads its own
uncommitted data before exiting.

No tool said a word about it. The syntax is valid, the style is clean and
nothing is insecure — the code is simply missing a step that the problem domain
requires. This is the boundary of static analysis: it checks the *form* of the
code, not whether the code accomplishes what it set out to do. The behaviour
has been left as-is, since changing it would go beyond the lab's brief.
