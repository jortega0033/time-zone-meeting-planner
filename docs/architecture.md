# Implementer map

Status: **planned, not implemented.** This page maps the boundaries that [PROJECT-PLAN.md](PROJECT-PLAN.md) requires onto a module layout so that parallel tickets do not collide. It adds no requirement; the plan wins where they differ. The names are the orchestrator's proposal, fixed by the scaffold; a ticket that changes one corrects this page in the same pull request.

## Planned module map

| Boundary | Module | Owns | Parent ticket |
|---|---|---|---|
| Time data and conversion | `meeting_planner/zones.py` | Staged TZif registry, data version, local-to-UTC resolution, fold and gap results | #2 |
| Scenario contract | `meeting_planner/schema.py` | Schema version, field validation, error codes with field paths | #2 |
| Calendars | `meeting_planner/calendars.py` | Weekly windows, busy intervals, normalisation, half-open overlap | #3 |
| Options | `meeting_planner/options.py` | Recurrence expansion, feasible occurrence vectors, burden, dated rejection examples | #3 |
| Allocation | `meeting_planner/solver.py` | Bounded deterministic search, score, statuses, conflict evidence | #4 |
| Storage | `meeting_planner/storage.py` | App-owned data folder, atomic replacement, import and export | #6 |
| HTTP | `meeting_planner/server.py` | Loopback bind, request guards, routes, static assets | #2 (validation), #5, #6 |
| Browser assets | `meeting_planner/static/` | Scenario selection, editor, agenda, conflict view | #5 |
| Test oracle | `tests/oracle.py` | Exhaustive reference solver for tiny cases | #4 |

Dependency direction: `server` depends on `schema`, `solver` and `storage`; `solver` on `options`; `options` on `calendars` and `zones`; `schema` on `zones`. `tests/oracle.py` imports nothing from the package.

## Freeze points

Parallel tickets rely on these shapes. A ticket that changes a frozen shape updates this page and every dependent ticket in the same pull request.

- **Scenario, Result and field-error shapes** (schema version 1): ticket #2 writes them down here before #3, #5 and #6 build on them.
- **Zone registry result**: UTC instants, offset and status for one local wall time (#2).
- **Result JSON** read by the browser: occurrences with UTC interval, anchor and participant labels, burden, or blocker evidence (#4; #5 may start from fixture results of the same shape).

## What is verified where

Python tests run locally and in CI on Linux and Windows, where Windows has no host time-zone data: that run proves the staged data is used. Browser checks are manual in Chrome unless a ticket states a headless run.
