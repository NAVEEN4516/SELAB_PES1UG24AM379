# Lab 5 — Reflection

**Student:** Naveen Prasad M — PES1UG24AM379
**File analysed:** `supplier_orders.py`

> The lab handout asks for answers to the reflection questions but does not
> print them. The four standard questions for this lab are restated below.

## 1. What is the purpose and scope of static code analysis, and what did it find here that reading the code might not?

Static analysis reads source code without executing it. That gives it complete
coverage of every branch — including the ones no test ever reaches — but it
confines it strictly to the *form* of the code. It can tell you the code is
built wrong; it cannot tell you the code is solving the wrong problem.

Both halves were visible in this file.

The strength: the demo runs clean and prints `1 540`, exactly what you would
expect. Nothing about running it suggests a problem. But line 11 builds a SQL
statement by `%`-formatting a supplier name into a string. With the demo's
inputs — `"Acme Steel"`, `"Bolt Co"` — it behaves perfectly. A supplier
recorded as `O'Brien Supplies` would break the query outright, and one recorded
deliberately would own the database. Testing with realistic data would never
surface this. Bandit found it immediately, because it was looking at how the
string was *constructed*, not at what the string happened to contain today.

The `except Exception: pass` in `cleanup` is the same story from the other
direction. It is three lines that look like defensive programming and are
actually the opposite — they guarantee that any failure is invisible. The
program would report success while quietly doing nothing.

The limit: nothing in the program ever calls `commit()`. On a file-backed
database every order placed would be discarded when the connection closed. The
demo only survives because `:memory:` lets the process read back its own
uncommitted writes. Not one of the three tools mentioned it, and they were
right not to — there is no rule that says "a program using sqlite3 must
commit." Only someone who knows how transactions work catches that.

So the scope is narrow but genuinely deep inside its boundary.

## 2. Which tool was most useful, and how do the three differ?

They answer three different questions, and the sharpest way to see the
difference is to look at what each one missed.

- **Bandit** found the highest-stakes issues. The SQL injection and the shell
  injection are the two defects in this file that could cause actual damage,
  and Bandit found both. Neither Pylint nor Flake8 said anything about either
  one. Bandit also correctly ranked them — shell injection High, SQL injection
  Medium — which matters when a report has twenty entries and you need to know
  which three to fix first.
- **Pylint** found the issue I think is most interesting: the `global
  order_total` counter. Bandit does not care about globals and Flake8 does not
  either, but this one is a real bug. The counter duplicates information the
  database already holds, and `cleanup()` deletes rows without adjusting it, so
  after a cleanup the printed total is simply wrong. Pylint flagged it as a
  style smell (`W0603`); following that flag honestly led to a correctness fix.
  It also caught that `markReceived` accepted a `remarks` argument and silently
  threw it away — every caller believes it is recording delivery notes, and
  nothing is stored.
- **Flake8** was the shallowest and the fastest. Four findings, all cosmetic.
  Its value is not in what it finds but in what it removes from code review:
  nobody should spend review time on line length.

Most useful overall was Bandit, because security defects are the ones you
cannot fix cheaply later. But Pylint found more *bugs*, which surprised me — I
had expected it to only have opinions about naming.

## 3. How does static analysis contribute to code quality and maintainability?

**It changes when defects are found, and that changes what they cost.** Fixing
the SQL injection took one parameterised query. Finding the same flaw after a
stores department has been running it for a year means an incident, an audit,
and a supplier database of unknown integrity. Static analysis sits at the
earliest point in the lifecycle where any tool can look at all.

**It makes human review worth doing.** Once the tool has settled naming,
spacing and line length, a reviewer's attention goes to whether orders should
really be deleted on cleanup rather than archived. That is the part of the
review a machine cannot do, and it is exactly the part that gets squeezed out
when half the comments are about whitespace.

**It transfers expertise.** I did not know that `%`-formatting a SQL string was
the classic injection vector, or that `except Exception: pass` has its own
Bandit rule because of how often it hides real failures. Each check exists
because someone was burned and wrote it down. Running the tools is a cheap way
to inherit that.

The caveat matters though. This file now scores 10.00/10 from Pylint, reports
no Bandit issues and no Flake8 findings — and it still never commits a
transaction. A clean report means "none of the known defect categories are
present," not "this code is correct." Treating a perfect score as proof of
correctness is the main way static analysis gets misused.

## 4. Would you use these tools in your own workflow, and how?

Yes, but configured deliberately. Badly-tuned static analysis produces noise,
noise gets ignored, and an ignored tool is worse than no tool because it
creates false confidence.

What I would actually do:

- **Flake8 in the editor, on save.** Formatting issues should be fixed before a
  commit exists, not argued about in review.
- **Bandit in CI, blocking the merge on High and Medium.** These are the
  findings that are expensive to fix later, and there are few enough of them
  that blocking is reasonable.
- **Pylint in CI, gated on a score threshold rather than zero messages.** The
  long tail of Pylint conventions is not worth failing a build over, but a
  score dropping below the threshold is a signal worth acting on.
- **Fix the baseline before turning the gate on.** Running Pylint on an
  existing codebase for the first time produces hundreds of messages, and the
  natural human response is to ignore every one. Clearing them up front is what
  makes a *new* message mean something.
- **Suppress narrowly and in writing.** If a finding genuinely cannot be fixed,
  suppress that specific rule on that specific line with a comment explaining
  why. A blanket disable turns the tool off silently, and that failure mode is
  invisible precisely because the build stays green.

The principle I would take from this lab: let the tools own everything
mechanical, so human attention goes entirely to whether the program does the
right thing. On this file the tools caught eleven issues correctly and had
nothing to say about the missing `commit()`. Both of those facts are the
lesson.
